from datastore.dbtypes import *
from datastore.infostore import InfoStore
import arch
from arch.common.hacks import *
import traceback


# Attach hooks to notifications from datastore
def registerFunctionality(ds):
    registerXrefChangeTracker(ds)


# Update Xref info cache when infostore changes
def registerXrefChangeTracker(ds):
    def xrefChangeTracker(ident, typ):
        ds.xreflist.delXrefFrom(ident)

        # If update is not a delete, rebuild the xrefs for the meminfo
        if typ != ds.infostore.INF_CHG_DEL:
            status, result = ds.infostore.lookup(ident)

            if status == ds.infostore.LKUP_OK:
                buildXrefForInfo(ds, result)

    ds.infostore.infoChanged.connect(xrefChangeTracker)


def buildXrefForInfo(ds, insn):
    segment = ds.segments.findSegment(insn.addr)
    for dest, typ in ((segment.mapOut(i), typ)
            for i, typ in insn.disasm.dests()):

        # No xrefs for next-instruction flow
        if dest == insn.addr + insn.length:
            continue

        flags = ds.xreflist.XREF_CODE

        if typ == REL_CALL:
            flags |= ds.xreflist.XREF_CODE_CALL
            print insn.addr, dest

        ds.xreflist.addXref(insn.addr, dest, flags)  # HACK, always code


# Manual Xref rebuild process
def rebuildXrefs(ds):
    ds.xreflist.clearXrefs()

    for insn in ds.infostore:
        buildXrefForInfo(ds, insn)


# entry_point is an ident
def codeFollow(ds, arch_name, entry_point):
    from applogic.cmd import CompoundCommand, SetTypeCommand
    cc = CompoundCommand()

    from types import FunctionType

    # MAP entry_point to addr - ensure all dests within same seg?
    #                         - run dests thru reverse mapper?

    q = [entry_point]
    arch_info = arch.machineFactory(ds, arch_name)

    local_set = set()

    while q:
        pc = q.pop()

        rcode, _ = ds.infostore.lookup(pc)

        if rcode != InfoStore.LKUP_NONE or pc in local_set:
            continue

        try:
            fetched_mem = ds.readBytes(pc, arch_info.max_length)
        except IOError:
            # If the generated addr is outside of mapped memory, skip it
            continue

        # TODO: HACK: 6 repeated 0xFF's = uninited mem
        if all([i == 0xFF for i in fetched_mem]):
            continue

        segment = ds.segments.findSegment(pc)

        try:
            insn = arch_info.disassemble(pc, None)
        except IOError:
            continue
        except Exception:
            traceback.print_exc()
            continue

        # If we can't decode it, leave as is
        if not insn:
            continue

        # Make sure memory is clear
        mem_clear = True
        for i in xrange(1, insn.length()):
            try:
                rc, _ = ds.infostore.lookup(pc + i)
                if rc != InfoStore.LKUP_NONE:
                    mem_clear = False
            except KeyError:
                pass
        if not mem_clear:
            continue

        # HACK - Add destinations, use IR
        try:
            q.extend([segment.mapOut(i) for i, _ in insn.dests()])
        except ValueError:
            q.extend([insn.length() + pc])
        except AttributeError:
            q.extend([insn.length() + pc])

        cc.add(SetTypeCommand(pc, arch_name, insn.length()))
        local_set.update(xrange(pc, pc + insn.length()))

    ds.cmdlist.push(cc)
