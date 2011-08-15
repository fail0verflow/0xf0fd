#!/usr/bin/python

import unittest

import tests.segment
import tests.some_ds_tests
import tests.regression
import tests.packing


alltests = unittest.TestSuite([tests.segment.suite,
    tests.some_ds_tests.suite, tests.regression.suite,
    tests.packing.suite])

if __name__ == '__main__':
    r = unittest.TextTestRunner(verbosity=2).run(alltests)
    if r.failures:
        exit(1)
