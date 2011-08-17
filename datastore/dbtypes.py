import traceback


class CommentPosition:
    POSITION_BEFORE = 0
    POSITION_RIGHT = 1
    POSITION_BOTTOM = 2


class proxy_dict(dict):
    def __getstate__(self):
        return dict([i for i in self.__dict__.items() if i[0] != 'parent'])

    def __init__(self, parent, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.parent = parent

    def __setitem__(self, k, v):
        if self.parent:
            self.parent()
        return dict.__setitem__(self, k, v)

    def __delitem__(self, v):
        if self.parent:
            self.parent()
        return dict.__delitem__(self, v)


# Information about a memory location
class MemoryInfo(object):
    @staticmethod
    def createForTypeName(ds, addr, typename):
        """ Create an MemoryInfo object, given only the desired typename"""
        decoder = ds.decoder_lookup(ds, typename)

        if not decoder:
            return None

        decoded = decoder.disassemble(addr, saved_params=None)
        m = MemoryInfo(
                ds=ds,
                addr=addr,
                length=decoded.length(),
                typeclass=decoder.typeclass,
                typename=decoder.shortname,
                disasm=decoded,
                persist_attribs=None)

        return m

    @staticmethod
    def createFromParams(ds, addr, length, typename,
        typeclass, persist_attribs):
        try:
            saved_params = persist_attribs["saved_params"]
        except KeyError:
            saved_params = {}

        decoder = ds.decoder_lookup(ds, typename)

        if not decoder:
            return None

        try:
            decoded = decoder.disassemble(addr, saved_params=saved_params)
        except Exception:
            decoded = None
            traceback.print_exc()

        if not decoded:
            err_decoder = ds.decoder_lookup(ds, "error")
            if not err_decoder:
                raise NotImplementedError("""The 'error' datatype must be
                implented'""")
            decoded = err_decoder.disassemble(addr, length=length)

            assert decoded

        assert decoded.length() == length

        m = MemoryInfo(
                ds=ds,
                addr=addr,
                length=decoded.length(),
                typeclass=decoder.typeclass,
                typename=decoder.shortname,
                disasm=decoded,
                persist_attribs=persist_attribs)

        return m

    # Disable serialization
    def __getstate__(self):
        raise NotImplementedError()

    # Disable serialization
    def __setstate__(self, d):
        raise NotImplementedError()

    # Addr is read-only, since its a primary key.
    # Delete and recreate to change
    def __get_addr(self):
        return self.__addr
    addr = property(__get_addr)

    # Read-only view of length
    def __get_length(self):
        return self.__length
    length = property(__get_length)

    # Text form of the decoding [TODO: rename?]
    def __get_disasm(self):
        return self.__disasm
    disasm = property(__get_disasm)

    # General type of the data
    # Currently two valid values ["code", "data"]
    @staticmethod
    def __validate_typeclass(value):
        return value in ["code", "data"]

    def __get_typeclass(self):
        return self.__typeclass
    typeclass = property(__get_typeclass)

    # Actual type of the data
    def __get_typename(self):
        return self.__typename
    typename = property(__get_typename)

    # Handy accessor method - just calls into datastore
    def __getlabel(self):
        return self.ds.symbols.getSymbol(self.addr)
    label = property(__getlabel)

    # Handy comment accessor method - just calls into datastore
    def __getcomment(self):
        comment = self.ds.comments.getComments(self.addr,
            position=CommentPosition.POSITION_RIGHT)

        if not comment:
            return ""

        return comment[0]
    comment = property(__getcomment)

    def __get_cdict(self):
        return self.__cdict
    cdict = property(__get_cdict)

    def __init__(self, addr, length, typeclass,
        typename, disasm, ds, persist_attribs):

        self.ds = ds
        # legacy
        self.ds_link = None

        # Create the custom properties dictionary
        self.__cdict = dict()

        if not persist_attribs:
            self.persist_attribs = proxy_dict(self.push_changes)
        else:
            self.persist_attribs = persist_attribs

        self.__addr = addr
        self.__length = length
        self.__disasm = disasm

        assert MemoryInfo.__validate_typeclass(typeclass)
        self.__typeclass = typeclass

        self.__typename = typename

        # Should go away too
        self.xrefs = []

    def push_changes(self):
        if (self.ds_link):
            self.ds_link(self.addr, self)
