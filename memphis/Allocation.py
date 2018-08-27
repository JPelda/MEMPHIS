# -*- coding: utf-8 -*-
"""
Created on Wed May  2 11:32:35 2018

@author: jpelda
"""
from osmnx import get_nearest_node
from networkx import get_node_attributes
import shapely.ops


def polys_to_point(gdf_polys, gdf_polys_centroid, gdf_polys_values,
                   gdf_points):
    """Allocates inhabitans to nodes. Nodes in same raster field will get
    raster's inhabitans divided by amout of nodes within raster. Raster
    fields without nodes are allocated to nearest node. Values <= 0 are not
    considered!

    Parameters
    ----------
    gdf_polys : geopandas.GeoDataFrame(shapely.geometry.polygon)
    gdf_polys_centroid : geopandas.GeoDataFrame(shapely.geometry.Point)
    gdf_polys_values : geopandas.GeoDataFrame(int or float)
    gdf_points : geopandas.GeoDataFrame(shapely.geometry.points)


    Returns
    -------
    list(float)
        list of inhabitants in order of gdf_nodes
    """

    gdf_points_sindexed = gdf_points.sindex
    dic = {key: 0 for key in gdf_points.index}
    print(dic.keys())
    pts1 = gdf_points.unary_union

    for i, (geo, poly, value) in enumerate(
                                        zip(gdf_polys_centroid,
                                            gdf_polys,
                                            gdf_polys_values)):
        print("Polys to points, objects left {}".format(len(gdf_polys) - i))
        if value <= 0:
            continue
        else:
            possible_matches_index = list(
                            gdf_points_sindexed.intersection(
                                    poly.bounds))

            if possible_matches_index != []:
                val = value / len(possible_matches_index)
                for key in possible_matches_index:
                    key = gdf_points.index[key]
                    dic[key] += val
            else:
                nearest = gdf_points.geometry ==\
                          shapely.ops.nearest_points(geo, pts1)[1]
                key = gdf_points[nearest].index.values[0]
                dic[key] += value

    list_of_inhabs = [dic[key] for key in gdf_points.index]
    return list_of_inhabs

def alloc_wc_from_b_to_node(gdf_gis_b, gdf_nodes, graph):
    """Allocates the water consumption of each building in GIS-Data to
    nearest node of graph.

    Parameters
    ----------
    gdf_gis_b : geopandas.GeoDataFrame()
        * gdf_gis_b['geometry']: the geometry
        * gdf_gis_b['wc']: the water consumption
        * gdf_gis_b['area']: the area of the building
    graph : nx.Graph()
        edges and nodes from graph of streetnetwork
    Returns
    -------
    list(float)
        list of water consumption of each node in order of gdf_nodes
    """

    dic = {key: 0 for key in gdf_nodes.index}
    geos = gdf_gis_b['SHAPE'][gdf_gis_b['wc'] > 0].centroid
    wc = gdf_gis_b['wc'][gdf_gis_b['wc'] > 0]

    for i, (geo, wc) in enumerate(zip(geos, wc)):
        key = get_nearest_node(graph, (geo.y, geo.x))
        dic[key] += wc

    list_of_wc = [dic[key] for key, item in gdf_nodes.iterrows()]
    return list_of_wc


