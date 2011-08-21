from arch.common.machine import *
import arch.common.bits as bits
from arch.common.builders import get_MachineInstructionBuilder
from arch.shared_opcode_types import *
from arch.common.hacks import *
import math
from operands import *
from formats import *
from instructions import *


def w_mode(w, m):
    if m == 0:
        return OpW(w)

    return OpWInd(w, m)


# NOTE: This processor module expects to be working on a
#       code segment with 16 bit words, as is described
#       in the microchip ISA. the "high" 16 bit word
#       [odd address], has the top 8 bits forced to 0
#       These are unimpl in HW, as HW stores 24 bits
#       all on even addresses. Odd addresses are used for
#       byte addressing


class PIC24Machine(object):
    shortname = "pic24"
    longname = "PIC24/dsPIC3x"
    typeclass = "code"
    max_length = 4

    def __init__(self):
        self.core_is_dspic = False
        self.core_is_E = False

    def decode0(self, pc, src):
        w0 = src(0)
        op4 = (w0 >> 15) & 0x1E
        op5 = (w0 >> 15) & 0x1F

        if op4 == 0x0:
            return PIC24Nop(pc)

        elif op4 == 2:
            raise NotImplementedError("Indirect Call / Goto")

        elif op4 in (4,8):
            w1 = src(1)
            s = Fmt4(w0, w1)

            if op4 == 0x04:
                return PIC24Call(pc, 4, s.N)
            return PIC24Goto(4, s.N)

        elif op5 == 0xA:
            raise NotImplementedError("fmt5 retlw")

        elif op5 == 0xC:
            if w0 == 0x060000:
                return PIC24Return()
            elif w0 == 0x64000:
                return PIC24Retfie()

        elif op4 == 0x0E:
            s = Fmt7(pc, w0)

            return PIC24RCall(pc, 2, s.N)
        elif op5 == 0x12:
            raise NotImplementedError("RepeatK")
        elif op5 == 0x13:
            raise NotImplementedError("repeat")


    def decode_A(self, pc, w0):
        opc4 = BITS(w0, 16, 4)

        if opc4 in (5, 13):
            s = Fmt1(w0)
            if opc4 == 13:
                return PIC24Bsw(pc, s.Z, s.S, s.W)
            elif opc5 == 5:
                return PIC24Btst(pc, False, s.Z, s.S, s.W)
        elif opc4 <= 0x7:
            s = Fmt12(w0)
            if opc4 == 0:
                return PIC24Bset(pc, s.B, s.S, s.b)
            elif opc4 == 1:
                return PIC24Bclr(pc, s.B, s.S, s.b)
            elif opc4 == 2:
                return PIC24Btg(pc, s.B, s.S, s.b)
            elif opc4 == 3:
                return PIC24Btst(pc, False, s.Z, s.S, s.b)
            elif opc4 == 4:
                return PIC24Btsts(pc, False, s.Z, s.S, s.b)
            elif opc4 == 6:
                return PIC24Btss(pc, False, s.S, s.b)
            elif opc4 == 7:
                return PIC24Btsc(pc, False, s.S, s.b)
        else:
            s = Fmt13(w0)

            if opc4 == 8:
                return PIC24Bset(pc, s.B, s.F, s.b)
            elif opc4 == 9:
                return PIC24Bclr(pc, s.B, s.F, s.b)
            elif opc4 == 0xA:
                return PIC24Btg(pc, s.B, s.F, s.b)
            elif opc4 == 0xB:
                return PIC24Btst(pc, s.B, None, s.F, s.b)
            elif opc4 == 0xC:
                return PIC24Btsts(pc, s.B, None, s.F, s.b)
            elif opc4 == 0xE:
                return PIC24Btss(pc, s.B, s.F, s.b)
            elif opc4 == 0xF:
                return PIC24Btsc(pc, s.B, s.F, s.b)

    def decodeALU(self, pc, w0):
        op5 = (w0 >> 19) & 0x1F

        if op5 == 0xF:
            s = Fmt25(w0)
            return PIC24Mov(pc, PIC24Mov.b2s(s.B),
                    s.S, s.D)

        else:
            aluOP = { 2:  PIC24Subr,
                      3:  PIC24Subbr,
                      8:  PIC24Add,
                      9:  PIC24Addc,
                      10: PIC24Sub,
                      11: PIC24Subb,
                      12: PIC24And,
                      13: PIC24Xor,
                      14: PIC24Ior
                    }[op5]

            s = Fmt8(w0)
            return aluOP(pc, s.B, s.W, s.src, s.D)

    def decodeBRA(self, pc, w0):
            s = Fmt7(pc, w0)

            cf = BITS(w0, 16, 4)

            cf_t = {
                    0: 'OV',
                    1: 'C',
                    2: 'Z',
                    3: 'N',
                    4: 'LE',
                    5: 'LT',
                    6: 'LEU',
                    7: None,
                    8: 'NOV',
                    9: 'NC',
                    10: 'NZ',
                    11: 'NN',
                    12: 'GT',
                    13: 'GE',
                    14: 'GTU'}[cf]

            cond = None
            if cf_t:
                cond = OpSBIT(cf_t)

            return PIC24Bra(pc, s.N, condition=cond)

    def decode_E(self, pc, w0):
        op2 = BITS(w0, 15, 5)

        # Decode cp0, cp and cpb in all 3 forms
        if op2 in (0,2,3,4,6,7):
            if op2 < 4:
                s = Fmt17(w0, self.core_is_E)
                base = s.W
                src = s.S
                b = s.B
            else:
                s = Fmt3(w0)
                src = None
                base = s.F
                b = s.B

            op2_f = op2 & 0x3

            # cp0 has only one operand in both cases
            if op2_f == 0:
                if not src:
                    src = base
                return PIC24Cp0(pc, b, src)
            elif op2_f == 2:
                return PIC24Cp(pc, b, base, src)
            elif op2_f == 3:
                return PIC24Cpb(pc, b, base, src)

        # INC/DEC/NEG/CLR/COM/SETM
        elif op2 & 0x10:
            if not op2 & 0x8:
                s = Fmt2(w0)
                src = s.S
                dest = s.D # s.D is the dest reg
            else:
                s = Fmt3(w0)
                src = s.F
                dest = None
                if not s.D: # s.D is the dest bit
                    dest = OpW(0)

            o = op2 & 0x7
            if o < 6:
                asm = {
                        0: PIC24Inc,
                        1: PIC24Inc2,
                        2: PIC24Dec,
                        3: PIC24Dec2,
                        4: PIC24Neg,
                        5: PIC24Com
                        } [o]
                return asm(pc, s.B, src, dest)

            elif o == 6:
                if not dest:
                    dest = src
                return PIC24Clr(pc, s.B, dest)
            elif o == 7:
                if not dest:
                    dest = src
                return PIC24Setm(pc, s.B, dest)
        else:
            raise NotImplementedError("skip / branch + cmp")

    def decode_B(self, pc, w0):
        alu_op = {
              0:  PIC24Add,
              1:  PIC24Addc,
              2: PIC24Sub,
              3: PIC24Subb,
              4: PIC24And,
              5: PIC24Xor,
              6: PIC24Ior
              }


        soc = BITS(w0, 15, 5)

        # 3 MOV.B.s
        if soc in (0xF, 0x1F, 0x7):
            if soc == 0x7:
                s = Fmt5(w0)
                if s.K.value > 0xFF:
                    return
                return PIC24Mov(pc, PIC24Mov.b2s(s.B),
                        s.K, s.D)

            elif soc == 0xF:
                s = Fmt3(w0)
                return PIC24Mov(pc, PIC24Mov.b2s(s.B),
                        OpW(0), s.F)

            elif soc == 0x1F:
                s = Fmt3(w0)

                if not s.D:
                    return PIC24Mov(pc, PIC24Mov.b2s(s.B),
                            s.F, OpW(0))
                return PIC24Mov(pc, PIC24Mov.b2s(s.B),
                        s.F)


        # B {0-F} ALU ops
        elif not soc & 0x10:
            if not soc & 0x8:
                s = Fmt5(w0)
                src = s.K
                dest = s.D

            else:
                s = Fmt3(w0)
                src = s.F
                dest = None
                if not s.D:
                    dest = OpW(0)

            return alu_op[soc & 0x7](pc, s.B, src, None, dest)

        elif soc in (0x14, 0x15, 0x16, 0x17):
            s = Fmt8(w0)
            op = {
                    0x14: PIC24Tblrdl,
                    0x15: PIC24Tblrdh,
                    0x16: PIC24Tblwtl,
                    0x17: PIC24Tblwth
                    }[soc]

            return op(pc, s.B, s.src, s.D)

        elif soc in (0x1C, 0x1D):
            s = Fmt1(w0)
            if w0 & 0xF800 == 0:
                return PIC24Mov(pc, 4, s.S, s.D)
            elif w0 & 0xFFF1 == 0x9F80:
                return PIC24Push(pc, 4, s.S)

        else:
            raise NotImplementedError("ext 0xB")

    def decode_D(self, pc, w0):
        a_op = {
              0: PIC24Sl,
              2: PIC24Lsr,
              3: PIC24Asr,
              4: PIC24Rlnc,
              5: PIC24Rlc,
              6: PIC24Rrnc,
              7: PIC24Rrc
              }


        soc = BITS(w0, 15, 5)

        if not soc & 0x10:
            op = soc & 7
            if op == 1:
                return

            opc = a_op[op]

            if soc & 0x8:
                s = Fmt3(w0)
                src = s.F
                dest = None
                if not s.D:
                    dest = OpW(0)
            else:
                s = Fmt2(w0)
                src = s.S
                dest = s.D

            return opc(pc, s.B, src, dest)

        elif soc in (0x1A, 0x1C, 0x1D):
            s = Fmt15(w0)

            if soc == 0x1A:
                opc = PIC24Sl
            elif soc == 0x1C:
                opc = PIC24Lsr
            elif soc == 0x1D:
                opc = PIC24Asr

            return opc(pc, False, s.W, s.D, s.src)

        raise NotImplementedError("0xB FBCL and DIV")

    def disasm_helper(self, pc, source):
        w1 = None
        def getWord(offs):
            w_l, w_h = source[offs * 2: offs * 2 + 2]

            # create a complete 24 bit instruction word
            w = w_h << 16 | w_l
            return w

        w0 = getWord(0)
        opc = (w0 & 0xF00000) >> 20
        opc2 = (w0 & 0x0F0000) >> 16

        # 0 - Control flow opcodes
        if opc == 0x0:
            return self.decode0(pc, getWord)

        # ALU ops
        elif opc in (1, 4, 5, 6, 7):
            return self.decodeALU(pc, w0)

        # Mov #lit16, wND
        elif opc == 0x2:
            s = Fmt9(w0)
            return PIC24Mov(pc, 2, s.K, s.D)

        elif opc == 0x3:
            return self.decodeBRA(pc, w0)

        # Mov f, w / w, f
        elif opc == 0x8:
            s = Fmt10(w0)
            ops = [s.F, s.R]

            # if bit3 set, MOV W, F
            if BIT(w0, 19):
                ops = ops[::-1]

            return PIC24Mov(pc, 2, *ops)

        elif opc == 0x9:
            s = Fmt11(w0)
            return PIC24Mov(pc, PIC24Mov.b2s(s.B),
                    s.src, s.dst)

        elif opc == 0xA:
            return self.decode_A(pc, w0)

        elif opc == 0xB:
            return self.decode_B(pc, w0)

        elif opc == 0xC:
            raise NotImplementedError("DSP Ops")

        elif opc == 0xD:
            return self.decode_D(pc, w0)

        elif opc == 0xE:
            return self.decode_E(pc, w0)

        elif w0 == 0xFE0000:
            return PIC24Reset()

        else:
            raise NotImplementedError("all others")

    def disassemble(self, pc, source):
        o = self.disasm_helper(pc, source)
        return o

