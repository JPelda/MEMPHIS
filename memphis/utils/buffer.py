# -*- coding: utf-8 -*-
"""
Created on Wed May  2 10:35:46 2018

@author: jpelda
"""
from shapely.geometry import Polygon


def buffer(gdf, x_min, x_max, y_min, y_max, factor=1.9):
    """Creates buffer around points. Buffer is rectangle with x == length of
    map divided by amounts of points in x-direction and y = length of map
    divided by amounts of poitns in y direction. CRS is variable.

    ARGS:
    -----
    gdf : geopandas.GeoDataFrame()
        gdf['len_x'], gdf['len_y'], gdf['CENTROID']
    x_max : float
        length of map in x direction
    y_max : float
        length of map in y direction

    KWARGS:
    -------
        factor : float
        Defines the boarder around each rectangle by
        (rectangle's width)/ factor

    RETURNS:
    -------
    polygons : list
        polygons of shape rectangle
    """

    gdf_length_x = gdf['len_x'][0]
    gdf_length_y = gdf['len_y'][0]
    gdf_x_length = x_max - x_min
    gdf_y_length = y_max - y_min

    factor = factor
    delta = gdf_x_length / gdf_length_x
    border = delta / factor
    delta_x = gdf_x_length / gdf_length_x - border
    # delta = gdf_y_length / gdf_length_y
    # border = delta / factor
    delta_y = gdf_y_length / gdf_length_y - border

    geo = [Polygon(((point.x - delta_x, point.y - delta_y),
                    (point.x + delta_x, point.y - delta_y),
                    (point.x + delta_x, point.y + delta_y),
                    (point.x - delta_x, point.y + delta_y),
                    (point.x - delta_x, point.y - delta_y))) for
           point in gdf['CENTROID']]

    return geo
