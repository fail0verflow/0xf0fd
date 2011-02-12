from dbtypes import *
import arch

# Clean and rebuild should never need to be called
# FIXME: Remove after verifying there is no use case
def clean(ds):
    cleanlist = []
    for i in ds:
        if "insn" in i.cdict:
            for j in xrange(i.length-1):
                if i.addr + j + 1 in ds:
                    cleanlist .append( i.addr + j + 1)
    for i in cleanlist:
        del ds[i]

# FIXME: Remove after verifying there is no use case
def rebuild(ds, arch):
    for i in ds:
        if "insn" in i.cdict:
            fetched_mem = ds.readBytes(i.addr,6)    
            insn = arch.decode(i.addr, fetched_mem)
            
            if (insn.length != i.length):
                raise ValueError, "New instruction length, can't rebuild"

            i.disasm = insn.disasm
            i.cdict["decoding"] = insn

    
# entry_point is an ident
def codeFollow(ds, arch_name, entry_point):
    from types import FunctionType

    # MAP entry_point to addr - ensure all dests within same seg?
    #                         - run dests thru reverse mapper?

    q = [entry_point]
    arch_info = arch.machineFactory(ds, arch_name)

    while q:
        pc = q.pop()

        if pc in ds and ds[pc].typeclass != "default":
            continue
        
        try:
            ds[pc]
        except KeyError:
            continue

        try:
            fetched_mem = ds.readBytes(pc,arch_info.max_length)
        except IOError:
            # If the generated addr is outside of mapped memory, skip it
            continue

        # TODO: HACK: 6 repeated 0xFF's = uninited mem
        if all([i==0xFF for i in fetched_mem]):
            continue
       
        segment = ds.segments.findSegment(pc)
        
        try:
            insn = arch_info.disassemble(pc, None)
        except IOError:
            continue
            
        # If we can't decode it, leave as is
        if not insn:
            continue
        
        # Make sure memory is clear
        mem_clear = True
        for i in xrange(insn.length()):
            try:
                if ds[pc + i].typeclass != "default" : mem_clear = False
            except KeyError: pass
        if not mem_clear: continue
        
        # HACK - Add destinations, use IR
        try:
            q.extend([segment.mapOut(i) for i, _ in insn.dests()])
        except AttributeError:
            q.extend([insn.length()+pc])


        m = MemoryInfo.createForTypeName(ds, pc, arch_name)

        for i in xrange(m.length):
            try:
                del ds[pc + i]
            except KeyError:
                pass

        ds[pc] = m
        
