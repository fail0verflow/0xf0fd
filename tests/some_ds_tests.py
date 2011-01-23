import unittest
from idis.datastore import DataStore
from idis.dbtypes import CommentPosition
from idis.tools import *


class miscTestCases(unittest.TestCase):

    def test_notInDS(self):
        ds = DataStore(":memory:")
        self.assertEqual(False, 0 in ds)
        self.assertEqual(False, 1 in ds)
        self.assertEqual(False, -1 in ds)

    def test_inBasicDS(self):
        ds = DataStore(":memory:")
        data = [0,1,2,3,4,5,6,7]
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

    def test_inBasicDS2(self):
        ds = DataStore(":memory:")
        
        data = [0,1,2,3,4,5,6,7]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        def fakeCallable():
            ds[-1]
        self.assertRaises(KeyError, fakeCallable)
        
        for i in xrange(0,8):
            ds[i]
            
        def fakeCallable():
            ds[8]
        self.assertRaises(KeyError, fakeCallable)
    
    def test_inBasicDS3(self):
        ds = DataStore(":memory:")
        
        data = [0,1,2,3,4,5,6,7]
        data2 = map(lambda x: x+10, data)

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
        ds[addr+1]

    def testUndefine(self):
        ds = DataStore(":memory:")
        
        data = [0,1,2,3,4,5,6,7]
        ds.segments.addSegment(0x0, len(data), "ROM", data)

        undefine(ds, 0)
   
 

    
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

suite = unittest.TestLoader().loadTestsFromTestCase(miscTestCases)
