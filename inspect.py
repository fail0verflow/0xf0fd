import sys

from datastore import DataStore
from arch import getDecoder


def main():
    ds = DataStore(sys.argv[1], getDecoder)

    location = ds[int(sys.argv[2], 0)]

    print """
    Address: %04x
    length: %d
    TypeClass: %s
    TypeName: %s""" % (location.addr, location.length,
        location.typeclass, location.typename)
    print "\tRawBytes: %s" % " ".join(
        ["%02x" % i for i in ds.readBytes(location.addr, location.length)])

if __name__ == "__main__":
    main()
