# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:40:53 2018

@author: jpelda
"""

from shapely.geometry import Point, LineString, Polygon
import shapely.ops as ops
from functools import partial
import pyproj as pp
import pandas as pd


def transform_coords(geo, from_coord='epsg:3035', into_coord='epsg:4326'):
    '''Transforms coordinates from given to requested coordinate system.
    
    Args:
        geo: [[x]], x is either Polygon, LineString, Point or (f,f)*i)
        from_coord: str, coordinate system given
        into_coord: str, coordinate system requested
    
    Returns:
        type(geo) transformed to into_coord
    '''
    import time
    stime = time.time()
    if type(geo[0]) == pd.core.series.Series:
        geo = geo[0].tolist()
    geo_as_tuples = [0]*len(geo)
    geo_type = type(geo[0])
    '''
    pp.transform needs tuples of floats to convert,
    here input is converted into tuples
    '''

    if isinstance(geo[0], Polygon):
        for i, poly in enumerate(geo):
            geo_as_tuples[i] = [(x, y) for x, y in
                                            zip(poly.exterior.coords.xy[0],
                                                poly.exterior.coords.xy[1])]
    elif geo_type == LineString:
        for i, line in enumerate(geo):
            geo_as_tuples[i] = [(x, y) for x, y in list(line.coords)]
    elif geo_type == Point:
        for i, point in enumerate(geo):
            geo_as_tuples[i] = [(point.coords[0][0], point.coords[0][1])]
    else:
        for i, item in enumerate(geo):
            geo_as_tuples[i] = [(x,y) for x, y in item]

    #  conversion of coordinates
    geo_convert = [0]*len(geo)
    for i, tuples in enumerate(geo_as_tuples):
        x = [x[0] for x in tuples]
        y = [x[1] for x in tuples]
        geo_convert[i] = pp.transform(pp.Proj(init=from_coord),
                                    pp.Proj(init=into_coord),
                                    x, y)
        geo_convert[i] = [(x, y) for x, y in zip(geo_convert[i][0],
                                             geo_convert[i][1])]

    # type(geo) shall be the output type
    ret = [0]*len(geo)
    if geo_type == Polygon:
        for i, item in enumerate(geo_convert):
            ret[i] = Polygon(item)
    elif geo_type == LineString:
        for i, item in enumerate(geo_convert):
            ret[i] = LineString(item)
    elif geo_type == Point:
        for i, item in enumerate(geo_convert):
            ret[i] = Point(item)
    else:
        ret = geo_convert
    print("transform_coords | {}".format(time.time() - stime))
    return ret


def transform_length(length, crs_from="EPSG:32633", crs_into="EPSG:4326"):
    """Transforms length into length based on crs.
        It is a little bit imprecise. For better results use 
        method crs_length_to_meter.

    ARGS:
    -----
    length: float [meter]

    KWARGS:
    ------
    crs_from: str
        coord system of length
    crs_into: str
        coord system in which length shall be converted

    RETURNS:
    --------
    length: float [crs based]
    """

    length = LineString([(0, 0), (length, 0)])
    project = partial(pp.transform,
                      pp.Proj(init=crs_from),
                      pp.Proj(init=crs_into))
    length = ops.transform(project, length)
    length = length.length

    return length


def crs_length_to_meter(linestring, crs='WGS84'):
    """Transforms crs_length into meters.

    ARGS:
    -----
    linestring: shapely.geometry.LineString

    RETURNS:
    -------
    length: float [m]
    """

    geod = pp.Geod(ellps=crs)
    angle1, angle2, distance = geod.inv(linestring.xy[0][0],
                                        linestring.xy[1][0],
                                        linestring.xy[0][1],
                                        linestring.xy[1][1])
    return distance

def transform_area(geom, crs_from="EPSG:4326"):
    """Transforms area into are based on crs.
    
    ARGS:
    ----
    geom: list
        List contains geometric objects.
    KWARGS:
    ------
    crs_from: str
        coord system of geom
    crs_into: str
        coord system defining the unit of return
    
    RETURNS:
    -------
    area: [floats] [crs based]
        EPSG:3035 returns area [m]
    """

    geom_area = [0] * len(geom)

    for index, geo in enumerate(geom):
        g = ops.transform(partial(pp.transform,
                                      pp.Proj(init=crs_from),
                                      pp.Proj(proj='aea',
                                              lat1=geo.bounds[1],
                                              lat2=geo.bounds[3])),
                                  geo)
        geom_area[index] = g.area

    return geom_area

