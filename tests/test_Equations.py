# -*- coding: utf-8 -*-
"""
Created on Tue May 29 17:04:00 2018

@author: jpelda
"""

import sys
import os
import unittest
from shapely.geometry import Polygon, Point
import geopandas as gpd
import numpy as np
from copy import copy

sys.path.append(os.path.dirname(os.getcwd()) + os.sep + 'src' + os.sep +
                'utils')
import Conversion as conv
import Allocation as alloc

class TestConversions(unittest.TestCase):

    def test_DN_to_V(self):
        self.assertListEqual(list(conv.DN_to_V({'DN': [0.3, 2],
                                                's_height': [4, 142.62],
                                                'e_height': [1., 142],
                                                'length': [1000, 1.266]})),
                             [0.053438630226139136, 101.73312110457051])

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')


class TestAllocation(unittest.TestCase):
    def setUp(self):
        self.poly1 = Polygon(((1, 1), (2.5, 1), (3.5, 3), (1, 3), (1, 1)))
        self.poly2 = Polygon(((4, 4), (5, 4), (5, 5), (4, 5), (4, 4)))
        self.point1 = Point((0.5, 2))
        self.point2 = Point((2, 1.5))
        self.point3 = Point((3.5, 3))
        self.point4 = Point((1.5, 1))
        self.point5 = Point((7, 9))

        self.gdf_polys = gpd.GeoDataFrame([self.poly1, self.poly2],
                                           columns=['SHAPE_b'],
                                           geometry='SHAPE_b')
        self.gdf_polys_centroid = self.gdf_polys['SHAPE_b'].centroid
        self.gdf_polys['values'] = np.array([6, 5])
        self.gdf_points = gpd.GeoDataFrame([self.point1, self.point2,
                                            self.point3, self.point4,
                                            self.point5],
                                            columns=['SHAPE'],
                                            geometry='SHAPE')
        self.gdf_points['values'] = [1, 2, 3, 4, 5]


    def test_polys_to_point(self):
        arr = alloc.polys_to_point(self.gdf_polys['SHAPE_b'],
                                   self.gdf_polys_centroid,
                                   self.gdf_polys['values'],
                                   self.gdf_points)
        results = [0, 2, 7, 2, 0]
        self.assertListEqual(arr, results)

    def test_points_to_poly(self):
        arr = alloc.points_to_poly(self.gdf_points['SHAPE'],
                                   self.gdf_points['values'],
                                   self.gdf_polys['SHAPE_b'],
                                   self.gdf_polys_centroid)
        results = [10, 5]
        self.assertListEqual(arr, results)



if __name__ == "__main__":

    testconversions = unittest.TestLoader().loadTestsFromTestCase(
        TestConversions)
    testallocation = unittest.TestLoader().loadTestsFromTestCase(
        TestAllocation)

    unittest.TextTestRunner(verbosity=2).run(testconversions)
    unittest.TextTestRunner(verbosity=2).run(testallocation)
else:
    pass
