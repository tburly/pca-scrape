#!/usr/bin/env python3

"""

    Script for running all testing modules.

"""

import unittest

import tests.test_pca as tp

loader, suite = unittest.TestLoader(), unittest.TestSuite()

# bundle up all test modules
suite.addTests(loader.loadTestsFromModule(tp))
# suite.addTests(loader.loadTestsFromModule(tpm))

# run the suite
result = unittest.TextTestRunner(verbosity=2).run(suite)
