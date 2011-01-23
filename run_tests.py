#!/usr/bin/python

import unittest

import tests.segment
import tests.some_ds_tests

alltests = unittest.TestSuite([tests.segment.suite, tests.some_ds_tests.suite])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(alltests) 
