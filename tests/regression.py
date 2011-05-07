import unittest
from datastore import DataStore, CommentPosition


class undoPopEmptyStack(unittest.TestCase):
    # Check for regression on undo'ing an empty undo-stack
    def testUndoPopOnEmpty(self):
        self.ds = DataStore(":memory:")
        self.ds.cmdlist.rewind(1)

suite = unittest.TestSuite([
    unittest.TestLoader().loadTestsFromTestCase(undoPopEmptyStack)
    ])
