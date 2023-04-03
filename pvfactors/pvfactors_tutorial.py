# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:41:09 2023

Tutorial of pvfactors which can be found on the following web site
https://sunpower.github.io/pvfactors/tutorials

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
discretization = {'cut': {
    0: {'back': 5},  # discretize the back side of the leftmost PV row into 5 segments
    1: {'front': 3}  # discretize the front side of the center PV row into 3 segments
    }}
pvarray_parameters.update(discretization)

# Create the PV array
from pvfactors.geometry import OrderedPVArray
pvarray = OrderedPVArray.fit_from_dict_of_scalars(pvarray_parameters)

# Plot
f, ax = plt.subplots(figsize = (10, 3))
pvarray.plot_at_idx(0, ax, with_surface_index=True)
plt.show()

# Print segments on each row
pvrow_left = pvarray.ts_pvrows[0]
n_segments = len(pvrow_left.back.list_segments)
print("Back side of leftmost PV row has {} segments".format(n_segments))

pvrow_center = pvarray.ts_pvrows[1]
n_segments = len(pvrow_center.front.list_segments)
print("Front side of center PV row has {} segments".format(n_segments))

#%% Calculate view factors

import matplotlib.pyplot as plt

# PV array parameters
pvarray_parameters = {
    'n_pvrows': 2,            # number of pv rows
    'pvrow_height': 1,        # height of pvrows (measured at center / torque tube)
    'pvrow_width': 1,         # width of pvrows
    'axis_azimuth': 0.,       # azimuth angle of rotation axis
    'surface_tilt': 20.,      # tilt of the pv rows
    'surface_azimuth': 90.,   # azimuth of the pv rows front surface
    'solar_zenith': 40.,      # solar zenith angle
    'solar_azimuth': 150.,    # solar azimuth angle
    'gcr': 0.5,               # ground coverage ratio
    }

# PV array
from pvfactors.geometry import OrderedPVArray
pvarray = OrderedPVArray.fit_from_dict_of_scalars(pvarray_parameters)

# Plot PV array
f, ax = plt.subplots(figsize = (10, 3))
pvarray.plot_at_idx(0, ax, with_surface_index=True)
plt.show()

# View factor matrix
from pvfactors.viewfactors import VFCalculator
vf_calculator = VFCalculator()

vf_matrix = vf_calculator.build_ts_vf_matrix(pvarray)

#%% Run full timeseries simulations

import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import pvlib, pathlib
    
#tmy data
DATA_DIR = pathlib.Path(pvlib.__file__).parent/'data'
df_tmy, metadata = pvlib.iotools.read_tmy3(DATA_DIR/'723170TYA.CSV', coerce_year=1990)

#location object to this TMY
location = pvlib.location.Location(latitude = metadata['latitude'], longitude = metadata['longitude'])

# Note: TMY datasets are right-labeled hourly intervals, e.g. the
# 10AM to 11AM interval is labeled 11.  We should calculate solar position in
# the middle of the interval (10:30), so we subtract 30 minutes:

times = df_tmy.index - pd.Timedelta('30min')
solar_position = location.get_solarposition(times)
#shift the index back to TMY data
solar_position.index += pd.Timedelta('30min')
#apparent zenith includes effect of atmospheric refraction

#POA for a tracking system
tracker_data = pvlib.tracking.singleaxis(apparent_zenith = solar_position['apparent_zenith'], 
                                         apparent_azimuth = solar_position['azimuth'], 
                                         axis_azimuth = 180)

df = pd.DataFrame({
    'dni': df_tmy['DNI'],
    'dhi': df_tmy['DHI'],
    'solar_zenith': solar_position['apparent_zenith'],
    'solar_azimuth': solar_position['azimuth'],
    'surface_tilt': tracker_data['surface_tilt'],
    'surface_azimuth': tracker_data['surface_azimuth']})

df_inputs = df.loc['1990-07-13']

# Plot the data
f, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 3))
df_inputs[['dni', 'dhi']].plot(ax=ax1)
df_inputs[['solar_zenith', 'solar_azimuth']].plot(ax=ax2)
df_inputs[['surface_tilt', 'surface_azimuth']].plot(ax=ax3)
plt.tight_layout()
plt.show()

# Fixed albedo
albedo = 0.2

# PVarray paramneters
from pvfactors.engine import PVEngine
from pvfactors.geometry import OrderedPVArray
pvarray_parameters = {
    'n_pvrows': 3,            # number of pv rows
    'pvrow_height': 1,        # height of pvrows (measured at center / torque tube)
    'pvrow_width': 1,         # width of pvrows
    'axis_azimuth': 0.,       # azimuth angle of rotation axis
    'gcr': 0.4,               # ground coverage ratio
    'rho_front_pvrow': 0.01,  # pv row front surface reflectivity
    'rho_back_pvrow': 0.03,   # pv row back surface reflectivity
}

# Simulation for a single timestep
pvarray = OrderedPVArray.init_from_dict(pvarray_parameters)

engine = PVEngine(pvarray)

engine.fit(df_inputs.index, df_inputs.dni, df_inputs.dhi,
           df_inputs.solar_zenith, df_inputs.solar_azimuth,
           df_inputs.surface_tilt, df_inputs.surface_azimuth,
           albedo)

# Get PV array
pvarray = engine.run_full_mode(fn_build_report = lambda pvarray: pvarray)

# Plot pvarray shapely geometries
f, ax = plt.subplots(figsize=(10, 3))
pvarray.plot_at_idx(15, ax, with_surface_index=True)
ax.set_title(df_inputs.index[15])
plt.show()

# Run multiple timesteps
from pvfactors.report import example_fn_build_report

report = engine.run_full_mode(fn_build_report = example_fn_build_report)
df_report = pd.DataFrame(report, index = df_inputs.index)

f, ax = plt.subplots(1, 2, figsize=(10, 3))
df_report[['qinc_front', 'qinc_back']].plot(ax=ax[0])
df_report[['iso_front', 'iso_back']].plot(ax=ax[1])
plt.tight_layout()
plt.show()