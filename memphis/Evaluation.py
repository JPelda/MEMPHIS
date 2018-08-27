# -*- coding: utf-8 -*-
"""
Created on Thu May 31 11:46:47 2018

@author: jpelda
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import MultiLineString

import Allocation as alloc
from transformations_of_crs_values import transform_length

def memphis_vs_sewagenetwork(Data, gdf_sewnet, gdf_paths, gdf_census):
    geo0 = [x[0] for x in gdf_sewnet['SHAPE'].boundary]
    geo1 = [x[1] for x in gdf_sewnet['SHAPE'].boundary]
    V = np.append(gdf_sewnet['V'].values, gdf_sewnet['V'].values)
    length = np.append(gdf_sewnet['length'].values,
                       gdf_sewnet['length'].values)
    d = {'geometry': geo0 + geo1, 'V': V, 'length': length}
    df = pd.DataFrame(data=d)
    gdf_pts_sewnet = gpd.GeoDataFrame(df, crs=Data.coord_system,
                                      geometry='geometry')

    geo0 = [x[0] for x in gdf_paths.geometry.boundary]
    geo1 = [x[1] for x in gdf_paths.geometry.boundary]
    V = np.append(gdf_paths.V.values, gdf_paths.V.values)
    length = np.append(gdf_paths['length'].values, gdf_paths['length'].values)
    d = {'geometry': geo0 + geo1, 'V': V, 'length': length}
    df = pd.DataFrame(data=d)
    gdf_pts_paths = gpd.GeoDataFrame(df, crs=Data.coord_system,
                                     geometry='geometry')

    gdf_pts_sewnet['inhabs'], gdf_pts_sewnet[
        'raster'] = alloc.alloc_nodes_to_inhabs(
        gdf_census, gdf_pts_sewnet)
    gdf_pts_paths['inhabs'], gdf_pts_paths[
        'raster'] = alloc.alloc_nodes_to_inhabs(
        gdf_census, gdf_pts_paths)

    # Getting distribution of points V to census inhabs
    keys = set(gdf_census.inhabs)
    dis_sew_in_inh = count_val_over_key(gdf_pts_sewnet, keys)
    dis_pat_in_inh = count_val_over_key(gdf_pts_paths, keys)
    dis_cen_in_inh = count_val_over_key(gdf_census, keys)
    pat_comp_V_sew = best_pts_within_overlay_pts('V',
                                                 gdf_pts_paths,
                                                 gdf_pts_sewnet,
                                                 buffer=transform_length(
                                                 20))

    k = list(pat_comp_V_sew.keys())
    k = [(k[i], k[i + 1]) for i, item in enumerate(k) if i + 1 < len(k)]
    boxplot_V_over_V_pat = {key: [] for key in pat_comp_V_sew.keys()}
    boxplot_V_over_V_sew = {key: [] for key in pat_comp_V_sew.keys()}
    for tup in k:
        V_list = []
        for val in pat_comp_V_sew[tup[0]]:
            if not val.empty:
                V_list.append(val.V)
            else:
                V_list.append([])
        boxplot_V_over_V_pat[tup[0]] = V_list

        V_list = []
        arr = gdf_pts_sewnet[gdf_pts_sewnet.V > tup[0]]
        arr = arr[arr.V <= tup[1]]
        if not arr.empty:
            V_list.append(arr['V'].values)
        else:
            V_list.append([])
        boxplot_V_over_V_sew[tup[0]] = V_list

    boxplot_length_over_V_pat = {key: [] for key in pat_comp_V_sew.keys()}
    boxplot_length_over_V_sew = {key: [] for key in pat_comp_V_sew.keys()}
    for tup in k:
        L_list = []
        for val in pat_comp_V_sew[tup[0]]:
            if not val.empty:
                L_list.append(val.length)
            else:
                L_list.append([])
        boxplot_length_over_V_pat[tup[0]] = L_list

        L_list = []
        leng = gdf_pts_sewnet[gdf_pts_sewnet.V > tup[0]]
        leng = leng[leng.V <= tup[1]]
        if not leng.empty:
            L_list.append(leng['length'].values)
        else:
            L_list.append([])
        boxplot_length_over_V_sew[tup[0]] = L_list

    overlay_match = {}
    overlay_sew = {}
    overlay_pat = {}
    for tup in k:
        m_ls_sew = gdf_sewnet[gdf_sewnet.V >= tup[0]]
        m_ls_sew = m_ls_sew[m_ls_sew.V < tup[1]]
        m_ls_pat = gdf_paths[gdf_paths.V >= tup[0]]
        m_ls_pat = m_ls_pat[m_ls_pat.V < tup[1]]

        m_ls_sew['geometry'] = m_ls_sew.buffer(transform_length(30))

        m_ls_sew = MultiLineString([(x) for x in m_ls_sew.geometry.values])
        m_ls_pat = MultiLineString([(x) for x in m_ls_pat.geometry.values])
        lines = m_ls_sew.intersection(m_ls_pat)

        overlay_match[tup[1]] = transform_length(
            np.sum(lines.length),
            crs_from="EPSG:4326",
            crs_into="EPSG:32633")
        overlay_sew[tup[1]] = transform_length(
            np.sum(m_ls_sew.length),
            crs_from="EPSG:4326",
            crs_into="EPSG:32633")
        overlay_pat[tup[1]] = transform_length(
            np.sum(m_ls_pat.length),
            crs_from="EPSG:4326",
            crs_into="EPSG:32633")

    length_over_V_sew = {}
    length_over_V_pat = {}

    for tup in k:
        m_ls_sew = gdf_sewnet[gdf_sewnet.V >= tup[0]]
        m_ls_sew = m_ls_sew[m_ls_sew.V < tup[1]]
        m_ls_pat = gdf_paths[gdf_paths.V >= tup[0]]
        m_ls_pat = m_ls_pat[m_ls_pat.V < tup[1]]

        len_sew = transform_length(sum(m_ls_sew.geometry.length),
                                   crs_from="EPSG:4326",
                                   crs_into="EPSG:32633")
        len_pat = transform_length(sum(m_ls_pat.geometry.length),
                                   crs_from="EPSG:4326",
                                   crs_into="EPSG:32633")

        length_over_V_sew[tup[1]] = len_sew
        length_over_V_pat[tup[1]] = len_pat

    return boxplot_V_over_V_pat, boxplot_length_over_V_pat,\
           boxplot_length_over_V_sew,\
           dis_sew_in_inh, dis_pat_in_inh, dis_cen_in_inh

def count_val_over_key(gdf, keys, keys_name='inhabs'):
    """Clusters points to -1, 0, 5, 10, 15 ... by its inhabs as gdf.keys()

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame()
        Data that are clustered by keys.
    keys : set
        Are the keys the gdf is clustered by.
    keys_name: str, optional
        The name of values of keys. Must also be given as col name in gdf.
    Returns
    -------
    dict
        dict.keys == cluster_keys
        dict.values == len(items of gdfs) per cluter_key
    """
    maxi_val = np.around(max(keys))
    mini_val = 0
    rang = np.arange(mini_val, np.around(maxi_val, decimals=-1) + 5, 5)
    rang = np.insert(rang, 0, -1)
    rang = {key: 0 for key in rang}

    cluster = {key: gdf[gdf[keys_name] == key] for key in keys}

    for key, obj in cluster.items():
        val = len(obj[keys_name])
        if key == -1:
            rang[key] += val
        else:
            rang[int(np.around(key / 5, decimals=0) * 5)] += val
    return rang


def best_pts_within_overlay_pts(comp_val, gdf, gdf_orig, buffer):
    """Selects pts in gdf, that match to pts in gdf_orig,
    clustered to 0.25, 0.5, 0.75, 1....

    Parameters
    ----------
    comp_val : str
        the col_name by which the best point is compared to gdf_orig
    gdf : geopandas.DataFrame()
        gdf with col 'geometry' that is matched with gdf_orig.
    gdf_orig : geopandas.DataFrame()
        gdf with col 'geometry' gdf is matched to.
    buffer : float
        Buffer around gdf_orig['geometry'] in [m].

    Returns
    --------
    dict
        dictionary of gdf's
    """
    # TODO mark keys, where no V of sewage system exists.
    maxi_val = 0.25
    mini_val = 0
    rang = np.arange(mini_val, np.around(maxi_val + 0.01, decimals=3),
                     0.01)
    rang = np.insert(rang, 0, -1)
    rang = {key: [] for key in rang}

    gdf_o = gdf_orig[gdf_orig['inhabs'] >= 0]
    gdf_ = gdf[gdf['inhabs'] >= 0]

    geos = gdf_o['geometry'].buffer(buffer)

    sindex = gdf_.sindex

    for i, (geo, val) in enumerate(zip(geos, gdf_o[comp_val])):
        print("\rLeft:{:>10}".format(len(geos) - i), end='')

        if isinstance(val, (float, int)) and val != np.nan\
                and val < maxi_val:
            poss_matches_i = list(sindex.intersection(geo.bounds))

            if poss_matches_i != []:
                poss_matches = gdf_.iloc[poss_matches_i]
                idx = np.abs(poss_matches[comp_val]
                             - val).values.argmin()
                rang[np.around(val / 0.01, decimals=0) * 0.01].append(
                    poss_matches.iloc[idx])

    return rang
