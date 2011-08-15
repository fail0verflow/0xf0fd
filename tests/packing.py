import unittest
import util.pack_unpack_tools as p


class TestPackUnpack(unittest.TestCase):
    def test_PackUnpack8(self):
        a = [1, 19, 32, 64, 7, 11, 0, 255]

        a_packed = p.intsToByteList(8, a)

        # intsToByteList(8, ...) is the identity
        # function for inputs with 8 bit members
        self.assertEquals(a_packed, a)

        a_unpacked = p.byteListToInts(8, a_packed)

        self.assertEquals(a_unpacked, a)

    def test_PackUnpack7(self):
        a = [1, 19, 32, 64, 7, 11, 0, 127]

        a_packed = p.intsToByteList(7, a)

        # intsToByteList(7, ...) is the identity
        # function for inputs with 7 bit members
        self.assertEquals(a_packed, a)

        a_unpacked = p.byteListToInts(7, a_packed)

        self.assertEquals(a_unpacked, a)

    def test_PackUnpack9(self):
        a = [1, 19, 32, 64, 7, 11, 0, 257]

        a_packed = p.intsToByteList(9, a)

        a_unpacked = p.byteListToInts(9, a_packed)

        self.assertEquals(a_unpacked, a)

    def test_PackUnpack23(self):
        a = [1, 19, 32, 64, 7, 11, 0, 123456]

        a_packed = p.intsToByteList(23, a)

        a_unpacked = p.byteListToInts(23, a_packed)

        self.assertEquals(a_unpacked, a)


suite = unittest.TestSuite([
    unittest.TestLoader().loadTestsFromTestCase(TestPackUnpack)])
