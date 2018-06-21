# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 14:47:54 2018

@author: adifischerson
"""


import pandas as pd
import pyproj as pp
from osgeo import ogr
from osgeo import osr
import osgeo
import shapely

class Conditioning:
    def __init__(self, df):
        self.df = df

#    def read_polygon_from_shp(self, shapefile):
#        #TODO read buildingsshp(shapefile, fiona, or ogr)of bbox selection
#        pass

    def get_centroid(self, df):
        # TODO calculate centroid from polygon
        # gets polygons
        # returns centroids as df dataframe
        return df



    def best_way_calculation(self):
        # TODO wighted graph ways + nodes find shortest way (ask Script Pascal)
        pass



if __name__ == "__main__":
    from Data_IO import Data_IO
    import os

    config = os.path.dirname(os.getcwd()) + os.sep +\
            'config' + os.sep + 'test_config.ini'
    Data = Data_IO(config)

    gis = Data.read_from_sqlServer('gis')
    
    census = Data.read_from_sqlServer('census')
    print(df.keys())
    Cond = Conditioning()
    Cond.transform_coords(['x','y'])

else:
    pass
