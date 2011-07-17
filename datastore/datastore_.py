import sqlite3

from properties import *
from commentlist import *
from symbollist import *
from segmentlist import *
from fsignal_thunk import *
from infostore import InfoStore
from xreflist import XrefList

from applogic.command_list import CommandList
from dbtypes import *


class DataStore(object):
    def __init__(self, filename_db, decoder_lookup=None):

        # Invoked whenever a decoder needs to be created
        if decoder_lookup:
            self.decoder_lookup = decoder_lookup
        else:
            self.decoder_lookup = self.fakeDecoderLookup

        # Allow supplying a SQLITE db for testing
        if type(filename_db) == str:
            self.conn = sqlite3.connect(filename_db)
        else:
            self.conn = filename_db

        self.c = self.conn.cursor()
        self.__createTables()

        self.symbols = SymbolList(self.conn, "symbols")
        self.comments = CommentList(self.conn, "comments")
        self.cmdlist = CommandList(self)
        self.segments = SegmentList(self.conn, self)
        self.infostore = InfoStore(self)
        self.xreflist = XrefList(self)

        self.properties = Properties(self.conn)

        self.layoutChanged = FSignal()

        # TODO - bump this every time we break
        # the DB [may need exponential notation]
        self.__my_db_version = 2
        try:
            self.db_version = self.properties.get("f0fd.db_version")
        except:
            # New DB - set the database verison
            self.properties.set("f0fd.db_version", self.__my_db_version)
            self.db_version = self.__my_db_version

        if self.db_version != self.__my_db_version:
            raise IOError("Could not load database, different DB version")

    def fakeDecoderLookup(self, ds, typename):
        raise NotImplementedError("No decoder lookup function was provided")

    # TODO - Remove/fixup me
    def readBytes(self, ident, length=1):
        # FIXME, use findsegment method on SegmentList
        for i in self.segments.segments_cache:
            # try to map the ident to an internal address for the read
            try:
                mapped_addr = i.mapIn(ident)
            except ValueError:
                continue

            try:
                return i.readBytes(mapped_addr, length)
            except IOError:
                pass

        raise IOError("no segment could handle the requested read")

    def __createTables(self):
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS symbols
                (addr INTEGER CONSTRAINT base_addr_pk PRIMARY KEY,
                name VARCHAR(100),
                type INTEGER,
                attrs BLOB
                )''')

        self.c.execute('''
            CREATE TABLE IF NOT EXISTS comments
                (addr INTEGER,
                text VARCHAR(100),
                position INTEGER,
                CONSTRAINT pk PRIMARY KEY (addr, position)
                )''')

        self.c.execute('''
            CREATE TABLE IF NOT EXISTS properties
                (prop_key VARCHAR(100),
                value BLOB,
                CONSTRAINT pk PRIMARY KEY (prop_key))
                ''')

    def flush(self):
        self.infostore.flush()
        self.conn.commit()
