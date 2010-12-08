# test, set, clear a single bit:
def test(value, bit):
    return value & (1 << bit)
def set(value, bit):
    return value | (1 << bit)
def clear(value, bit):
    return value & ~(1 << bit)

# get a range of bits, top and bottom are zero-based, and inclusive.
def get(source, top, bottom):
    mask = (1 << (top-bottom)+1) - 1
    return (source >> bottom) &  mask
