
import unittest
from datastore import DataStore
from idis.dbtypes import CommentPosition
from idis.tools import *
import sqlite3
import functools
# Regression/functionality/unit tests for segment


class segmentFunctionalityCases(unittest.TestCase):
    def setUp(self):
        self.ds = DataStore(":memory:")
        data = [1, 2, 3, 4, 5]
        self.ds.segments.addSegment(0x1234, len(data), "ROM", data)
        self.seg = self.ds.segments.__iter__().next()

    def test_segok(self):
        self.assert_(self.seg)

    def test_segNoOk(self):
        self.assertEquals(self.seg.seg_no, 0)

    def test_segSizeOk(self):
        self.assertEquals(self.seg.size, 5)

    def test_segStartAddr(self):
        self.assertEquals(self.seg.start_addr, 0x1234)

    def test_segName(self):
        self.assertEquals(self.seg.name, "ROM")

    def test_readBytes1(self):
        self.assertEquals(self.seg.readBytes(0x1234)[0], 1)

    def test_readBytes2(self):
        self.assertEquals(self.seg.readBytes(0x1238)[0], 5)

    def test_readBytesFail1(self):
        self.assertRaises(IOError, functools.partial(
            self.seg.readBytes, 0x1239
            ))

    def test_readBytesFail2(self):
        self.assertRaises(IOError, functools.partial(
            self.seg.readBytes, 0x1233
            ))

    def test_mapInOutRoundTrip(self):
        addr = 0x1

        # should map to addr 0x1235 -
        #   but this is an implementation detail

        mapped_in = self.seg.mapIn(addr)
        mapped_out = self.seg.mapOut(mapped_in)

        self.assertEquals(
            addr,
            mapped_out)

    def test_mapInLinearity(self):
        self.assertEquals(
            self.seg.mapIn(0) + 2,
            self.seg.mapIn(0 + 2)
            )

    def test_mapInOOR1(self):
        self.assertRaises(ValueError, functools.partial(
            self.seg.mapIn, 0x1233
            ))

    def test_mapInOOR2(self):
        self.assertRaises(ValueError, functools.partial(
            self.seg.mapIn, 0x1239
            ))


# Same tests as above class, just force database persistence
class segmentListPersistence(segmentFunctionalityCases):
    def setUp(self):
        db = sqlite3.connect(":memory:")

        # Populate the datastore
        self.ds = DataStore(db)
        data = [1, 2, 3, 4, 5]
        self.ds.segments.addSegment(0x1234, len(data), "ROM", data)
        self.seg = self.ds.segments.__iter__().next()
        del self.ds

        # Reload the datastore from the db
        self.ds = DataStore(db)


class segmentListFunctionality(unittest.TestCase):
    # Verify that the layoutChanged signal is emitted
    def testAddLayoutChanged(self):
        fired = [False]

        def mockChangeHDLR():
            fired[0] = True

        ds = DataStore(":memory:")
        ds.layoutChanged.connect(mockChangeHDLR)

        data = [0, 1, 2, 3, 4]
        ds.segments.addSegment(0x0, len(data), "ROM", data)
        self.assertEqual(fired[0], True)

suite = unittest.TestSuite([
    unittest.TestLoader().loadTestsFromTestCase(segmentFunctionalityCases),
    unittest.TestLoader().loadTestsFromTestCase(segmentListFunctionality),
    unittest.TestLoader().loadTestsFromTestCase(segmentListPersistence)
    ])
