# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:36:21 2018

@author: jpelda
"""

import os
import sys

import time
import geopandas as gpd

import osmnx
import numpy as np
from shapely.geometry import MultiPoint, Point, Polygon

path = os.getcwd()
sys.path.append(path + os.sep + 'memphis')
sys.path.append(path + os.sep + 'memphis' + os.sep + 'utils')

from Data_IO import Data_IO
import Allocation as alloc
from transformations_of_crs_values import transform_coords, transform_length,\
                                          transform_area
from buffer import buffer
from accumulate_val_along_path import sum_wc
from paths_to_dataframe import paths_to_dataframe
from shortest_paths import shortest_paths
from import_sewnet import import_sewagenetwork
import dictionary as dic
import Conversion as conv
import Evaluation as evalu
import Visualisation as vis


#########################################################################
# LOAD DATA
#########################################################################
print("load data")
s_time = time.time()

Data = Data_IO(path + os.sep + 'examples' + os.sep + 'config' +
               os.sep + 'goettingen.ini')

graph = Data.read_from_graphml('graph')
gdf_nodes, gdf_edges = osmnx.save_load.graph_to_gdfs(graph, nodes=True,
                                                     edges=True,
                                                     node_geometry=True,
                                                     fill_edge_geometry=True)
gdf_nodes.crs = Data.coord_system
gdf_edges.crs = Data.coord_system

stime = time.time()
gis_r = Data.read_from_sqlServer('gis_roads')
gdf_gis_r = gpd.GeoDataFrame(gis_r, crs=Data.coord_system, geometry='SHAPE')
print("gis_r | {}".format(time.time() - stime))

stime = time.time()
gis_b = Data.read_from_sqlServer('gis_buildings')
gdf_gis_b = gpd.GeoDataFrame(gis_b, crs=Data.coord_system, geometry='SHAPE')
gdf_gis_b['CENTROID'] = gdf_gis_b['SHAPE'].centroid
print("gis_b | {}".format(time.time() - stime))

stime = time.time()
gis_cat = Data.read_from_sqlServer('gis_categories')
gis_cat['cmPsma'] = gis_cat['cmPsma'].str.replace(',', '.')
gis_cat = gis_cat[gis_cat['cmPsma'] != '']
gis_cat = gis_cat[gis_cat['cmPsma'] != '?']
gis_cat['cmPsma'] = gis_cat['cmPsma'].astype(float)
print("gis_cat | {}".format(time.time() - stime))

gdf_gis_b['area'] = transform_area(gdf_gis_b.geometry)
gdf_gis_b['wc'] = alloc.alloc_wc_to_type(gis_cat, gdf_gis_b) *\
                    gdf_gis_b['area'] / (8760 * 3600)

wc = Data.read_from_sqlServer('wc_per_inhab')
wc = wc.drop(0)
wc['cmPERpTIMESh'] = wc['lPERpTIMESd'].astype(float) / 1000 / (24 * 3600)

if Data.census != 'None':
    census = Data.read_from_sqlServer('census')
    gdf_census = gpd.GeoDataFrame(census, crs=Data.coord_system,
                                  geometry='SHAPE')
    gdf_census['CENTROID'] = gdf_census['SHAPE']
    gdf_census['SHAPE'] = buffer(gdf_census, Data.x_min, Data.x_max,
                                 Data.y_min, Data.y_max)
    gdf_census['inhabs'][gdf_census['inhabs'] < 0] = 0
    print("gdf_census 1 | {}".format(gdf_census.inhabs[
                                         gdf_census.inhabs > 0].sum()))
else:
    points = [Point(graph.nodes[key]['x'], graph.nodes[key]['y']) for key in
              graph.nodes.keys()]
    mpoints = MultiPoint(points)
    bounds = mpoints.bounds
    poly = osmnx.bbox_to_poly(bounds[3], bounds[1], bounds[0], bounds[2])

    length = transform_length(100, crs_from=Data.coord_system_raster,
                              crs_into=Data.coord_system)
    x_points = np.linspace(Data.x_min, Data.x_max,
                           num=int((Data.x_max - Data.x_min) / length))
    y_points = np.linspace(Data.y_min, Data.y_max,
                           num=int((Data.y_max - Data.y_min) / length))
    pts = [Point(x, y) for x in x_points for y in y_points]

    gdf_census = gpd.GeoDataFrame(pts, columns=['CENTROID'],
                                  geometry='CENTROID',
                                  crs=Data.coord_system)
    gdf_census['x_mp_100m'] = np.repeat(x_points, len(y_points))
    gdf_census['y_mp_100m'] = np.repeat(y_points, len(x_points))
    gdf_census['len_x'] = len(x_points)
    gdf_census['len_y'] = len(y_points)
    gdf_census['SHAPE'] = buffer(gdf_census, Data.x_min, Data.x_max,
                                 Data.y_min, Data.y_max, factor=2)

    if Data.census == 'None' and Data.districts == 'None':
        print("Census will be calculated by city's inhabitants and distribution of"
              "houses' area")

        gdf_gis_b = alloc.inhabs_to_area(gdf_gis_b, Data.inhabs, dic.types['all'])

        # gdf_census['inhabs'] = alloc.points_to_poly(gdf_gis_b.centroid,
        #                                             gdf_gis_b.inhabs,
        #                                             c_sb['SHAPE_b'],
        #                                             gdf_census['SHAPE'])
        gdf_gis_b = gdf_gis_b.set_geometry('CENTROID')
        gdf_census = gdf_census.set_geometry('SHAPE')
        gdf_census['inhabs'] = alloc.points_to_poly(gdf_gis_b,
                                                    gdf_census, 'inhabs')
    elif Data.districts != 'None':
        print("Census will be calculated by city districts' inhabitants and"
              " distribution of houses' area")
        districts = Data.read_from_sqlServer('districts')
        gdf_districts = gpd.GeoDataFrame(districts, crs=Data.coord_system,
                                         geometry='SHAPE')
        gdf_census['inhabs'] = alloc.polys_to_point(gdf_districts,
                                                    gdf_census, 'inhabs')
        gdf_census = gdf_census.set_geometry('SHAPE')
    print("gdf_census 1 | {}".format(gdf_census.inhabs[
                                         gdf_census.inhabs > 0].sum()))


pipes_table = Data.read_from_sqlServer('pipes_dn_a_v_v')
pipes_table['V'] = pipes_table['V'] / 1000
pipes_table = {DN: {'A': A, 'v': v, 'V': V} for DN, A, v, V in
               zip(pipes_table.DN, pipes_table.A,
                   pipes_table.v, pipes_table.V)}

gdf_sewnet = gpd.GeoDataFrame()
if Data.sewage_network != 'None':
    sew_net = import_sewagenetwork(Data)
    sew_net['V'] = conv.DN_to_V(sew_net)
    gdf_sewnet = gpd.GeoDataFrame(sew_net, crs=Data.coord_system,
                                  geometry='SHAPE')

#########################################################################
# C O N D I T I O N I N G
#########################################################################
print('conditioning')

# Builds buffer around points of census.
stime = time.time()

print("buffer | {}".format(time.time() - stime))

if Data.sewage_network != 'None':
    geo0 = [x[0] for x in gdf_sewnet['SHAPE'].boundary]
    geo1 = [x[1] for x in gdf_sewnet['SHAPE'].boundary]
    mpt = MultiPoint(geo0 + geo1)
    convex_hull = mpt.convex_hull
    gdf_census = gdf_census[gdf_census.within(convex_hull)]
    gdf_gis_r = gdf_gis_r[gdf_gis_r.within(convex_hull)]
    gdf_gis_b = gdf_gis_b[gdf_gis_b.within(convex_hull)]

#########################################################################
# A L L O C A T I O N
#########################################################################

# Allocates inhabitans of census to nodes of graph and multiplies them by
# water consumption of previous specified country.

print('allocation')

stime = time.time()
gdf_census = gdf_census.set_geometry('SHAPE')
# gdf_nodes['inhabs'] = alloc.polys_to_point(gdf_census['SHAPE'],
#                                            gdf_census['CENTROID'],
#                                            gdf_census['inhabs'],
#                                            gdf_nodes['geometry'])
gdf_nodes['inhabs'] = alloc.polys_to_point(gdf_census, gdf_nodes, 'inhabs')

print("alloc_inhabs_to_nodes | {}".format(time.time() - stime))

# if Data.census != 'None':
#     stime = time.time()
#     gdf_nodes['inhabs'] = alloc.polys_to_node(gdf_census, gdf_nodes, graph,
#                                               'inhabs')
#     print("alloc_inhabs_to_nodes | {}".format(stime - time.time()))
# else:
#     stime = time.time()
#     res = alloc.nodes_to_node(gdf_census, graph)
#     gdf_nodes['inhabs'] = res
#     print("nodes_to_nodes | {}".format(stime - time.time()))


gdf_nodes['wc'] = gdf_nodes['inhabs'] *\
                         wc[wc.country_l ==
                            Data.country].cmPERpTIMESh.item() * 1.6
stime = time.time()
gdf_nodes['wc'] += alloc.alloc_wc_from_b_to_node(gdf_gis_b, gdf_nodes, graph)
print("alloc_wc_from_b_to_node | {}".format(time.time() - stime))
# Sets node of graph that is nearest to waste water treatment plant and
# calculates paths from nodes where nodes['inhabs'] > 0.
end_nodes = [osmnx.get_nearest_node(graph, (pt.y, pt.x)) for pt in Data.wwtp]
paths = [0] * len(end_nodes)
lengths = np.array([[0] * len(gdf_nodes)] * len(end_nodes))
for i, enode in enumerate(end_nodes):
    print("Calculate paths to {}. wwtp".format(i + 1))
    paths[i] = list(shortest_paths(graph, gdf_nodes, enode))
    for j, path in enumerate(paths[i]):
        lengths[i][j] = sum([graph[path[k]][path[k + 1]][0]['length'] for
                            k, u in enumerate(path) if k + 1 < len(path)])

    # dists[index] = [graph.edges[list(test)[1][i],
    #                 list(test)[1][i + 1], 0]['length'] for
    #                 n in list(test) for i, u in enumerate(n) if
    #                 i + 1 < len(list(test)[1])]
idx = np.argmin(lengths, axis=0)
path_to_end_node = [0] * len(gdf_nodes)
for i, _ in enumerate(path_to_end_node):
    path_to_end_node[i] = paths[idx[i]][i]

gdf_nodes['path_to_end_node'] = path_to_end_node

# Accumulates wc along each path.
gdf_nodes['V'] = sum_wc(gdf_nodes)

# Generates GeoDataFrame from all paths with its attributes. Introduces the
# waterflow for each path by respecting the flow direction.
gdf_paths = paths_to_dataframe(gdf_nodes, gdf_edges)
pipes_table_V_to_DN = {val['V']: key for key, val in
                       zip(pipes_table.keys(), pipes_table.values())}
DN = np.array(list(pipes_table_V_to_DN.values()))
V_key = np.array(list(pipes_table_V_to_DN.keys()))
arr = [DN[np.where(V_key - V >= 0)[0][0]] if np.any(V_key - V > 0) else
       DN[-1] for V in gdf_paths['V']]
gdf_paths['DN'] = arr


##########################################################################
# E V A L U A T I O N
##########################################################################
print('\nevaluation')

if Data.sewage_network != 'None':
    boxplot_V_over_V_pat, boxplot_length_over_V_pat,\
    boxplot_length_over_V_sew, dis_sew_in_inh, dis_pat_in_inh,\
    dis_cen_in_inh = evalu.memphis_vs_sewagenetwork(Data, gdf_sewnet,
                                                    gdf_paths, gdf_census)

#########################################################################
# V I S U A L I S A T I O N
#########################################################################
print('\nvisualisation')

if Data.sewage_network != 'None':
    vis.memphis_vs_sewagenetwork(Data, gdf_gis_b, gdf_gis_r, gdf_census,
                                 gdf_sewnet, gdf_paths, boxplot_V_over_V_pat,
                                 boxplot_length_over_V_pat,
                                 boxplot_length_over_V_sew, dis_sew_in_inh,
                                 dis_pat_in_inh, dis_cen_in_inh, area=
                                 Data.partial_map)
else:
    vis.memphis(Data, gdf_gis_b, gdf_gis_r, gdf_census, gdf_paths, area=
                Data.partial_map)
##########################
# SAVE
##########################
path_export_shp = os.sep + 'shp' + os.sep

gdf_census_copy = gdf_census.copy()
del gdf_census_copy['CENTROID']
Data.write_gdf_to_file(gdf_census_copy, 'census.shp')

gdf_gis_b_copy = gdf_gis_b.copy()
del gdf_gis_b_copy['CENTROID']
gdf_gis_b_copy = gdf_gis_b_copy.set_geometry('SHAPE')
Data.write_gdf_to_file(gdf_gis_b_copy, 'gis_b.shp')
Data.write_gdf_to_file(gdf_gis_r, 'gis_r.shp')

gdf_paths_copy = gdf_paths.copy()
for key in gdf_paths_copy.keys():
    if key not in ['geometry', 'osmid', 'u', 'v', 'V', 'DN']:
        del gdf_paths_copy[key]
gdf_paths_copy['osmid'] = [str(x) for x in gdf_paths_copy['osmid']]
Data.write_gdf_to_file(gdf_paths_copy, 'paths.shp')

# del gdf_sewnet['geometry_b']
# gdf_sewnet = gdf_sewnet.set_geometry('SHAPE')
# Data.write_gdf_to_file(gdf_sewnet, 'shp' + os.sep + 'sewnet.shp')

# Data.write_to_sqlServer('raster_visual', raster)
# Data.write_to_sqlServer('gis_visual', gis_gdf, dtype=)

# Data.write_to_sqlServer('raster_visual', raster, dtype={
#        'SHAPE':'GEOMETRY', 'inhabitans':'int'})

# folder = os.getcwd() + os.sep + 'input'
# osmnx.save_load.save_graph_shapefile(graph,'goettingen_graph',
# folder + os.sep)
# osmnx.save_load.save_gdf_shapefile(gdf_nodes, 'goettingen_graph', folder +
#                                   os.sep + 'goettingen_graph')
# osmnx.save_load.save_gdf_shapefile(gdf_edges, 'goettingen_graph', folder +
#                                   os.sep + 'goettingen_graph')
# osmnx.save_graphml(graph, 'goettingen.graphml', folder + os.sep)
