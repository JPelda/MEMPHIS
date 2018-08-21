# -*- coding: utf-8 -*-
"""
Created on Tue May 29 10:06:08 2018

@author: Adrian
"""
import numpy as np

def DN_to_V(self, df, g=9.81, v=1.31e-6, k=15e-4):
    '''Calculates the maximum volumestream possible in channel with
    nominal width DN.

    Args:
    -----
    df : pandas.DataFrame()
         col DN: nominal diameter [m]
         col s_height: height of channel at inlet [m]
         col e_height: height of channel at outlet [m]
         col length: length of channel [m]

    Kwargs:
    -------
    g : float
        earth's acceleration [m/s²] \n
    v : float
        kinematic viscosity waste water in [m²/s]
    k : float
        operational roughness of the inner profile wall for sewers [m]

    Returns:
    --------
    Wastewaterflow: float
        max possible waste water flow in channel [m³ / s]
    '''
    s_height = df['s_height']
    e_height = df['e_height']
    length = df['length']
    DN = df['DN']

    delta_h = [np.abs(s - e) if not
               np.abs(s - e) == 0 else 1e-5 for s, e in
               zip(s_height, e_height)]
    # 0.002 is for values that have np.nan as values
    J_e = np.array([d / l if not np.isnan(d / l) else 0.002 for
                    d, l in zip(delta_h, length)])
    J_e = np.abs(J_e)
    DN = np.abs(DN)

    C = (np.pi * np.power(DN, 2)) / 4
    N = -2 * np.log10(((2.51 * v) / (DN * np.sqrt(2 * g * DN * J_e))) +
                      (k / (3.71 * DN))) * np.sqrt(2 * g * DN * J_e)
    V = C * N

    return V
