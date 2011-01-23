# vim: set fileencoding=utf-8 :

from cPickle import *
import zlib
import sqlite3
from array import array

#
#   Segmentation concepts:
#
#   A segment is defined by (start, size)
#
#   The contiguous region defined by [start...start+size) may overlap with other segments
#   
#   To uniquely identify a location within a segment, the segments are mapped into a 64bit
#   unique identifier space, where each unique identifier is called an ident.
#
#   An iden is composed of:
#
#   [  14 bit segment number  ][ 50 bit seginternal ]
#
#   Where seginternal is used by the segment to identify the location address
#   seginternal is arbitrary, subject to the restriction that
#
#           mapin(addr + a) == ident + a
#
#   given:  mapin(addr) = ident, addr >= seg.start, addr + i < seg.start + seg.size
#
#   holds true.
#   
#
#   NOTE that a "location" within a segment does not necessarily refer to a byte-width
#   Many embedded system architectures have non-multiple-of-8 addressable code storage
#   The exact behavior of the code segment setup is dependent on the architecture


# The following simple mapIn / mapOut functions use a simple
# segInternal / ident mapping. This relation not need be true in the future,
# as long as the constraints above hold
def defaultMapIn(ident, seg):
    seg_no = (ident >> 50) & 0x3FFF
    if seg_no != seg.seg_no:
        raise ValueError("wrong segment for map")

    seg_internal = (ident & 0x3FFFFFFFFFFFF)  + seg.start_addr
    return seg_internal

def defaultMapOut(seg_internal, seg):
    assert seg.start_addr <= seg_internal < (seg.start_addr + seg.size)

    return (seg.seg_no << 50) | (seg_internal - seg.start_addr)



class SegmentList(object):
    class Segment(object):
        def __init__(self, start_addr, size, segno, name, data, locationBitSize=8):
            # FIXME choose array type based on location bitsize
            # FIXME - also, data needs to be able to be indirectable

            self.__data = array('B', data)
            self.__start_addr = start_addr
            self.__name = name
            self.__segno = segno
            self.__size = size

            # FIXME: We don't have any processors that need this yet, but we will
            assert locationBitSize == 8

        # NOTE: Data packing / storage isn't guaranteed in this array
        # Only really for use by SegmentList
        def __getdata(self):
            return self.__data
        data = property(__getdata)

        def __getsize(self):
            return self.__size
        size = property(__getsize)
        
        def __getstartaddr(self):
            return self.__start_addr
        start_addr = property(__getstartaddr)
        
        def __getsegno(self):
            return self.__segno
        seg_no = property(__getsegno)

        def __getname(self):
            return self.__name
        name = property(__getname)

        def readBytes(self, seg_internal_start, length = 1):
            if (seg_internal_start < self.__start_addr or seg_internal_start >= self.__start_addr + self.__size):
                raise IOError, "not in segment"
            return self.__data[seg_internal_start - self.__start_addr:seg_internal_start - self.__start_addr+length]

        # In/out are in terms of "into" /"out of" segment terms
        # so mapIn is map an ident into segment terms, aka, get an addr
        # based on this segments view of the world

        def mapIn(self, ident):
            """get a segment-virtual address from an ident. Throws valuerror if ident could not be mapped"""
            seg_internal = defaultMapIn(ident, self)
            if not (self.__start_addr <= seg_internal < (self.__start_addr + self.__size)):
                raise ValueError
            return seg_internal

        def mapOut(self, addr):
            """get an ident from a segment-virtual address"""
            # Note - behavior when mapping to an address not within our space is as-yet undefined.
            # A good initial behavior is to assume the segment list is no-overlapping, and walk the list
            # until we find dest_addr ∈ [segment.start ... segment.start + size)
            # we should allow hooking at a per-segment or global level of this process
            # For now, use the standard mapin / mapout functions, and just throw valueerror if not within the segment

            if self.__start_addr <= addr < (self.__start_addr + self.__size):
                return defaultMapOut(addr, self)
            raise ValueError


    def __init__(self, conn, ds):
        self.__conn = conn

        self.setupSQL()        
        self.segments_cache = []
        self.__populateSegments()
        self.ds = ds


    def __iter__(self):
        return self.segments_cache.__iter__()

    def __populateSegments(self):
        for segno, start_addr, size, name, data in self.__conn.execute('''SELECT segno, start_addr, size, name, data FROM segments'''):
            data = [ord(i) for i in zlib.decompress(data)]

            self.segments_cache.append(SegmentList.Segment(start_addr, size, segno, name, data))

    def findSegment(self, ident):
        for i in self.segments_cache:
            try:
                i.mapIn(ident)
            except:
                pass
            else:
                return i
        return None

    def setupSQL(self):
        self.__conn.execute('''
            CREATE TABLE IF NOT EXISTS segments
                (segno INTEGER PRIMARY KEY ASC,
                 start_addr INTEGER,
                 size INTEGER,
                 name STRING,
                 data BLOB)''')

    def addSegment(self, start_addr, size, name, data):
        # Create a new segment number
        segno = max(map(lambda x: x.seg_no, self.segments_cache)) + 1 if self.segments_cache else 0

        # Create segment object
        segment = SegmentList.Segment(start_addr, size, segno, name, data)

        # Add it to the list of segments
        self.segments_cache.append(segment)

        dbstr = sqlite3.Binary(zlib.compress("".join([chr(i) for i in segment.data])))

        self.__conn.execute('''INSERT INTO segments (segno, start_addr, size, name, data) VALUES (?,?,?,?,?)''',
              (segment.seg_no, segment.start_addr, segment.size, segment.name, dbstr))

        self.ds.layoutChanged()
