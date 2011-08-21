def BITS(d,l,n,signed=False):
    d = (d >> l) & ((1 << n) - 1)
    if signed and d & (1 << (n - 1)):
        return d - (1 << n)
    return d

def BIT(d,l):
    return BITS(d, l, 1, False)


from operands import *

class _stub(object):
    pass

def Fmt1(word1):
    s = _stub()
    _Z = BIT(word1, 15)
    _W = BITS(word1, 11, 4)
    _D = BITS(word1, 7, 4)
    _P = BITS(word1, 4, 3)
    _s = BITS(word1, 0, 4)

    s.Z = 'C' if _Z else 'Z'
    s.W = OpW(_W)
    s.D = OpW(_D)
    s.S = OpWInd(_s, _P)

    return s

def Fmt2(word1):
    s = _stub()
    _B = BIT(word1, 14)
    _Q = BITS(word1, 11, 3)
    _D = BITS(word1, 7, 4)
    _P = BITS(word1, 4, 3)
    _S = BITS(word1, 0, 4)

    s.B = _B
    s.D = OpWInd(_D, _Q)
    s.S = OpWInd(_S, _P)

    return s

def Fmt3(word1):
    s = _stub()
    _B = BIT(word1, 14)
    _D = BIT(word1, 13)
    _F = BITS(word1, 0, 13)
    s.F = OpF(_F)
    s.D = _D
    s.B = _B
    return s

def Fmt4(w0, w1):
    s = _stub()
    _N = (BITS(w0, 0, 16) & 0xFFFE) | \
          BITS(w1, 0, 7) << 16
    s.N = OperandOffset(_N)

    return s

def Fmt5(w0):
    s = _stub()
    _B = BIT(w0, 14)
    _K = BITS(w0, 4, 10)
    _D = BITS(w0, 0, 4)

    s.B = _B
    s.K = OpK(10, _K)
    s.D = OpW(_D)

    return s

def Fmt6(word):
    s = _stub()
    _K = BITS(word, 0, 15)
    s.K = OpK(15, _K)
    return s

def Fmt7(pc, word):
    s = _stub()

    slit16 = BITS(word, 0, 16, signed=True)
    _N = 2 * slit16 + pc + 2

    s.N = OperandOffset(_N)

    return s

def Fmt8(word):
    s = _stub()

    _W = BITS(word, 15, 4)
    _B = BIT(word, 13)
    _Q = BITS(word, 11, 3)
    _D = BITS(word, 7, 4)

    _P = BITS(word, 4, 3)
    _S = BITS(word, 0, 4)

    _K = BITS(word, 0, 5)

    if _P & 0x6 == 6:
        s.src = OpK(5, _K)
    else:
        s.src = OpWInd(_S, _P)

    s.W = OpW(_W)
    s.D = OpWInd(_D, _Q)
    s.B = _B
    return s

def Fmt9(w0):
    s = _stub()
    s.K = OpK(16, BITS(w0, 4, 16))
    s.D = OpW(BITS(w0, 0, 4))
    return s

def Fmt10(w0):
    s = _stub()

    # Implied 0 LSB
    _F = BITS(w0,4,15) * 2
    _R = BITS(w0, 0, 4)
    s.F = OpF(_F)
    s.R = OpW(_R)
    return s

def Fmt11(word):
    s = _stub()

    _S = BITS(word, 0, 4)
    _D = BITS(word, 7, 4)

    _K = BITS(word, 4, 3) | \
            BITS(word, 11, 3) << 3 | \
            BITS(word, 15, 4) << 6

    _K = BITS(_K, 0, 10, True)

    _B = BIT(word, 14)

    flg = BIT(word, 19)

    if not flg:
        s.src = OpW_disp(_S, _K)
        s.dst = OpW(_D)
    else:
        s.src = OpW(_S)
        s.dst = OpW_disp(_D, _K)

    s.B = _B

    return s


def Fmt12(w0):
    s = _stub()
    _B = not BITS(w0, 10, 1)
    _Z = not BITS(w0, 11, 1)
    _b = BITS(w0, 12, 4)

    _P = BITS(w0, 4, 3)
    _S = BITS(w0, 0, 4)

    s.S = OpWInd(_S, _P)
    s.Z = 'C' if _Z else 'Z'
    s.B = _B
    s.b = OpB4(_b)

    return s



def Fmt13(w0):
    s = _stub()
    _F = BITS(w0, 1, 12) << 1
    _B = not BITS(w0, 0, 1)
    _b = BITS(w0, 13, 3) | BITS(w0, 0, 1) << 3

    s.F = OpF(_F)
    s.B = _B
    s.b = OpB4(_b)

    return s

def Fmt14(word):
    raise NotImplementedError

def Fmt15(w0):
    s = _stub()
    _W = BITS(w0, 11, 4)
    _D = BITS(w0, 7, 4)

    flg = BIT(w0, 6)

    s.W = OpW(_W)
    s.D = OpW(_D)

    if flg:
        _K = BITS(w0, 0, 4)
        s.src = OpK(4, _K)
    else:
        _S = BITS(w0, 0, 4)
        s.src = OpK(4, _S)

    return s


def Fmt16(word):
    raise NotImplementedError

def Fmt17(w0, is_e):
    s = _stub()

    _S = BITS(w0, 0, 4)
    _P = BITS(w0, 4, 3)
    _K = BITS(w0, 0, 5)
    _K_sw = 5

    # E core supports 8 bit literals
    if is_e:
        _K |= BIST(w0, 7, 3) << 5
        _K_sw = 8

    _B = BIT(w0, 14)
    _W = BITS(w0, 15, 4)

    if _P & 0x6 == 0x6:
        s.S = OpK(_K_sw, _K)
    else:
        s.S = OpWInd(_S, _P)

    s.W = OpW(_W)
    s.B = _B

    return s

def Fmt18(word):
    raise NotImplementedError

def Fmt19(word):
    raise NotImplementedError

def Fmt20(word):
    raise NotImplementedError

def Fmt21(word):
    raise NotImplementedError

def Fmt22(word):
    raise NotImplementedError

def Fmt23(word):
    raise NotImplementedError

def Fmt24(word):
    raise NotImplementedError

def Fmt25(w0):
    s = _stub()

    _S = BITS(w0, 0, 4)
    _G = BITS(w0, 4, 3)
    _D = BITS(w0, 7, 4)
    _H = BITS(w0, 11, 3)
    _B = BIT(w0, 14)
    _W = BITS(w0, 15, 4)

    s.B = _B

    s.S = OpWInd(_S, _G, _W)
    s.D = OpWInd(_D, _H, _W)

    return s
