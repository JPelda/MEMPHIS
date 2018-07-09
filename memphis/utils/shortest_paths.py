# -*- coding: utf-8 -*-
"""
Created on Mon May 28 14:55:03 2018

@author: jpelda
"""
import networkx as nx


def shortest_paths(graph, gdf, end_node):
    """Finds shortest paths from many start points to one end point, if gdf.wc
       is not 0.

    Args:
    -----
    graph : networkx.Graph()
        The graph for which the shortest paths are calculated.
    gdf : geopandas.DataFrame()
        gdf.wc shows if path is calculated, if gdf.wc == 0 path is not calc.
    end_node : int
         Node number to which path is calculated to.

    Returns:
    --------
    dic.values() : giving all paths for each gdf

    """
    gdf['path_to_end_node'] = None
    dic = {x: None for x in gdf.index}

    for m, (index, row) in enumerate(gdf.iterrows()):

        if row.wc != 0:

            values = dic[index]

            if values is None:

                print("\rLeft:{:>10}".format(len(gdf) - m), end='')

                try:
                    values =\
                        nx.shortest_path(graph, index,
                                         end_node, weight='length')
                    for i, n in enumerate(values):
                        dic[n] = values[i:]

                except nx.NetworkXNoPath:
                    print("\nNo path between {} and wastewater"
                          "treatment plant with node {}".format(index,
                                                                end_node))
                    dic[index] = []

        else:
            dic[index] = []
    return dic.values()
