# -*- coding: utf-8 -*-
"""
Created on Wed May  2 14:27:46 2018

@author: jpelda
"""


def sum_wc(gdf):
    """Accumulates the paths' water flows that pass along each node.

    Args:
    -----
    gdf: geopandas.GeoDataFrame()
        gdf['wc'], gdf['path_to_end_node']

    Returns:
    --------
    list_of_sum_wc: list(floats)
        List of floats is in order of gdf_nodes
    """

    dic = {key: 0 for key in gdf.index}

    for node_list, wc in zip(gdf.path_to_end_node, gdf.wc):
        for key in node_list:
            dic[key] += wc

    arr = [x for x in dic.values()]
    return arr
