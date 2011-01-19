from arch.common.machine import *
import arch.common.bits as bits
from arch.common.builders import get_MachineInstructionBuilder

from arch.common.hacks import *

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

MIB = get_MachineInstructionBuilder('arch.i8051.machine',i8051MachineInstruction)

def i8051Adaptor(id, bytes):
    rv = opcode_8051.decode_bytes(id, bytes)

    if not rv:
        return None

    disasm = rv["disasm"]
    length = rv["length"]

    # NOTE - both of these should be derived from the IR
    # They are done processor specific simply to allow development
    # of the gui while the IR is still early.
    # Yes, this is a HACK

    dests_jmp = rv["dests"]
    try:
        dests_call = rv["dests_call"]
    except KeyError:
        dests_call = []

    dests = [(i, REL_JUMP) for i in dests_jmp] + [(i, REL_CALL) for i in dests_call]

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

