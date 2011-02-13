import unittest
from datastore import DataStore, CommentPosition
from idis.defaultmockproxy import DefaultMockProxy
from arch import getDecoder

from idis.tools import *


class miscTestCases(unittest.TestCase):

    def test_notInDS(self):
        ds = DataStore(":memory:")
        self.assertEqual(False, 0 in ds)
        self.assertEqual(False, 1 in ds)
        self.assertEqual(False, -1 in ds)

    def test_inBasicDNoSDefault(self):
        ds = DataStore(":memory:")
        data = [0, 1, 2, 3, 4, 5, 6, 7]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        # These are IDENT based addresses
        self.assertEqual(False, -1 in ds)
        self.assertEqual(False, 0 in ds)
        self.assertEqual(False, 7 in ds)
        self.assertEqual(False, 8 in ds)

    def test_inBasicDSDefault(self):
        ds = DefaultMockProxy(DataStore(":memory:"))
        data = [0, 1, 2, 3, 4, 5, 6, 7]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        # These are IDENT based addresses
        self.assertEqual(False, -1 in ds)
        self.assertEqual(True, 0 in ds)
        self.assertEqual(True, 1 in ds)
        self.assertEqual(True, 2 in ds)
        self.assertEqual(True, 3 in ds)
        self.assertEqual(True, 4 in ds)
        self.assertEqual(True, 5 in ds)
        self.assertEqual(True, 6 in ds)
        self.assertEqual(True, 7 in ds)
        self.assertEqual(False, 8 in ds)

    def test_inBasicDS2Default(self):
        ds = DefaultMockProxy(DataStore(":memory:"))

        data = [0, 1, 2, 3, 4, 5, 6, 7]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        def fakeCallable():
            ds[-1]
        self.assertRaises(KeyError, fakeCallable)

        for i in xrange(0, 8):
            ds[i]

        def fakeCallable():
            ds[8]
        self.assertRaises(KeyError, fakeCallable)

    # Ensure defaults created in the default
    # mock don't migrate to the datastore
    # [regression check]
    def test_defaultsNoPropogate(self):
        ds = DataStore(":memory:")

        defs = DefaultMockProxy(ds)
        ds.segments.addSegment(0x0, 3, "ROM", [1, 2, 3])

        defs[0]

        rc, obj = ds.lookup(0)
        self.assertEquals(rc, ds.LKUP_NONE)

    def test_inBasicDS3Default(self):
        ds = DefaultMockProxy(DataStore(":memory:"))

        data = [0, 1, 2, 3, 4, 5, 6, 7]
        data2 = map(lambda x: x + 10, data)

        ds.segments.addSegment(0x00, len(data), "ROM", data)
        ds.segments.addSegment(0x80, len(data), "ROM", data2)

        # TODO: FIX THIS HACK
        it = ds.segments.__iter__()
        it.next()
        addr = it.next().mapOut(0x80)

        ds[0]
        ds[1]

        # try second segment
        ds[addr]
        ds[addr + 1]

    def test_dataStoreOverlap(self):
        ds = DataStore(":memory:", arch.getDecoder)
        data = [0x02, 0xFF, 0x9A, 0x00, 0x00, 0x00]   # 8051 ljmp + 3 * 0x0

        ds.segments.addSegment(0x00, len(data), "ROM", data)
        ds[0] = m = MemoryInfo.createForTypeName(ds, 0, "8051")

        # Verify we can lookup objects by an address within them
        rc, val = ds.lookup(2)
        self.assertEquals(rc, ds.LKUP_OVR)
        self.assertEquals(val, m)

        rc, val = ds.lookup(3)

        # Verify that we can't find an address that doesn't exist,
        #   but is in memory
        self.assertEquals(rc, ds.LKUP_NONE)
        self.assertEquals(val, None)

        # Verify that mapped addresses w/o obs don't have a startaddr
        self.assertEquals(None, ds.findStartForAddress(3))

        # Verify that objs work properly
        self.assertEquals(0, ds.findStartForAddress(2))
        self.assertEquals(0, ds.findStartForAddress(1))
        self.assertEquals(0, ds.findStartForAddress(0))

        # Make sure that non-mapped addresses don't have startaddr
        self.assertEquals(None, ds.findStartForAddress(24))

    def test_dataStoreOverlapDefaults(self):
        ds = DefaultMockProxy(DataStore(":memory:", arch.getDecoder))
        data = [0x02, 0xFF, 0x9A, 0x00, 0x00, 0x00]   # 8051 ljmp + 3 * 0x0

        ds.segments.addSegment(0x00, len(data), "ROM", data)
        ds[0] = m = MemoryInfo.createForTypeName(ds, 0, "8051")

        rc, val = ds.lookup(2)

        self.assertEquals(rc, ds.LKUP_OVR)
        self.assertEquals(val, m)

        rc, val = ds.lookup(3)

        self.assertEquals(rc, ds.LKUP_OK)

        self.assertEquals(3, ds.findStartForAddress(3))
        self.assertEquals(0, ds.findStartForAddress(2))
        self.assertEquals(0, ds.findStartForAddress(1))
        self.assertEquals(0, ds.findStartForAddress(0))

        self.assertEquals(None, ds.findStartForAddress(24))

    def test_Undefine(self):
        ds = DataStore(":memory:", arch.getDecoder)

        data = [0, 1, 2, 3, 4, 5, 6, 7]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        ds[0] = m = MemoryInfo.createForTypeName(ds, 0, "8051")
        self.assert_(m)

        undefine(ds, 0)

    def test_CodeFolow(self):
        ds = DataStore(":memory:", getDecoder)
        addBinary(ds, "performance/src/8051_flash_trunc.bin", 0, 0, 0x8000)
        codeFollow(ds, "8051", 0)

    def test_CodeFollowCheckCommentLabels(self):
        ds = DataStore(":memory:", getDecoder)
        addBinary(ds, "performance/src/8051_flash_trunc.bin", 0, 0, 0x8000)
        ds.symbols.setSymbol(0x0, "hello")
        ds.comments.setComment(0x0, "blah", CommentPosition.POSITION_RIGHT)
        codeFollow(ds, "8051", 0)

        self.assertEqual(ds.symbols.getSymbol(0x0), "hello")
        self.assertEqual(ds.comments.getCommentText(0x0,
            CommentPosition.POSITION_RIGHT), "blah")

    def test_NoDecoderLookupException(self):
        ds = DataStore(":memory:")

        data = [1, 2, 3, 4]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        def _call():
            m = MemoryInfo.createForTypeName(ds, 0, "fakeTypeName")

        self.assertRaises(NotImplementedError, _call)

suite = unittest.TestLoader().loadTestsFromTestCase(miscTestCases)
