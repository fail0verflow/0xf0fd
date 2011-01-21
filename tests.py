#!/usr/bin/python

import unittest
from idis.datastore import DataStore
from idis.dbtypes import Segment, CommentPosition
from idis.tools import *

class basicSectionTestCase(unittest.TestCase):

    def test_notInDS(self):
        ds = DataStore(":memory:")
        self.assertEqual(False, 0 in ds)
        self.assertEqual(False, 1 in ds)
        self.assertEqual(False, -1 in ds)

    def test_inBasicDS(self):
        ds = DataStore(":memory:")
        seg = Segment([0,1,2,3,4,5,6,7], 0x0)
        ds.addSegment(seg)
        
        
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

    def test_inBasicDS(self):
        ds = DataStore(":memory:")
        seg = Segment([0,1,2,3,4,5,6,7], 0x0)
        ds.addSegment(seg)
        
        def fakeCallable():
            ds[-1]
        self.assertRaises(KeyError, fakeCallable)
        
        for i in xrange(0,8):
            ds[i]
            
        def fakeCallable():
            ds[8]
        self.assertRaises(KeyError, fakeCallable)
        

    def testUndefine(self):
        ds = DataStore(":memory:")
        seg = Segment([0,1,2,3,4,5,6,7], 0x0)
        ds.addSegment(seg)
        
        undefine(ds, 0)
   
    # Verify that the layoutChanged signal is emitted
    def testAddLayoutChanged(self):
        fired = [False]
        def mockChangeHDLR():
            fired[0] = True

        ds = DataStore(":memory:")
        ds.layoutChanged.connect(mockChangeHDLR)

        seg = Segment([0,1,2,3,4,5,6,7], 0x0)
        ds.addSegment(seg)
        
        self.assertEqual(fired[0], True)

    
    def testCodeFolow(self):
        ds = DataStore(":memory:")
        addBinary(ds, "performance/src/8051_flash_trunc.bin", 0, 0, 0x8000)
        codeFollow(ds, "8051", 0)

    def testCodeFollowCheckCommentLabels(self):
        ds = DataStore(":memory:")
        addBinary(ds, "performance/src/8051_flash_trunc.bin", 0, 0, 0x8000)
        ds.symbols.setSymbol(0x0, "hello")
        ds.comments.setComment(0x0, "blah", CommentPosition.POSITION_RIGHT)
        codeFollow(ds, "8051", 0)

        self.assertEqual(ds.symbols.getSymbol(0x0), "hello")
        self.assertEqual(ds.comments.getCommentText(0x0, CommentPosition.POSITION_RIGHT), "blah")

if __name__ == '__main__':
    unittest.main()
