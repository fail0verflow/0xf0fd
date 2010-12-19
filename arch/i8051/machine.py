from arch.common.machine import *
import arch.common.bits as bits
from arch.common.builders import get_MachineInstructionBuilder

import opcode_8051


class i8051MachineInstruction(MachineInstruction):
    def __init__(self, length, dests, *args):
        self.operands = args
        self.__length = length
        self.__dests = dests

    def __repr__(self):
        res = self.mnemonic + " "
        for op in self.operands:
            res += op.render(None)
        return res

    def length(self):
        return self.__length

    def dests(self):
        return self.__dests

MIB = get_MachineInstructionBuilder('arch.mips.machine',i8051MachineInstruction)

def i8051Adaptor(id, bytes):
    rv = opcode_8051.decode_bytes(id, bytes)

    if not rv:
        return None

    disasm = rv["disasm"]
    length = rv["length"]
    dests = rv["dests"]

    return MIB(disasm.opcode, None)(
        length,dests, *disasm.operands)


class i8051Machine(object):
    shortname = "8051"
    longname = "8051"
    typeclass = "code"
    max_length = 4

    def __init__(self, datastore):
        self.datastore = datastore
        
    def disassemble(self, id, saved_params=None):
        bytes = self.datastore.readBytes(id, 5)
        return i8051Adaptor(id, bytes)

machines = [i8051Machine]   

