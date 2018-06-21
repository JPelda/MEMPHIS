# -*- coding: utf-8 -*-
"""
Created on Wed May  2 17:42:14 2018

@author: jpelda
"""


def paths_to_dataframe(gdf_nodes, gdf_edges):
    """Brings all paths to dataframe with values of edges

    Args:
    -----
    gdf_nodes: geopandas.GeoDataFrame()
        gdf_nodes['path_to_end_node']
    gdf_edges: geopandas.GeoDataFrame()
        gdf_edges['u'], gdf_edges['v']

    Returns:
    --------
    gdf: geopandas.GeoDataFrame()
        gdf contains all information of gdf_edges and only edges according
        to gdf_nodes['path_to_end_node'] with flow direction u -> v and its
        volume stream.
    """

    # Forms a list of tuple from odd or uneven list.
    uv = [(x, arr[i+1]) if i < len(arr) - 1 else () for arr in
          gdf_nodes.path_to_end_node for i, x in enumerate(arr)]
    uv = set(uv)

    arr = []
    list_V = []
    for index, u, v in zip(gdf_edges.index, gdf_edges.u, gdf_edges.v):
        uv_item = (u, v)
        vu_item = (v, u)

        for vec in uv:
            if vec == uv_item:
                arr.append(index)
                list_V.append(gdf_nodes.V[u])
                uv.remove(vec)
                break
            elif vec == vu_item:
                arr.append(index)
                list_V.append(gdf_nodes.V[v])
                uv.remove(vec)
                break

    gdf = gdf_edges.iloc[arr].copy()
    gdf['V'] = list_V
    return gdf
