# -*- coding: utf-8 -*-
"""
Created on Tue May 29 17:04:00 2018

@author: jpelda
"""

import sys
import os
import unittest
import numpy as np

sys.path.append(os.path.dirname(os.getcwd()) + os.sep + 'src' + os.sep +
                'utils')
from Equations import Conversions


class Test_Conversions(unittest.TestCase):

    def test_DN_to_V(self):
        conv = Conversions()
        self.assertListEqual(list(conv.DN_to_V({'DN': [0.3, 2],
                                                's_height': [4, 142.62],
                                                'e_height': [1., 142],
                                                'length': [1000, 1.266]})),
                             [0.053438630226139136, 101.73312110457051])

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')


if __name__ == "__main__":

    suite = unittest.TestLoader().loadTestsFromTestCase(Test_Conversions)
    unittest.TextTestRunner(verbosity=2).run(suite)

else:
    pass
