# -*- coding: utf-8 -*-
"""
Created on Wed May  2 11:32:35 2018

@author: jpelda
"""
from osmnx import get_nearest_node
from networkx import get_node_attributes
import shapely.ops
import geopandas as gpd
import pandas as pd
import numpy as np
import time

def polys_to_point(gdf_polys, gdf_points, col):
    """Allocates values of col of polygons to nodes.
    Points in same polygon will get value divided by amout of points within
    raster. Polygons without points are allocated to nearest points.

    Parameters
    ----------
    gdf_polys : geopandas.GeoDataFrame()
        *gdf_polys['SHAPE'] as geometry and shapely.geometry.polygon
        *gdf_polys['CENTROID'], gdf_polys[col]
    gdf_points : gpd.GeoDataFrame()
        gdf_points['SHAPE'] as geometry and shapely.geometry.point
    col: str
        Name of column with values

    Returns
    -------
    list(float)
        list of inhabitants in order of gdf_points
    """

    df = pd.DataFrame(0, index=gdf_points.index, columns=['results'])
    gdf_res = gpd.sjoin(gdf_polys, gdf_points, op='intersects', how='right')

    polys_left = gdf_polys.drop(set(
        gdf_res.index_left[gdf_res.index_left.notnull()]))

    # finds mean value for the polygon which gets the values from points.
    counts = gdf_res['index_left'].value_counts(sort=False, dropna=False)
    factor = np.repeat(counts.values, counts.values)
    values = gdf_res[col] / factor

    df.loc[gdf_res.index, 'results'] += values
    df['results'] = df['results'].fillna(0)

    if not polys_left.empty:
        d = {key: 0 for key in gdf_points.index}
        ptsofpoints = gdf_points.centroid.unary_union

        pts = polys_left['CENTROID'].values
        pts_val = polys_left[col].values

        pts_test = gdf_points.centroid.values
        pts_test = np.array([(p.x, p.y) for p in pts_test])

        for i, (pt, val) in enumerate(zip(pts, pts_val)):
            print("Poly to points -> nearest_points,"
                  " objects left {}".format(len(pts) - i))
            # stime = time.time()
            # nearest = gdf_points.geometry == \
            #           shapely.ops.nearest_points(pt, ptsofpoints)[1]
            # key = gdf_points[nearest].index.values[0]
            # d[key] += val
            # print(key)
            # print(time.time() - stime)
            # stime = time.time()
            nearest = closest_node(pt, pts_test)
            key = gdf_points.index[nearest]
            d[key] += val
            # print(nearest)
            # print(time.time() -stime)

        df.loc[d.keys(), 'results'] += list(d.values())

    return df.values

def closest_node(point, points):
    """

    Parameters
    ----------
    point
    points : array()

    Returns
    -------
    index : int
    """
    deltas = points - point
    dist_2 = np.einsum('ij,ij->i', deltas, deltas)

    return np.argmin(dist_2)

def alloc_wc_from_b_to_node(gdf_gis_b, gdf_nodes, graph):
    """Allocates the water consumption of each building in GIS-Data to
    nearest node of graph.

    Parameters
    ----------
    gdf_gis_b : geopandas.GeoDataFrame()
        * gdf_gis_b['CENTROID']: the geometry
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
    geos = gdf_gis_b['CENTROID'][gdf_gis_b['wc'] > 0]
    wc = gdf_gis_b['wc'][gdf_gis_b['wc'] > 0]

    for i, (geo, wc) in enumerate(zip(geos, wc)):
        key = get_nearest_node(graph, (geo.y, geo.x))
        dic[key] += wc

    list_of_wc = [dic[key] for key, item in gdf_nodes.iterrows()]
    return list_of_wc


def points_to_poly(gdf_points, gdf_polys, col):
    """Allocates points' values to polygon if point is within polygon. Values
    <= 0 are not considered!
    If there is no unary_union for a gdf than first set the right geometry
    for this gdf --> gdf = gdf.set_geometry()

    Parameters
    ----------
    gdf_points : geopandas.GeoDataFrame()
        * gdf_points['geometry']  as shapely.geometry.Points set as geometry
        * gdf_points[col]
    gdf_polys : geopandas.GeoDataFrame()
        * gdf_polys['SHAPE'] as shapely.geometry.polygons set as geometry,
        * gdf_polys['CENTROID']
    col : str
        column name of values which will be transfered to polygon
    Returns
    -------
    arr : containing the accumulated values in gdf_polys order
    """

    df = pd.DataFrame(0, index=gdf_polys.index, columns=['results'])
    gdf_res = gpd.sjoin(gdf_points, gdf_polys, op='intersects', how='right')

    pts_left = gdf_points.drop(set(
        gdf_res.index_left[gdf_res.index_left.notnull()]))

    if not pts_left.empty:
        d = {key: 0 for key in gdf_polys.index}
        ptsofpoly = gdf_polys.centroid.unary_union
        pts = pts_left.geometry.values
        pts_val = pts_left[col].values
        for i, (pt, val) in enumerate(zip(pts, pts_val)):
            print("Points to poly -> nearest_points,"
                  " objects left {}".format(len(pts) - i))
            nearest = gdf_polys.centroid == \
                                shapely.ops.nearest_points(pt, ptsofpoly)[1]

            key = gdf_polys[nearest].index.values[0]
            d[key] += val

        df.loc[d.keys(), 'results'] += list(d.values())

    gdf_res = gdf_res.groupby('index_right')[col].sum()
    df.loc[gdf_res.index, 'results'] += gdf_res.values

    return df.values


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

#TODO can this be transformed to points_to_poly?
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

