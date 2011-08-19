from cPickle import dumps, loads
from dbtypes import MemoryInfo
from fsignal_thunk import *


class InfoStore(object):
    INF_CHG_ALTER = 1
    INF_CHG_DEL = 2

    def __init__(self, parent):
        self.__parent = parent

        self.conn = parent.conn
        self.c = self.conn.cursor()
        self.__createTables()

        self.__memory_info_cache = {}
        self.__memory_info_insert_queue = {}

        self.__memory_info_insert_queue = []
        self.__memory_info_insert_queue_ignore = set()

        self.decoder_lookup = parent.decoder_lookup

        self.updates = 0
        self.inserts = 0
        self.deletes = 0
        self.commits = 0
        self.meminfo_misses = 0
        self.meminfo_fetches = 0
        self.meminfo_failures = 0

        self.infoChanged = FSignal()

    def __createTables(self):
        # Attrs/obj is a dumped representation of a dict
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS memory_info
                (addr       INTEGER CONSTRAINT addr_pk PRIMARY KEY,
                 length     INTEGER,
                 typeclass  VARCHAR(100),
                 typename   VARCHAR(100),
                 obj        BLOB )''')

    def __len__(self):
        return self.c.execute('''SELECT count(addr)
                                 FROM memory_info''').fetchone()[0]

    def __iter__(self):
        self.flushInsertQueue()

        addrs = self.c.execute('''SELECT addr
                    FROM memory_info''').fetchall()
        addrs = [i[0] for i in addrs]

        class DataStoreIterator:
            def __init__(self, src, addrs):
                self.src = src
                self.addrs = addrs

            def next(self):
                if not self.addrs:
                    raise StopIteration

                v = self.src[self.addrs[0]]
                self.addrs = self.addrs[1:]
                return v

        return DataStoreIterator(self, addrs)

    def __contains__(self, ident):
        status, result = self.lookup(ident)
        return status == self.LKUP_OK

    # find the instruction that includes this address
    def findStartForAddress(self, seekaddr):
        stat, obj = self.lookup(seekaddr)

        if stat == self.LKUP_OK:
            return seekaddr

        elif stat == self.LKUP_NONE:
            return None

        elif stat == self.LKUP_OVR:
            return obj.addr

    LKUP_OK = 0     # Found item @ ident
    LKUP_NONE = 1   # No item found @ ident
    LKUP_OVR = 2    # passed ident overlapped another

    def __getitem__(self, ident):
        status, value = self.lookup(ident)
        if status == self.LKUP_OK:
            return value

        raise KeyError

    def lookup(self, addr):
        self.meminfo_fetches += 1
        # See if the object is already around
        try:
            obj = self.__memory_info_cache[addr]

            # We should never have a "none" result in the cache
            assert (obj != None)
            return self.LKUP_OK, obj

        except KeyError:
            self.flushInsertQueue()

            # No item already cached, fetch from DB
            row = self.c.execute('''SELECT addr,
                    length, typeclass, typename, obj
                    FROM memory_info
                    WHERE addr <= ? ORDER BY addr DESC LIMIT 1''',
                  (addr,)).fetchone()

            if not row:
                return self.LKUP_NONE, None

            resultcode = self.LKUP_OK

            # If the row doesn't equal the address, then
            # either we found a memory object that finishes
            # before this address, or one that overlaps this address
            if row[0] != addr:
                if row[0] + row[1] > addr:
                    # See whether we already know the object we're in
                    try:
                        obj = self.__memory_info_cache[row[0]]
                        return self.LKUP_OVR, obj
                    except KeyError:
                        pass
                    resultcode = self.LKUP_OVR
                else:
                    return self.LKUP_NONE, None

            self.meminfo_misses += 1

            try:
                params = loads(str(row[4]))
            except ImportError:
                print "Warning, discarding params for %x" % row[0]
                params = {
                        "saved_params": None
                    }

            obj = MemoryInfo.createFromParams(
                self.__parent, row[0], row[1],
                str(row[3]), str(row[2]), params)

            if not obj:
                print "Warning - Potentially missing datatype:", row[3]
                return self.LKUP_NONE, None

            obj.ds_link = self.__changed

            if resultcode == self.LKUP_OK:
                assert obj.addr == addr

            elif resultcode == self.LKUP_OVR:
                assert obj.addr <= addr and obj.addr + obj.length > addr

            self.__memory_info_cache[obj.addr] = obj

            return resultcode, obj

    def setType(self, ident, typeName):
        # ensure that we're not creating an MI
        # within another
        rc, _ = self.lookup(ident)
        assert rc in [self.LKUP_NONE, self.LKUP_OK]

        v = MemoryInfo.createForTypeName(self.__parent, ident, typeName)

        v.ds_link = self.__changed
        assert v.addr == ident

        try:
            # Evict the current entry from the cache
            del self.__memory_info_cache[ident]
        except KeyError:
            pass

        if ident in self.__memory_info_insert_queue_ignore:
            self.flushInsertQueue()

        self.__memory_info_cache[ident] = v

        assert not v.typeclass == "default"

        self.__queue_insert(ident, v)

        self.infoChanged.emit(ident, self.INF_CHG_ALTER)
        return v

    def __queue_insert(self, ident, v):
        # Not in cache, so save new obj in cache
        self.__memory_info_insert_queue.append(ident)

    def __delitem__(self, ident):
        self.remove(ident)

    def remove(self, ident):
        try:
            # KeyError can be tripped here too
            is_default = self.__memory_info_cache[ident].typeclass == "default"
            assert not is_default

            del self.__memory_info_cache[ident]
        except KeyError:
            pass

        self.deletes += 1
        #print "DELETE: %d" % self.deletes

        self.__memory_info_insert_queue_ignore.update([ident])
        self.c.execute('''DELETE FROM memory_info WHERE addr=?''',
              (ident,))

        self.infoChanged.emit(ident, self.INF_CHG_DEL)

    def __changed(self, ident, value):
        self.updates += 1
        self.flushInsertQueue()

        self.c.execute(
            '''UPDATE memory_info SET length=?,
                typeclass=?, typename=?, obj=? WHERE ident=?''',
              (value.length, value.typeclass,
              value.typename, dumps(value.persist_attribs), ident))

        self.infoChanged.emit(ident, self.INF_CHG_ALTER)

    def flushInsertQueue(self):
        params = []
        for ident in self.__memory_info_insert_queue:
            if ident in self.__memory_info_insert_queue_ignore:
                continue
            obj = self.__memory_info_cache[ident]
            param_l = (obj.addr, obj.length, obj.typeclass,
                obj.typename, dumps(obj.persist_attribs))
            params.append(param_l)

        self.__memory_info_insert_queue_ignore = set()
        self.__memory_info_insert_queue = []

        self.inserts += len(params)

        self.conn.executemany('''INSERT OR REPLACE INTO memory_info
            (addr, length, typeclass, typename, obj) VALUES
            (?,?,?,?,?)''',
            params
            )

    def flush(self):
        self.flushInsertQueue()
        self.commits += 1
        self.conn.commit()

    def __del__(self):
        self.flush()
