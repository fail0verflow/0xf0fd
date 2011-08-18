from arch.common.machine import *
import arch.common.bits as bits
from arch.common.builders import get_MachineInstructionBuilder
from arch.shared_opcode_types import *
from arch.common.hacks import *
import math

class OpSBIT(Operand):
    def __init__(self, v):
        self.__v = v

    def render(self, ds, segment):
        return "%s" % self.__v, TYPE_UNSPEC

class OpB4(Operand):
    def __init__(self, value):
        self.__v = value

    def render(self, ds, segment):
        return "0x%x" % (self.__v), TYPE_UNSPEC


class OpK(Operand):
    def __init__(self, width, value):
        self.__w = width
        self.__v = value

    @property
    def value(self):
        return self.__v

    def render(self, ds, segment):
        return "#0x%0*x" % (int(math.ceil(self.__w/4)), self.__v), TYPE_UNSPEC

class OpWInd(Operand):
    def __init__(self, n, m, wb=None):
        self.__n = n
        self.__m = m
        self.__wb = wb

    def render(self, ds, segment):

        if self.__m in (6, 7):
            assert self.__wb
            return "[W%d + W%d]" % (self.__n, self.__wb), TYPE_UNSPEC


        pp = {
                0: None,
                1: ('', ''),
                2: ('', '--'),
                3: ('', '++'),
                4: ('--', ''),
                5: ('++', '')} [self.__m]

        if pp:
            return "[%sW%d%s]" % (pp[0], self.__n, pp[1]), TYPE_UNSPEC

        return "W%d" % (self.__n), TYPE_UNSPEC


class OpW(OpWInd):
    def __init__(self, n):
        return super(OpW, self).__init__(n, 0)

class OperandOffset(object):
    def __init__(self, addr, dbus = 0):
        self.addr = addr
        self.dbus = dbus

    def render(self, ds, segment):
        # Map out the offset on the specified addr bus
        __i = segment.translateOut(self.addr, self.dbus)

        # Find the segment that that ident corresponds to
        ns = ds.segments.findSegment(__i)


        typecode = TYPE_UNSPEC
        if ds:
                rc, obj = ds.infostore.lookup(__i)

                if rc != ds.infostore.LKUP_OK:
                    typecode = TYPE_DEST_INVALID

                elif obj.label:
                    return obj.label, TYPE_SYMBOLIC

        # No name -
        #  Map it back in to a segment-local address
        naddr = ns.mapIn(__i)
        if ns != segment:
            return "%s:%04x" % (ns.name, naddr), typecode

        return "%04x" % (naddr), typecode

class OpF(OperandOffset):
    def __init__(self, n):
        super(OpF, self).__init__(n, 1)


class OperandPCOffset(OperandOffset):
    def __init__(self, addr):
        super(OperandPCOffset, self).__init__(addr, 0)

