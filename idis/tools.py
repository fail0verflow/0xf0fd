from arch.shared_opcode_types import *
from arch.shared_mem_types import *
from datastore.dbtypes import *
from tools_algos import *
from tools_loaders import *


# Undefine a specific opcode [should this have a
#   follow-until-other-assigned mode]?
def undefine(ds, addr):
    l = ds[addr].length
    del ds[addr]


def decodeAs(ds, dec_type, memaddr):
    old_mem = ds[memaddr]

    params = getDecoder(dec_type)(ds, memaddr)

    if not params:
        return False

    # Make sure the range needded for the new data is clear
    for i in xrange(params["length"]):
        try:
            if ds[memaddr + i].typeclass != "default":
                return
        except KeyError:
            pass

    # Carry over old label and comment
    m = MemoryInfo.createFromDecoding(params)
    m.ds = ds
    m.label = old_mem.label
    m.comment = old_mem.comment

    for i in xrange(params["length"]):
        try:
            del ds[memaddr + i]
        except KeyError:
            pass

    ds[memaddr] = m


# Takes an ident and returns the logical "following" ident
def follow(ds, ident):
    try:
        d = ds[ident]
        dests = d.disasm.dests()
    except KeyError:
        return None

    segment = ds.segments.findSegment(ident)

    for j, _ in dests:
        if j == segment.mapIn(d.addr) + d.length:
            continue

        try:
            print segment.mapOut(j)
            dest_info = ds[segment.mapOut(j)]
        except KeyError:
            pass

        return segment.mapOut(j)

    return None
