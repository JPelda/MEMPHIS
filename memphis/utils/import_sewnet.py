# -*- coding: utf-8 -*-
"""
Created on 23.08.2018

@author: jpelda
"""

def import_sewagenetwork(data):
    sew_net = data.read_from_sqlServer('sewage_network')
    sew_net = sew_net[sew_net['type'] == 'Schmutzwasserkanal']
    sew_net['s_height'] = sew_net['s_height'].str.replace(',', '.')
    sew_net['e_height'] = sew_net['e_height'].str.replace(',', '.')
    sew_net['length'] = sew_net['length'].str.replace(',', '.')
    sew_net['depth'] = sew_net['depth'].str.replace(',', '.')
    sew_net['s_height'] = sew_net['s_height'].astype(float)
    sew_net['e_height'] = sew_net['e_height'].astype(float)
    sew_net['length'] = sew_net['length'].astype(float)
    sew_net['depth'] = sew_net['depth'].astype(float)
    sew_net['DN'] = sew_net['width'] / 1000
    sew_net['height'] = sew_net['height'] / 1000

    return sew_net