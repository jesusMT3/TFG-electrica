# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 10:16:47 2023

@author: Jesús
"""

import pvlib
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import pathlib

#set STC conditions
E0 = 1000 # W/m^2
T0 = 25 # ºC

# set the IEC grid
E_IEC = [100, 200, 400, 600, 800, 1000, 1100] # irradiances W/m^2
T_IEC = [15, 25, 50, 75] # temperatures ºC

#meshgrid of temperatures and irradiances
IEC = np.meshgrid(T_IEC, E_IEC)

# use pvlib python to retrieve CEC module parameters from the SAM libraries
# with the "name" argument set to "CECMod"
CECMODS = pvlib.pvsystem.retrieve_sam(name='CECMod')
index = CECMODS.T.index

#using filters to search for modules
filters = CECMODS.T.index.str.startswith('Canadian_Solar') & CECMODS.T.index.str.contains('220M')
canadian_solar = CECMODS.T[filters]

#using C5SP-220M
CS_220M = CECMODS['Canadian_Solar_Inc__CS5P_220M']

#%%
#cell to look for modules

your_mod = 'Shanghai_Aerospace_Automobile_Electromechanical_Co___Ltd__HT72_156M_V__350'
try:
    your_mod = CECMODS[your_mod]
except KeyError:
    print(f"*** Sorry, '{your_mod}' wasn't found in CECMODS. Please try again. ***")
else:
    # display your module
    your_mod
#%%
# finally this is the magic
temp_cell, effective_irradiance = IEC
cecparams = pvlib.pvsystem.calcparams_cec(
        effective_irradiance=effective_irradiance,
        temp_cell=temp_cell,
        alpha_sc=CS_220M.alpha_sc,
        a_ref=CS_220M.a_ref,
        I_L_ref=CS_220M.I_L_ref,
        I_o_ref=CS_220M.I_o_ref,
        R_sh_ref=CS_220M.R_sh_ref,
        R_s=CS_220M.R_s,
        Adjust=CS_220M.Adjust,
        EgRef=1.121,
        dEgdT=-0.0002677)
IL, I0, Rs, Rsh, nNsVth = cecparams
# display the photogenerated current
IL
#%% #IV curve info
curve_info = pvlib.pvsystem.singlediode(photocurrent = IL.flatten(), 
                                        saturation_current = I0.flatten(), 
                                        resistance_series = Rs, 
                                        resistance_shunt = Rsh.flatten(), 
                                        nNsVth = nNsVth.flatten(),
                                        ivcurve_pnts = 101,
                                        method = 'lambertw')

#plot the calculated curves
exclude = [(1100, 15), (400, 75), (200, 50), (200, 75), (100, 50), (100, 75)] #inusual points
kolor = ['#1f77b4', '#2ca02c', '#8c564b', '#9467bd', '#d62728', '#e377c2', '#ff7f0e'] #color of the curves
f, ax = plt.subplots(2, 2, figsize = (16, 10), sharex = True, sharey = True)
for m, irr in enumerate(E_IEC):
    for n, tc in enumerate(T_IEC):
        if (irr, tc) in exclude:
            continue
        
        
        i = n + 4 * m
        j = n // 2, n % 2
        label = ("$G_{eff}$ " + f"{irr} $W/m^2$")
        
        #plot V(i) and get vmp and imp
        ax[j].plot(curve_info['v'][i], curve_info['i'][i], label = label, c = kolor[m])
        v_mp = curve_info['v_mp'][i]
        i_mp = curve_info['i_mp'][i]
        
        #mark the MPP
        ax[j].plot(v_mp, i_mp, ls = '', marker = 'o', c = kolor[m])
        ax[j].vlines(v_mp, 0, i_mp, linestyle = 'dashed', color = kolor[m])
        
        #legend
        ax[j].legend(loc = 'right')
        if j[0] == 1:
            ax[j].set_xlabel('Module voltage [V]')
        if j[1] == 0:
            ax[j].set_ylabel('Module current [A]')
        ax[j].set_title(f"{CS_220M.name}, " + "$T_{cell}$ " + f"{tc} " + "$^{\circ}C$")
        ax[j].grid(True)
        ax[j].set_xlim([0, 80])
        
f.tight_layout()