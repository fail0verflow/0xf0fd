import unittest
from datastore import DataStore, CommentPosition, InfoStore
from applogic.defaultmockproxy import DefaultMockProxy
from arch import getDecoder
import sqlite3
from applogic.tools import *


class miscTestCases(unittest.TestCase):

    def test_actualPersistence(self):
        sql = sqlite3.connect(":memory:")

        ds = DataStore(sql, getDecoder)
        data = [0, 1, 2, 3, 4, 5, 6, 7]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        ds.infostore.setType(1, "8051")

        ds.flush()
        del ds

        #print [i for i in sql.execute("SELECT * from memory_info")]
        ds2 = DataStore(sql, getDecoder)
        rc, obj = ds2.infostore.lookup(1)

        self.assertEquals(rc, InfoStore.LKUP_OK)
        self.assertEquals(obj.addr, 1)

    def test_notInDS(self):
        ds = DataStore(":memory:")
        self.assertEqual(False, 0 in ds.infostore)
        self.assertEqual(False, 1 in ds.infostore)
        self.assertEqual(False, -1 in ds.infostore)

    def test_inBasicDNoSDefault(self):
        ds = DataStore(":memory:")
        data = [0, 1, 2, 3, 4, 5, 6, 7]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        # These are IDENT based addresses
        self.assertEqual(False, -1 in ds.infostore)
        self.assertEqual(False, 0 in ds.infostore)
        self.assertEqual(False, 7 in ds.infostore)
        self.assertEqual(False, 8 in ds.infostore)

    def test_inBasicDSDefault(self):
        ds = DefaultMockProxy(DataStore(":memory:"))
        data = [0, 1, 2, 3, 4, 5, 6, 7]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        # These are IDENT based addresses
        self.assertEqual(False, -1 in ds.infostore)
        self.assertEqual(True, 0 in ds.infostore)
        self.assertEqual(True, 1 in ds.infostore)
        self.assertEqual(True, 2 in ds.infostore)
        self.assertEqual(True, 3 in ds.infostore)
        self.assertEqual(True, 4 in ds.infostore)
        self.assertEqual(True, 5 in ds.infostore)
        self.assertEqual(True, 6 in ds.infostore)
        self.assertEqual(True, 7 in ds.infostore)
        self.assertEqual(False, 8 in ds.infostore)

    def test_inBasicDS2Default(self):
        ds = DefaultMockProxy(DataStore(":memory:"))

        data = [0, 1, 2, 3, 4, 5, 6, 7]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        def fakeCallable():
            ds.infostore[-1]
        self.assertRaises(KeyError, fakeCallable)

        for i in xrange(0, 8):
            ds.infostore[i]

        def fakeCallable():
            ds.infostore[8]
        self.assertRaises(KeyError, fakeCallable)

    # Ensure defaults created in the default
    # mock don't migrate to the datastore
    # [regression check]
    def test_defaultsNoPropogate(self):
        ds = DataStore(":memory:")

        defs = DefaultMockProxy(ds)
        ds.segments.addSegment(0x0, 3, "ROM", [1, 2, 3])

        defs.infostore[0]

        rc, obj = ds.infostore.lookup(0)
        self.assertEquals(rc, InfoStore.LKUP_NONE)

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

        ds.infostore[0]
        ds.infostore[1]

        # try second segment
        ds.infostore[addr]
        ds.infostore[addr + 1]

    def test_dataStoreOverlap(self):
        ds = DataStore(":memory:", arch.getDecoder)
        data = [0x02, 0xFF, 0x9A, 0x00, 0x00, 0x00]   # 8051 ljmp + 3 * 0x0

        ds.segments.addSegment(0x00, len(data), "ROM", data)
        m = ds.infostore.setType(0, "8051")

        # Verify we can lookup objects by an address within them
        rc, val = ds.infostore.lookup(2)
        self.assertEquals(rc, InfoStore.LKUP_OVR)
        self.assertEquals(val, m)

        rc, val = ds.infostore.lookup(3)

        # Verify that we can't find an address that doesn't exist,
        #   but is in memory
        self.assertEquals(rc, InfoStore.LKUP_NONE)
        self.assertEquals(val, None)

        # Verify that mapped addresses w/o obs don't have a startaddr
        self.assertEquals(None, ds.infostore.findStartForAddress(3))

        # Verify that objs work properly
        self.assertEquals(0, ds.infostore.findStartForAddress(2))
        self.assertEquals(0, ds.infostore.findStartForAddress(1))
        self.assertEquals(0, ds.infostore.findStartForAddress(0))

        # Make sure that non-mapped addresses don't have startaddr
        self.assertEquals(None, ds.infostore.findStartForAddress(24))

    def test_dataStoreSetMulti(self):
        ds = DefaultMockProxy(DataStore(":memory:", arch.getDecoder))
        data = [0x02, 0xFF, 0x9A, 0x00, 0x00, 0x00]   # 8051 ljmp + 3 * 0x0

        ds.segments.addSegment(0x00, len(data), "ROM", data)
        m = ds.infostore.setType(0, "8051")
        self.assert_(m)
        ds.infostore.flush()

        m = ds.infostore.setType(0, "8051")
        self.assert_(m)
        ds.infostore.flush()

    def test_dataStoreOverlapDefaults(self):
        ds = DefaultMockProxy(DataStore(":memory:", arch.getDecoder))
        data = [0x02, 0xFF, 0x9A, 0x00, 0x00, 0x00]   # 8051 ljmp + 3 * 0x0

        ds.segments.addSegment(0x00, len(data), "ROM", data)
        m = ds.infostore.setType(0, "8051")

        rc, val = ds.infostore.lookup(2)

        self.assertEquals(rc, InfoStore.LKUP_OVR)
        self.assertEquals(val, m)

        rc, val = ds.infostore.lookup(3)

        self.assertEquals(rc, InfoStore.LKUP_OK)

        self.assertEquals(3, ds.infostore.findStartForAddress(3))
        self.assertEquals(0, ds.infostore.findStartForAddress(2))
        self.assertEquals(0, ds.infostore.findStartForAddress(1))
        self.assertEquals(0, ds.infostore.findStartForAddress(0))

        self.assertEquals(None, ds.infostore.findStartForAddress(24))

    def test_Undefine(self):
        ds = DataStore(":memory:", arch.getDecoder)

        data = [0, 1, 2, 3, 4, 5, 6, 7]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        m = ds.infostore.setType(0, "8051")
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
            ds.infostore.setType(0, "fakeTypeName")

        self.assertRaises(NotImplementedError, _call)

    def test_xrefStore(self):
        ds = DataStore(":memory:")

        xrs = ds.xreflist

        xrs.addXref(4, 8, xrs.XREF_CODE)
        xrs.addXref(9, 4, xrs.XREF_CODE)

        a1 = xrs.getXrefsTo(8)
        a2 = xrs.getXrefsFrom(4)

        self.assertEquals(len(a1), 1)
        self.assertEquals(len(a2), 1)

suite = unittest.TestLoader().loadTestsFromTestCase(miscTestCases)
