from arch.common.machine import *
import arch.common.bits as bits
from arch.common.builders import get_MachineInstructionBuilder
from arch.shared_opcode_types import *
from arch.common.hacks import *
import math

from operands import *

class PIC24NewMIBase(object):
    def __init__(self, ident):
        self.__ident = ident

    length = 2

    @property
    def dests(self):
        return [self.__ident + self.length]
    pass


class PIC24Reset(object):
    operands = []
    opcode = "reset"
    length = 2
    dests = []


class PIC24Return(object):
    def __init__(self):
        self.length = 2
        self.operands = []
        self.dests = []
        self.opcode = "return"


class PIC24Retfie(object):
    def __init__(self):
        self.length = 2
        self.operands = []
        self.dests = []
        self.opcode = "retfie"


class PIC24Bra(object):
    length = 2
    opcode = "bra"

    def __init__(self, pc, dest, condition=None):
        self.dests = [
                      (dest.addr, REL_JUMP)]
        if condition:
            self.dests.append((pc + 2, REL_JUMP))

        self.operands = []

        if condition:
            self.operands += [condition]

        self.operands += [dest]



class PIC24Nop(object):
    def __init__(self, pc):
        self.dests = [(pc + 2, REL_JUMP)]
    operands = []
    opcode = "nop"
    length = 2


class PIC24Goto(object):
    opcode = "goto"

    def __init__(self, enc_length, destop):

        if isinstance(destop, OperandOffset):
            self.dests = [ (destop.addr, REL_JUMP) ]

        self.length = enc_length
        self.operands = [destop]

class PIC24Call(object):
    opcode = "call"

    def __init__(self, pc, enc_length, destop):

        if isinstance(destop, OperandOffset):
            self.dests = [ (destop.addr, REL_CALL),
                           (pc + enc_length, REL_JUMP) ]

        self.length = enc_length
        self.operands = [destop]

class PIC24RCall(PIC24Call):
    opcode = "rcall"

class PIC24CP0(object):
    opcode = "cp0"

    def __init__(self, pc, enc_length, cp):
        self.length = enc_length
        self.ident = ident

        self.dests = [(pc + self.length, REL_JUMP)]

        self.operands = [cp]


class PIC24Mov(object):
    opcode = "mov"

    def __init__(self, pc, b_flag, src, dst=None):
        self.length = 2

        self.dests = [(pc + self.length, REL_JUMP)]
        self.operands = [src]
        if dst:
            self.operands += [dst]



#############################
# Bit math instructions
class PIC24BitInst1(object):
    def __init__(self, mnem, pc, b_flag, c_z_flag, ops, opbitno):
        self.length = 2
        self.dests = [(pc + self.length, REL_JUMP)]
        self.opcode = mnem

        if b_flag:
            self.opcode += ".b"
        elif c_z_flag == "b":
            self.opcode += ".c"
        elif c_z_flag == "z":
            self.opcode += ".Z"

        assert not (b_flag and c_z_flag)

        self.operands = [ops, opbitno]

class PIC24Bset(PIC24BitInst1):
    def __init__(self, pc, b_flag, ops, opbitno):
        super(PIC24Bset, self).__init__("bset", pc, b_flag, None, ops, opbitno)

class PIC24Bclr(PIC24BitInst1):
    def __init__(self, pc, b_flag, ops, opbitno):
        super(PIC24Bclr, self).__init__("bclr", pc, b_flag, None, ops, opbitno)

class PIC24Btg(PIC24BitInst1):
    def __init__(self, pc, b_flag, ops, opbitno):
        super(PIC24Btg, self).__init__("btg", pc, b_flag, None, ops, opbitno)

class PIC24Btst(PIC24BitInst1):
    def __init__(self, pc, b_flag, c_z_flag, ops, opbitno):
        super(PIC24Btst, self).__init__("btst", pc, b_flag, c_z_flag, ops, opbitno)

