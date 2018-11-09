# -*- coding: utf-8 -*-
"""
Created on 07.09.2018

@author: jpelda
"""

import os

from Data_IO import Data_IO
from shapely.geometry import Point
import geopandas as gpd

fname_byCensus = 'goettingen.ini'
fname_byCityPop = 'goettingen_censusByCitysPopulation.ini'
path = os.getcwd() + os.sep + 'examples' + os.sep + 'config' + os.sep
config_byCensus = path + fname_byCensus
config_byCityPop = path + fname_byCityPop

center = {'goettingen.ini': Point((9.935007, 51.532762))}
p = center[fname_byCensus]

data_byCensus = Data_IO(config_byCensus)
data_byCityPop = Data_IO(config_byCityPop)

gdf_c = data_byCensus.read_from_shp('paths',
                                    path=data_byCensus.path_export_shp)
gdf_c['CENTROID'] = gdf_c.centroid
gdf_cbc = data_byCityPop.read_from_shp('paths',
                                       path=data_byCityPop.path_export_shp)
gdf_cbc['CENTROID'] = gdf_cbc.centroid

gdf_c['DISTANCE'] = gdf_c.centroid.distance(p)
gdf_cbc['DISTANCE'] = gdf_cbc.centroid.distance(p)

gdf_c = gdf_c.sort_values('DISTANCE')
gdf_cbc = gdf_cbc.sort_values('DISTANCE')

