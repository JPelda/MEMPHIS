# -*- coding: utf-8 -*-
"""
Created on Wed May  2 11:32:35 2018

@author: jpelda
"""
from osmnx import get_nearest_node


class Allocation:

    def __init__(self):
        pass

    def alloc_inhabs_to_nodes(self, gdf_raster, gdf_nodes, graph):
        """Allocates inhabitans to nodes. Nodes in same raster field will get
        raster's inhabitans divided by amout of nodes within raster. Raster
        fields without nodes are allocated to nearest node.

        Args:
        gdf_raster(geopandas.GeoDataFrame()):
            gdf['SHAPE'], gdf['SHAPE_b'], gdf['inhabs']
        gdf_nodes : geopandas.GeoDataFrame()
            gdf['osmid'], gdf['geometry']
        graph : nx.Graph()

        RETURNS:
        --------
        list_of_inhabs : list(floats)
            List of floats is in order of gdf_nodes
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

    def alloc_wc_from_b_to_node(self, gdf_gis_b, gdf_nodes, graph):
        """Allocates the water consumption of each building in GIS-Data to
        nearest node of graph.

        ARGS:
        ----
        gdf_gis_b : geopandas.GeoDataFrame()
            gdf['geometry'], gdf['wc'], gdf['area']
        graph : nx.Graph()

        RETURNS:
        -------
        list_of_wc : list(floats)
            List of floats is in order of gdf_nodes of graph
        """

        dic = {key: 0 for key in gdf_nodes.index}
        geos = gdf_gis_b['SHAPE'][gdf_gis_b['wc'] > 0].centroid
        wc = gdf_gis_b['wc'][gdf_gis_b['wc'] > 0]

        for i, (geo, wc) in enumerate(zip(geos, wc)):
            key = get_nearest_node(graph, (geo.y, geo.x))
            dic[key] += wc

        list_of_wc = [dic[key] for key, item in gdf_nodes.iterrows()]
        return list_of_wc

    def alloc_nodes_to_inhabs(self, gdf_raster, gdf_nodes):
        """Allocates points of gdf to fields of gdf_census.

        ARGS:
        -----
        gdf_raster : geopandas.GeoDataFrame()
            gdf_raster['inhabs']
        gdf_nodes : geopandas.GeoDataFrame()
            gdf_nodes['geometry'].boundary

        RETURNS:
        --------
        list_of_inhabs : list(floats)
            List of floats is in order of gdf_nodes
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

    def alloc_wc_to_type(self, gis_cat, types):
        """Allocates waste consumption to types coming from gis_builings.

        ARGS:
        -----
        gis_cat : pandas.DataFrame()
            gis_cat['type'], gis_cat['cat']
        types : [str]
            Types to which wc is allocated. Types are found in gis_cat['type']

        RETURNS:
        -------
        wc : [float]
            Returns the water consumption for each type in types.
        """

        dic = {key: val for key, val in zip(gis_cat['type'],
                                            gis_cat['cmPsma'])}
        arr = [dic[t] if t in dic.keys() else 0 for t in types]

        return arr
