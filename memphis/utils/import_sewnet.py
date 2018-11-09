# -*- coding: utf-8 -*-
"""
Created on 23.08.2018

@author: jpelda
"""

def import_sewagenetwork(data):
    sew_net = data.read_from_sqlServer('sewage_network')
    for key in sew_net.keys():
        if key in ['s_height', 'e_height', 'length', 'depth']:
            sew_net[key] = sew_net[key].str.replace(',', '.')
            sew_net[key] = sew_net[key].astype(float)
    if 'type' in sew_net.keys():
        sew_net = sew_net[sew_net['type'] == 'Schmutzwasserkanal']

    sew_net['DN'] = sew_net['width'] / 1000
    sew_net['height'] = sew_net['height'] / 1000

    return sew_net