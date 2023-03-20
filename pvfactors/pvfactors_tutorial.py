# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:41:09 2023

@author: Jesus
"""

#%% Getting Started

#import external libraries
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Timeseries inputs
df_inputs = pd.DataFrame(
    {'solar_zenith': [20., 50.],
     'solar_azimuth': [110., 250.],
     'surface_tilt': [10., 20.],
     'surface_azimuth': [90., 270.],
     'dni': [1000., 900.],
     'dhi': [50., 100.],
     'albedo': [0.2, 0.2]},
    index=[datetime(2017, 8, 31, 11), datetime(2017, 8, 31, 15)]
)

# PV array parameters
pvarray_parameters = {
    'n_pvrows': 3,            # number of pv rows
    'pvrow_height': 1,        # height of pvrows (measured at center / torque tube)
    'pvrow_width': 1,         # width of pvrows
    'axis_azimuth': 0.,       # azimuth angle of rotation axis
    'gcr': 0.4,               # ground coverage ratio
    }

# Create a PV array and update it with the engine
from pvfactors.engine import PVEngine
from pvfactors.geometry import OrderedPVArray

pvarray = OrderedPVArray.init_from_dict(pvarray_parameters) # PVarray
engine = PVEngine(pvarray) # engine

engine.fit(timestamps = df_inputs.index, 
           DNI = df_inputs.dni, 
           DHI = df_inputs.dhi, 
           solar_zenith = df_inputs.solar_zenith, 
           solar_azimuth = df_inputs.solar_azimuth, 
           surface_tilt = df_inputs.surface_tilt, 
           surface_azimuth = df_inputs.surface_azimuth, 
           albedo = df_inputs.albedo)

# Plot
f, ax = plt.subplots(figsize = (10, 3))
pvarray.plot_at_idx(1, ax)
plt.show()

# Run simulation using the full mode

# Report function
def fn_report(pvarray):
    return pd.DataFrame({'qinc_back': pvarray.ts_pvrows[1].back.get_param_weighted('qinc')})

# Run full-mode simulation
report = engine.run_full_mode(fn_build_report = fn_report)

#print results
df_report_full = report.assign(timestamps = df_inputs.index).set_index('timestamps')

#Run simulation using the fast mode
df_report_fast = engine.run_fast_mode(fn_build_report = fn_report,  pvrow_index = 1)

#%% PV array geometry introduction

# Imports
import matplotlib.pyplot as plt

# PV array parameters
pvarray_parameters = {
    'n_pvrows': 4,            # number of pv rows
    'pvrow_height': 1,        # height of pvrows (measured at center / torque tube)
    'pvrow_width': 1,         # width of pvrows
    'axis_azimuth': 0.,       # azimuth angle of rotation axis
    'surface_tilt': 20.,      # tilt of the pv rows
    'surface_azimuth': 90.,   # azimuth of the pv rows front surface
    'solar_zenith': 40.,      # solar zenith angle
    'solar_azimuth': 150.,    # solar azimuth angle
    'gcr': 0.5,               # ground coverage ratio
    }

# Create a PV array and its shadows
from pvfactors.geometry import OrderedPVArray
pvarray = OrderedPVArray.fit_from_dict_of_scalars(pvarray_parameters)

# Plot PV array
f, ax = plt.subplots(figsize = (10, 3))
pvarray.plot_at_idx(0, ax)
plt.show()

# Situation with direct shading
pvarray_parameters.update({'surface_tilt': 80.,
                           'solar_zenith': 75.,
                           'solar_azimuth': 90.})

#create new PV array with updated pvarray_parameters
pvarray_w_direct_shading = OrderedPVArray.fit_from_dict_of_scalars(pvarray_parameters)

# Plot PV array
f, ax = plt.subplots(figsize = (10, 3))
pvarray_w_direct_shading.plot_at_idx(0, ax)
plt.show()

# Shaded length on first pv row (leftmost)
l = pvarray_w_direct_shading.ts_pvrows[0].front.shaded_length
print("Shaded length on front surface of leftmost PV row: %.2f m" % l)

# Shaded length on last pv row (rightmost)
l = pvarray_w_direct_shading.ts_pvrows[-1].front.shaded_length
print("Shaded length on front surface of rightmost PV row: %.2f m" %l)

# Timeseries geometries introduction
front_ilum_ts_surface = pvarray_w_direct_shading.ts_pvrows[0].front.list_segments[0].illum.list_ts_surfaces[0]
coords = front_ilum_ts_surface.coords
print("Coords: {}".format(coords))

#%% Discretize PV row sides and indexing

import matplotlib.pyplot as plt

pvarray_parameters = {
    'n_pvrows': 3,            # number of pv rows
    'pvrow_height': 1,        # height of pvrows (measured at center / torque tube)
    'pvrow_width': 1,         # width of pvrows
    'axis_azimuth': 0.,       # azimuth angle of rotation axis
    'surface_tilt': 20.,      # tilt of the pv rows
    'surface_azimuth': 270.,   # azimuth of the pv rows front surface
    'solar_zenith': 40.,      # solar zenith angle
    'solar_azimuth': 150.,    # solar azimuth angle
    'gcr': 0.5,               # ground coverage ratio
    }

# Discretization scheme
discretization = {
    0: {'back': 5},  # discretize the back side of the leftmost PV row into 5 segments
    1: {'front': 3}  # discretize the front side of the center PV row into 3 segments
    }
pvarray_parameters.update(discretization)

# Create the PV array
from pvfactors.geometry import OrderedPVArray
pvarray = OrderedPVArray.fit_from_dict_of_scalars(pvarray_parameters)

# Plot
f, ax = plt.subplots(figsize = (10, 3))
pvarray.plot_at_idx(0, ax)
plt.show()


pvrow_left = pvarray.ts_pvrows[0]
n_segments = len(pvrow_left.back.list_segments)
print("Back side of leftmost PV row has {} segments".format(n_segments))

pvrow_center = pvarray.ts_pvrows[1]
n_segments = len(pvrow_center.front.list_segments)
print("Front side of center PV row has {} segments".format(n_segments))