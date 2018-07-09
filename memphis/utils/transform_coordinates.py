# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:40:53 2018

@author: jpelda
"""

from shapely.geometry import Point, LineString, Polygon
import pyproj as pp

def transform_coords(geo, from_coord='epsg:3035', into_coord='epsg:4326'):
    '''Transforms coordinates from given to requested coordinate system.
    
    Args:
        geo: [[x]], x is either Polygon, LineString, Point or (f,f)*i)
        from_coord: str, coordinate system given
        into_coord: str, coordinate system requested
    
    Returns:
        type(geo) transformed to into_coord
    '''

    geo_as_tuples = [0]*len(geo)
    geo_type = type(geo[0])
    '''
    pp.transform needs tuples of floats to convert,
    here input is converted into tuples
    '''
    if geo_type == Polygon:
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

    return ret