def points_to_poly(gdf_points, gdf_points_values,
                   gdf_polys, gdf_polys_centroid):
    """Allocates points' values to polygon if point is within polygon. Values
    <= 0 are not considered!
    If there is no unary_union for a gdf than first set the right geometry
    for this gdf --> gdf = gdf.set_geometry()

    Parameters
    ----------
    gdf_points : geopandas.GeoDataFrame(shapely.geometry.points)
    gdf_points_values : geopandas.GeoDataFrame(int / float)
    gdf_polys : geopandas.GeoDataFrame(shapely.geometry.polygons)
    gdf_polys_centroid : geopandas.GeoDataFrame(shapely.geometry.points)

    Returns
    -------
    arr : containing the accumulated values in gdf_polys order
    """

    gdf_points_sindexed = gdf_points.sindex
    dic = {key: 0 for key in gdf_polys.index}
    for i, (index, poly) in enumerate(zip(gdf_polys.index.values, gdf_polys)):
        print("Points to poly, objects left {}".format(len(gdf_polys) - i))

        possible_matches_index = list(gdf_points_sindexed.intersection(
                                      poly.bounds))
        if possible_matches_index != []:
            dic[index] += sum(gdf_points_values.iloc[possible_matches_index])
            gdf_points_values.loc[possible_matches_index] = 0
        if i % 2500 == 0:
            gdf_points_sindexed = gdf_points.loc[gdf_points_values != 0].sindex

    gdf_points = gdf_points.loc[gdf_points_values != 0]
    gdf_points_values = gdf_points_values.loc[gdf_points_values != 0]
    if not gdf_points.empty:
        pts = gdf_polys_centroid.unary_union
        for i, (pt, val) in enumerate(zip(gdf_points, gdf_points_values)):
            print("Points to poly -> nearest_points,"
                  " objects left {}".format(len(gdf_points) - i))
            nearest = gdf_polys_centroid.geometry == \
                      shapely.ops.nearest_points(pt, pts)[1]
            key = gdf_polys[nearest].index.values[0]
            dic[key] += val

    arr = [dic[key] for key in gdf_polys.index]
    return arr

def inhabs_to_area(gdf_gis_b, inhabitants, types):
    """

    Parameters
    ----------
    gdf_gis_b: GeoPandas.GeoDataFrame()
        gdf_gis_b['type'], gdf_gis_b['geometry']
    inhabitants: int
        Overall inhabitants of city
    types: [str]
        All types that are not inhabited.
    Returns
    -------
    gdf
    """

    # gdf['area'] = transform_area(gdf.geometry)

    # sum of all inhabited building areas (example type='none',
    #  type='dormitory'),
    # to calculate the population density by overall_population / sum_inhabs.
    logical = ~gdf_gis_b['type'].isin(types)
    area = sum(gdf_gis_b['area'][logical])

    # average inhabitant per square meter in choosen city
    inhabsperarea = inhabitants / area
    # giving all buildings their amount of inhabitants
    gdf_gis_b['inhabs'] = gdf_gis_b['area'] * logical.astype(int)\
        * inhabsperarea
    print("Distribution of inhabitants: {} [inhabs/m²]".format(inhabsperarea))

    return gdf_gis_b

def nodes_to_node(gdf_nodes, gdf_node, name='inhabs'):
    """
    Allocates nodes of gdf to graph
    Parameters
    ----------
    gdf_nodes : geopandas.GeoDataFrame()
        gdf['SHAPE'] with shapely.geometry.points, gdf[name]
    gdf_node : geopandas.GeoDataFrame()
        gdf['SHAPE'] with shapely.geometry.points
    name : str
        Attribute (float, int) that is allocated and accumulated to graph's
        node
    Returns
    -------
    list of name's values in order or gdf_node
    """
    pts = gdf_nodes.geometry.unary_union
    # gdf_node_spatial_index = gdf_node.sindex
    for i, pt, val in enumerate(gdf_node['SHAPE']):
        print("pts left: {}".format(len(gdf_nodes) - i))
        nearest = gdf_nodes.geometry == shapely.ops.nearest_points(pts, pt)[1]
        gdf_node[name] += gdf_nodes[nearest][name]
        # shapely.ops.
    return list(get_node_attributes(graph, name).values())


def alloc_wc_to_type(gis_cat, gdf_gis_b):
    """Allocates water consumption to types coming from gis_buildings.

    Parameters
    ----------
    gis_cat : pandas.DataFrame()
        * gis_cat['type']: type of GIS-data
        * gis_cat['cat']: category type belongs to
    gdf_gis_b : geopandas.GeoDataFrame()
        * gdf_gis_b['types']: type of building
    Returns
    -------
    list(float)
        the water consumption for each building in gdf_gis_b
    """
    types = gdf_gis_b['type']
    dic = {key: val for key, val in zip(gis_cat['type'],
                                        gis_cat['cmPsma'])}
    arr = [dic[t] if t in dic.keys() else 0 for t in types]

    return arr

