# -*- coding: utf-8 -*-
"""
Created on Wed May  2 11:32:35 2018

@author: jpelda
"""
from osmnx import get_nearest_node


def alloc_inhabs_to_nodes(gdf_raster, gdf_nodes, graph):
    """Allocates inhabitans to nodes. Nodes in same raster field will get
    raster's inhabitans divided by amout of nodes within raster. Raster
    fields without nodes are allocated to nearest node.

    :param geopandas.GeoDataFrame() gdf_raster:
            * gdf['SHAPE']
            * gdf['SHAPE_b']
            * gdf['inhabs']
    :param geopandas.GeoDataFrame() gdf_nodes:
            * gdf['osmid'], gdf['geometry']
    :param nx.Graph() graph:
            * edges and nodes from graph of streetnetwork
    :return:
            * list of inhabitants in order of gdf_nodes
    :rtype: list(float)

    """

    gdf_nodes_spatial_index = gdf_nodes.sindex
    dic = {key: 0 for key in gdf_nodes.index}
    for i, (geo, poly, inhab) in enumerate(
                                        zip(gdf_raster['SHAPE'],
                                            gdf_raster['SHAPE_b'],
                                            gdf_raster['inhabs'])):
        if inhab <= 0:
            continue
        else:
            possible_matches_index = list(
                            gdf_nodes_spatial_index.intersection(
                                    geo.bounds))

            if possible_matches_index != []:
                val = inhab / len(possible_matches_index)
                for key in possible_matches_index:
                    dic[key] += val
            else:
                key = get_nearest_node(graph, (geo.y, geo.x))
                dic[key] += inhab

    list_of_inhabs = [dic[key] for key, item in gdf_nodes.iterrows()]
    return list_of_inhabs


def test():
    """
        Switch minor tick labeling on or off.

        Parameters
        ----------
        labelOnlyBase : bool
            If True, label ticks only at integer powers of base.
        test_test : str
            What else
    """
    pass

def test_google():
    """
        Switch minor tick labeling on or off.

        Args:
        
            labelOnlyBase : bool  
                If True, label ticks only at integer powers of base. und noch ganz viel weiteren Text anfüge was passiert dann mit dem umbruch?
            
            test_test (str) : What else is back
    """
    pass

def alloc_wc_from_b_to_node(gdf_gis_b, gdf_nodes, graph):
    """Allocates the water consumption of each building in GIS-Data to
    nearest node of graph.

    :param geopandas.GeoDataFrame() gdf_gis_b:
            * gdf_gis_b['geometry']: the geometry
            * gdf_gis_b['wc']: the water consumption
            * gdf_gis_b['area']: the area of the building
    :param nx.Graph() graph:
            * edges and nodes from graph of streetnetwork
    :return:
        list of water consumption of each node in order of gdf_nodes
    :rtype: list(float)

    """

    dic = {key: 0 for key in gdf_nodes.index}
    geos = gdf_gis_b['SHAPE'][gdf_gis_b['wc'] > 0].centroid
    wc = gdf_gis_b['wc'][gdf_gis_b['wc'] > 0]

    for i, (geo, wc) in enumerate(zip(geos, wc)):
        key = get_nearest_node(graph, (geo.y, geo.x))
        dic[key] += wc

    list_of_wc = [dic[key] for key, item in gdf_nodes.iterrows()]
    return list_of_wc

def alloc_nodes_to_inhabs(gdf_raster, gdf_nodes):
    """Allocates nodes of gdf to fields of gdf_census.

    :param geopandas.GeoDataFrame() gdf_raster:
            * gdf_raster['inhabs']: the amount of inhabs per geometry
            * gdf_raster['geometry']: the geometry
    :param geopandas.GeoDataFrame() gdf_nodes:
            * gdf_nodes['geometry']: the geometry

    :return:
            * list of inhabitants per node
            * list of raster id
    :rtype: list, list
    """

    gdf_raster_spatial_index = gdf_raster.sindex
    arr = [0] * len(gdf_nodes)
    raster = [0] * len(gdf_nodes)

    for i, geo in enumerate(gdf_nodes['geometry']):

        possible_matches_index = list(
                            gdf_raster_spatial_index.intersection(
                                    geo.bounds))
        possible_matches = gdf_raster.iloc[possible_matches_index]
        precise_matches = possible_matches[
                possible_matches.contains(geo)]
        if not precise_matches.empty:
            arr[i] = precise_matches['inhabs'].values[0]
            raster[i] = precise_matches.index.values[0]
    return arr, raster

def alloc_wc_to_type(gis_cat, gdf_gis_b):
    """Allocates water consumption to types coming from gis_buildings.

    :param pandas.DataFrame() gis_cat:
            * gis_cat['type']: type of GIS-data
            * gis_cat['cat']: category type belongs to
    :param geopandas.GeoDataFrame() gdf_gis_b:
            * gdf_gis_b['types']: type of building
    :return:
            the water consumption for each building in gdf_gis_b
    :rtype: [float]

    """
    types = gdf_gis_b['type']
    dic = {key: val for key, val in zip(gis_cat['type'],
                                        gis_cat['cmPsma'])}
    arr = [dic[t] if t in dic.keys() else 0 for t in types]

    return arr

if __name__ == "__main__":
    pass
else:
    pass
