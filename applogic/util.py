

# Create a human readable name from a segment identifier
# Format:
#    SEGNAME:00000000
def formatIdent(ds, ident):
    s = ds.segments.findSegment(ident)

    if not s:
        return None

    segment_vaddr = s.mapIn(ident)

    return "%s:%08x" % (s.name, segment_vaddr)
