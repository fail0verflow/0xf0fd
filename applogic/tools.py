from arch.shared_opcode_types import *
from arch.shared_mem_types import *
from datastore.dbtypes import *
from tools_algos import *
from tools_loaders import *
import arch

import builtin_types
import type_base


known_types = None


# Todo - REWORK ALL THIS CRAP. The decoder system is so legacy and broken
#  that a complete rewrite wouldn't hurt. This should be the main entry point
#  rework all below here.
def typeFactory(datastore, typename):
    global known_types

    # Singleton instance for known types,
    #  create at startup
    if known_types == None:
        known_types = {}
        for i in type_base.DecodeTypeBase.__subclasses__():
            known_types[i.shortname] = i

    # Try finding a decoder for the built-in types
    if typename in known_types:
        return known_types[typename](datastore)

    return arch.getDecoder(datastore, typename)


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

        if rc == ds.infostore.LKUP_OVR:
            return None

        return segment.mapOut(j)

    return None
