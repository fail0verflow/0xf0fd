import applogic.type_base
from arch.shared_opcode_types import StringOperand


class ErrorType(object):
    mnemonic = "ERROR"

    def __init__(self, length):
        self.__length = length
        self.operands = [StringOperand("ERROR")]

    def __repr__(self):
        return "ASCII %s" % self.val

    def length(self):
        return self.__length

    def dests(self):
        return []


class ErrorTypeDecoder(applogic.type_base.DecodeTypeBase):
    shortname = "error"
    typeclass = "data"
    max_length = -1     # No maximum length

    def __init__(self, datastore):
        self.datastore = datastore

    def disassemble(self, ident, saved_params=None, length=0):

        return ErrorType(length)