class PIC24Btsts(PIC24BitInst1):
    def __init__(self, pc, b_flag, c_z_flag, ops, opbitno):
        super(PIC24Btsts, self).__init__("btsts", pc, b_flag, c_z_flag, ops, opbitno)

class PIC24Btss(PIC24BitInst1):
    def __init__(self, pc, b_flag, ops, opbitno):
        super(PIC24Btss, self).__init__("btss", pc, b_flag, None, ops, opbitno)

class PIC24Btsc(PIC24BitInst1):
    def __init__(self, pc, b_flag, ops, opbitno):
        super(PIC24Btsc, self).__init__("btsc", pc, b_flag, None, ops, opbitno)

class PIC24Bsw(PIC24BitInst1):
    def __init__(self, pc, c_z_flag, ops, opbitno):
        super(PIC24Bsw, self).__init__("bsw", pc, False, c_z_flag, ops, opbitno)



######################
class PIC24ALU(object):
    def __init__(self, pc, b_flag, src1, src2, dest):
        self.length = 2
        self.operands = [src1]

        if src2:
            self.operands += [src2]

        if dest:
            self.operands += [dest]

        self.dests = [(pc + self.length, REL_JUMP)]
        self.opcode = self.mnem

        if b_flag:
            self.opcode += ".B"

class PIC24Subr(PIC24ALU):
    mnem = "subr"

class PIC24Subbr(PIC24ALU):
    mnem = "subbr"

class PIC24Add(PIC24ALU):
    mnem = "add"

class PIC24Addc(PIC24ALU):
    mnem = "addc"

class PIC24Sub(PIC24ALU):
    mnem = "sub"

class PIC24Subb(PIC24ALU):
    mnem = "subb"

class PIC24And(PIC24ALU):
    mnem = "and"

class PIC24Xor(PIC24ALU):
    mnem = "xor"

class PIC24Ior(PIC24ALU):
    mnem = "ior"



###########
class PIC24Compare(object):
    def __init__(self, pc, b_flag, src1, src2 = None):
        self.length = 2
        self.operands = [src1]

        if src2:
            self.operands += [src2]

        self.dests = [(pc + self.length, REL_JUMP)]
        self.opcode = self.mnem

        if b_flag:
            self.opcode += ".B"

class PIC24Cp0(PIC24Compare):
    mnem = "cp0"

class PIC24Cp(PIC24Compare):
    mnem = "cp"

class PIC24Cpb(PIC24Compare):
    mnem = "cpb"


############
class PIC24SimpleALU(object):
    def __init__(self, pc, b_flag, src1, src2 = None):
        self.length = 2
        self.operands = [src1]

        if src2:
            self.operands += [src2]

        self.dests = [(pc + self.length, REL_JUMP)]
        self.opcode = self.mnem

        if b_flag:
            self.opcode += ".B"

class PIC24Inc(PIC24SimpleALU):
    mnem = "inc"

class PIC24Inc2(PIC24SimpleALU):
    mnem = "inc2"

class PIC24Dec(PIC24SimpleALU):
    mnem = "dec"

class PIC24Dec2(PIC24SimpleALU):
    mnem = "dec2"

class PIC24Neg(PIC24SimpleALU):
    mnem = "neg"

class PIC24Com(PIC24SimpleALU):
    mnem = "com"

class PIC24Clr(PIC24SimpleALU):
    mnem = "clr"

class PIC24Setm(PIC24SimpleALU):
    mnem = "setm"

# TBL RD/WR
class PIC24TblOp(object):
    def __init__(self, pc, b_flag, src, dest):
        self.length = 2
        self.operands = [src, dest]
        self.dests = [(self.length + pc, REL_JUMP)]
        self.opcode = self.mnem
        if b_flag:
            self.opcode += ".B"

class PIC24Tblrdl(PIC24TblOp):
    mnem = "tblrdl"

class PIC24Tblrdh(PIC24TblOp):
    mnem = "tblrdh"

class PIC24Tblwtl(PIC24TblOp):
    mnem = "tblwtl"

class PIC24Tblwth(PIC24TblOp):
    mnem = "tblwth"

