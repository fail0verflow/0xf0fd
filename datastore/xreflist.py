from collections import defaultdict


class Xref(object):
    def __init__(self, ident_from, ident_to, xref_type):
        self.ident_from = ident_from
        self.ident_to = ident_to
        self.xref_type = xref_type


class XrefList(object):
    XREF_CODE = 1  # Dest should be treated as code
    XREF_DATA = 2  # Dest should be treated as data

    def __init__(self, parent):
        self.__parent = parent

        #self.conn = parent.conn
        #self.__c = self.conn.cursor()

        self.clearXrefs()

    def clearXrefs(self):
        self.__xrefs_from = defaultdict(list)
        self.__xrefs_to = defaultdict(list)

    def addXref(self, ident_from, ident_to, xref_type):
        o = Xref(ident_from, ident_to, xref_type)
        self.__xrefs_from[ident_from].append(o)
        self.__xrefs_to[ident_to].append(o)

    def getXrefsTo(self, ident_to):
        return self.__xrefs_to[ident_to]

    def getXrefsFrom(self, ident_from):
        return self.__xrefs_from[ident_from]
