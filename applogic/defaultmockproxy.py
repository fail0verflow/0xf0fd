from datastore.infostore import InfoStore


# Temporary mock operand until the type system gets sorted out
class DefaultMock(object):
    """ Mock object created when there
    is nothing in the DB about a given address """

    class OperandMock(object):
        def __init__(self, value):
            self.value = value

        def render(self, ds, segment):
            if self.value != None:
                return "0x%02x" % self.value, 0
            return "?", 0

    class DisasmMock(object):
        def __init__(self, value):
            self.mnemonic = ".db"
            self.operands = [DefaultMock.OperandMock(value)]

    def __getLabelFromDS(self):
        return self.ds.symbols.getSymbol(self.addr)
    label = property(__getLabelFromDS)

    def __init__(self, ds, addr):
        self.ds = ds

        # If segment doesn't have defined data,
        # readbytes returns None
        v = ds.readBytes(addr, 1)
        if v:
            self.value = v[0]
        else:
            self.value = None

        self.disasm = DefaultMock.DisasmMock(self.value)
        self.typename = "default"
        self.typeclass = "default"
        self.addr = addr
        self.cdict = {}
        self.length = 1
        self.comment = ""


class DefaultMockProxy(object):
    def __init__(self, ds):
        self.__subject = ds
        self.infostore = InfoStoreMockProxy(ds.infostore, self)

    def __getattr__(self, name):
        return getattr(self.__subject, name)


class InfoStoreMockProxy(object):
    """Proxy that returns "mock" objects for any memory location that is
        valid but does not have a real repr in the datastore"""

    def __init__(self, infostore, parent):
        self.__subject = infostore
        self.__parent = parent

    def __iter__(self):
        raise TypeError("'InfoStoreMockProxy' object is not iterable")

    # Deprecated interface, use lookup
    def __contains__(self, ident):
        status, value = self.lookup(ident)
        return status == InfoStore.LKUP_OK

    # Deprecated interface, use lookup
    def __getitem__(self, ident):
        status, value = self.lookup(ident)
        if status == InfoStore.LKUP_OK:
            return value

        raise KeyError

    def __createDefault(self, ident):
        # Only return a defaults object if we're within a valid memory range
        try:
            self.__parent.readBytes(ident, 1)
            mi = DefaultMock(self.__parent, ident)
            return mi
        except IOError:
            return None

    # find the instruction that includes this address
    def findStartForAddress(self, seekaddr):
        stat, obj = self.lookup(seekaddr)

        if stat == self.LKUP_OK:
            return seekaddr

        elif stat == self.LKUP_NONE:
            return None

        elif stat == self.LKUP_OVR:
            return obj.addr

    def lookup(self, ident):
        real_lookup_status, real_result = self.__subject.lookup(ident)

        if real_lookup_status in [InfoStore.LKUP_OK, InfoStore.LKUP_OVR]:
            return real_lookup_status, real_result

        default_result = self.__createDefault(ident)

        if default_result:
            return InfoStore.LKUP_OK, default_result

        return InfoStore.LKUP_NONE, None

    def __getattr__(self, name):
        return getattr(self.__subject, name)
