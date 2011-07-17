import applogic.type_base
from arch.shared_opcode_types import StringOperand


class StringType(object):

    def __init__(self, length, val, mnemonic=".ascii"):

        self.__length = length
        self.__value = val

        self.operands = [StringOperand(val)]
        self.mnemonic = mnemonic

    def __repr__(self):
        return "ASCII %s" % self.val

    def length(self):
        return self.__length

    def dests(self):
        return []


class AsciiStringTypeDecoder(applogic.type_base.DecodeTypeBase):
    shortname = "ascii"
    typeclass = "data"
    max_length = -1     # No maximum length

    def __init__(self, datastore):
        self.datastore = datastore

    @staticmethod
    def __isasciistr(c):
        return 0x20 <= c <= 0x7e or c in [0xA, 0xD]

    def disassemble(self, ident, saved_params=None):
        char_ar = ''

        ident_ind = ident
        while 1:
            c_ar = self.datastore.readBytes(ident_ind)
            ident_ind += 1

            # If we run off the end of fetchable memory
            if not c_ar:
                break

            c = c_ar[0]
            if not AsciiStringTypeDecoder.__isasciistr(c):
                break

            char_ar += chr(c)

        return StringType(len(char_ar), char_ar)
