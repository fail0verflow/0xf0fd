import math


def intsToByteList(bits_per_unit, data):
    d = []
    n_bytes = int(math.ceil(bits_per_unit / 8.))
    for i in data:
        for j in xrange(0, n_bytes):
            d.append(i & 0xFF)
            i = i >> 8

    return d


def byteListToInts(bits_per_unit, packed_data):
    n_bytes = int(math.ceil(bits_per_unit / 8.))

    data = [reduce(lambda x, y: x << 8 | y,
                    packed_data[i:i + n_bytes][::-1])
             for i in xrange(0, len(packed_data), n_bytes)]
    return data