# The following adaptors adapt the new-style PIC24 disassembler
# to the old-style arch codebase. They will be removed upon merge
# of the arch fixes
def PIC24OperandAdaptor(x):
    return x

class PIC24MachineInstructionAdaptor(MachineInstruction):
    def __init__(self, ds, ident, impl):
        self.__ds = ds
        self.__ident = ident
        self.__impl = impl
        self.__myseg = \
                self.__ds.segments.findSegment(self.__ident)

    def __repr__(self):
        return self.__impl.text()

    def length(self):
        return self.__impl.length

    def __map(self, (i, j)):
        return (self.__myseg.mapOut(i), j)

    def dests(self):
        __olddests = list(self.__impl.dests)
        dests = filter(lambda x: x != None,
                map(self.__map, __olddests))
        return dests

    @property
    def operands(self):
        return self.__impl.operands

class PIC24MachineAdaptor(object):
    shortname = "pic24"
    longname = "PIC24/dsPIC3x"
    typeclass = "code"
    max_length = 4

    def __init__(self, datastore):
        self.__d = datastore
        self.__i = PIC24Machine()


    def disassemble(self, ident, saved_params):
        class access(object):
            def __init__(self, d, offs):
                self.d = d
                self.offs = offs

            def __getslice__(self, a, b):
                return self.d.readBytes(a + self.offs, b-a)

        pc = self.__d.segments.findSegment(ident).mapIn(ident)
        _o = self.__i.disassemble(pc, access(self.__d, ident))

        if _o:
            return MIB(_o.opcode, None)(
                self.__d, ident, _o)
        return None



MIB = get_MachineInstructionBuilder('arch.pic24.machine',
        PIC24MachineInstructionAdaptor)

machines = [PIC24MachineAdaptor]
