from arch.shared_opcode_types import *
from arch.shared_mem_types import *
from datastore.dbtypes import *
from tools_algos import *
from tools_loaders import *


# Undefine a specific opcode [should this have a
#   follow-until-other-assigned mode]?
def undefine(ds, addr):
    ds.infostore.remove(addr)


# Takes an ident and returns the logical "following" ident
def follow(ds, ident):
    rc, d = ds.infostore.lookup(ident)
    if rc != ds.infostore.LKUP_OK:
        return None

    dests = d.disasm.dests()

    segment = ds.segments.findSegment(ident)

    for j, _ in dests:
        if j == segment.mapIn(d.addr) + d.length:
            continue

        rc, dest_info = ds.infostore.lookup(segment.mapOut(j))
        if rc != ds.infostore.LKUP_OK:
            return None

        return segment.mapOut(j)

    return None
