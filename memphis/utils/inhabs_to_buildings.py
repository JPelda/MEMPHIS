# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 13:40:46 2018

@author: dreyF
"""
from copy import deepcopy
from transformations_of_crs_values import transform_area


def inhabs_to_buildings(gdf_gis_b, inhabitants, types):
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
