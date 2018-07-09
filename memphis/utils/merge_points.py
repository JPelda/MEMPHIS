# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 14:25:23 2018

@author: jpelda
"""


def merge_points(list_of_tuples_point_ids, dist, crs="EPSG:4326"):
    """Merges points with distance <dist> to each other into one point.

    Args:
    -----

    list_of_tuples_point_ids: list(tuples(id, shapely.Point((x, y))))
    dist: float[meter]

    Returns:
    --------

    remaining_points: list(tuples(id, shapely.Point((x, y))))

    """

    from transformations_of_crs_values import meter_to_crs_length

    dist = meter_to_crs_length(dist, crs=crs)

    points_f = [p[1] for p in list_of_tuples_point_ids]
    dict_of_points = {}
    #  TODO Try nx.ego_graph() to speed up performance
    for index, point in enumerate(list_of_tuples_point_ids):
        points_near = [p for p in points_f if p.distance(point[1]) <=
                       dist]
        dict_of_points[index] = points_near
        points_f = [p for p in points_f if p not in points_near]
        print(index)

    arr = []
    for key in dict_of_points.keys():
        for value in dict_of_points[key]:
            if value != []:
                arr.append([list_of_tuples_point_ids[key][0],
                            list_of_tuples_point_ids[key][1]])

    return arr

#from shapely.geometry import Point
#import numpy as np
#plist = [('a', Point((1,1))),
#         ('b', Point((0,0))),
#         ('c', Point((3,3))),
#         ('d', Point((4,4))),
#         ('e', Point((9,9)))]
#
#
#arr = merge_points(plist, 1, crs='EPSG:32633')
#
#
#import geopandas as gpd
#import matplotlib.pyplot as plt
#fig = plt.figure()
#ax = fig.add_subplot(111)
#
#df = gpd.GeoDataFrame(arr, columns=['key', 'SHAPE'], geometry='SHAPE')
##df_f = gpd.GeoDataFrame(
#print(df)
##gis_gdf.plot(ax=ax, color='black', linewidth=0.3, alpha=1)
#df.plot(ax=ax, color='red')
