from arch.shared_opcode_types import *
from arch.shared_mem_types import *


# TODO: This is a hack to adapt the legacy 8051 disassembly code to the new
# modern infrastructure
class DictProxy(dict):
    def __init__(self, **args):
        if __debug__ and "length" in args and "dests" in args and "pc" in args:
            for x in args["dests"]:
                assert not (x > args["pc"] and
                        x < args["pc"] + args["length"])

        dict.__init__(self, args)
        self["typeclass"] = "code"
        self["typename"] = "8051"

        # Kill off the simulator
        try:
            del self["sim"]
        except KeyError:
            pass


def sb(x):
    if x >= 128:
        return x - 256
    return x


class ProgramMemoryIndirectAddressingOperand(Operand):
    def __init__(self, from_pc=True):
        self.from_pc = from_pc

    def render(self, ds=None, segment=None):
        return "@a + %s" % (
                {False: "dptr", True: "pc"}[self.from_pc]), TYPE_UNSPEC


class DptrOperand(Operand):
    def render(self, ds=None, segment=None):
        return "dptr", TYPE_UNSPEC


class PCOperand(Operand):
    def render(self, ds=None, segment=None):
        return "pc", TYPE_UNSPEC


class DptrIndirectAddressingOperand(Operand):
    def render(self, ds=None, segment=None):
        return "@dptr", TYPE_UNSPEC


class RegisterOperand(Operand):
    def __init__(self, Rn):
        assert Rn >= 0 and Rn <= 7
        self.Rn = Rn
        Operand.__init__(self)

    def render(self, ds=None, segment=None):
        return "R%d" % self.Rn, TYPE_UNSPEC


class RegisterIndirectAddressingOperand(Operand):
    def __init__(self, Rn):
        assert Rn in [0, 1]
        self.Rn = Rn

    def render(self, ds=None, segment=None):
        return "@R%d" % self.Rn, TYPE_UNSPEC


class DirectAddressingOperand(Operand):
    def __init__(self, direct):
        assert direct < 256 and direct >= 0
        self.direct = direct

    def render(self, ds=None, segment=None):
        return "(%#02x)" % self.direct, TYPE_SYMBOLIC


class ImmediateOperand8(Operand):
    def __init__(self, constant):
        assert constant >= 0 and constant < 256
        self.constant = constant

    def render(self, ds=None, segment=None):
        return "#0x%02x" % self.constant, TYPE_UNSPEC


class ImmediateOperand16(Operand):
    def __init__(self, constant):
        assert constant >= 0 and constant < 65536
        self.constant = constant

    def render(self, ds=None, segment=None):
        return "#0x%04x" % self.constant, TYPE_UNSPEC


class BitOperand(Operand):
    def __init__(self, bit_and_addr, inv=False):
        bit = bit_and_addr & 0x7
        byte = bit_and_addr & 0xF8
        if (byte < 0x80):
            addr = 0x20 + byte / 8
        else:
            addr = byte

        self.addr = addr
        self.bit = bit
        self.invflag = inv

    def render(self, ds=None, segment=None):
        return "%s(%#02x.%d)" % ("/" if self.invflag else "",
                self.addr, self.bit), TYPE_UNSPEC


class AccumulatorOperand(Operand):
    def render(self, ds=None, segment=None):
        return "a", TYPE_UNSPEC


class ABOperand(Operand):
    def render(self, ds=None, segment=None):
        return "ab", TYPE_UNSPEC


class CarryFlagOperand(Operand):
    def render(self, ds=None, segment=None):
        return "c", TYPE_UNSPEC


# TODO: This should be a shared operand type -
# subclass the numeric class and change the defaults such that
# it defaults to symbolic?
class PCJmpDestination(Operand):
    def __init__(self, calculated_addr):
        self.addr = calculated_addr

    def render(self, ds=None, segment=None):
        typecode = TYPE_UNSPEC
        if ds:
            try:
                ident = segment.mapOut(self.addr)
            except ValueError:
                typecode = TYPE_DEST_INVALID
            else:
                rc, obj = ds.infostore.lookup(ident)

                if rc != ds.infostore.LKUP_OK:
                    typecode = TYPE_DEST_INVALID

                elif obj.label:
                    return obj.label, TYPE_SYMBOLIC

        return "%#04x" % self.addr, typecode


a_R = RegisterOperand
a_RI = RegisterIndirectAddressingOperand
a_D = DirectAddressingOperand
a_A = AccumulatorOperand
a_AB = ABOperand
a_C = CarryFlagOperand
a_B = BitOperand
a_DPTR = DptrOperand
#a_PC = PCOperand
a_DPTRI = DptrIndirectAddressingOperand
a_I8 = ImmediateOperand8
a_I16 = ImmediateOperand16
a_PMAI = ProgramMemoryIndirectAddressingOperand

a_PC = PCJmpDestination
