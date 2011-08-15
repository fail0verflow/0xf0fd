from datastore.dbtypes import *
from datastore import SegmentList
from arch.shared_mem_types import *
import math


# All addrs here are segment-rel addresses
def addBinary(ds, file, base_addr, start_offset, length, bits=8, name=""):
    # Load the file

    # We assume little endian padding, aligned to byte sizes
    # bits are packed within the unit right aligned
    # IE, for a 14 bit unit:
    #
    # [0]bits7..0 [0]00bits14..8 [1]bits7..0 .....

    n_bytes_per = int(math.ceil(bits / 8.))

    file_data = [ord(i) for i in open(file).read()]
    end_offset = start_offset + length
    file_data = file_data[start_offset:end_offset]

    n_units = len(file_data) / n_bytes_per

    # repack rows to match data
    file_data = [reduce(lambda x, y: x << 8 | y,
                        file_data[i:i + n_bytes_per][::-1])
                 for i in xrange(0, len(file_data), n_bytes_per)]

    if length == -1:
        end_offset = n_units
    else:
        end_offset = start_offset + length

    ds.segments.addSegment(base_addr, len(file_data),
        name, file_data, bits)


def parseIhexLine(line):
    if line[0] != ':':
        print "Start char fail!"
        return
    bc = int(line[1:3], 16)
    addr = int(line[3:7], 16)
    rtype = int(line[7:9], 16)
    data = line[9:9 + 2 * bc]
    data = [int(data[i:i + 2], 16) for i in xrange(0, len(data), 2)]
    ck = int(line[9 + 2 * bc: 9 + 2 * bc + 2], 16)

    if bc != len(data):
        print "data len fail!"
        return

    calcck = (0x100 -
        (sum([bc, addr & 0xFF, addr >> 8, rtype] + data) & 0xFF)) & 0xFF

    if calcck != ck:
        print data
        print "Checksum Fail, %02x = %02x!" % (calcck, ck)
        return

    return rtype, addr, data


def addIHex(ds, file):
    lines = open(file).readlines()

    recs = []
    for i in lines:
        record = parseIhexLine(i)
        if not record:
            print "Error parsing line %s" % i
        recs.append(record)

    addrs = [(addr, addr + len(data))
        for rtype, addr, data in recs if rtype == 0x0]

    dmin = min([i[0] for i in addrs])
    dmax = max([i[1] for i in addrs])

    # build data array
    data = [0x0] * (dmax - dmin + 1)
    for rtype, addr, ldata in recs:
        if (rtype == 0x0):
            for offs, j in enumerate(ldata):
                data[offs + addr - dmin] = j

    ds.segments.addSegment(dmin, dmax - dmin, "CODE", data)
