# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 12:24:19 2023

Using the thhermal module from the Sandia Array Performance Model

@author: Jesús
"""

import pvlib
import pandas as pd
import matplotlib.pyplot as plt
import pathlib

print(pvlib.__version__)

#wather and tracking data
DATA_DIR = pathlib.Path(pvlib.__file__).parent / 'data'

df_tmy, metadata = pvlib.iotools.read_tmy3(DATA_DIR / '723170TYA.CSV', coerce_year = 1990)

location = pvlib.location.Location(latitude = metadata['latitude'], 
                                   longitude = metadata['longitude'])

times = df_tmy.index - pd.Timedelta('30min')
solar_position = location.get_solarposition(times)
solar_position.index += pd.Timedelta('30min')

tracker_data = pvlib.tracking.singleaxis(apparent_zenith = solar_position['apparent_zenith'], 
                                         apparent_azimuth = solar_position['azimuth'],
                                         axis_azimuth = 180)
tilt = tracker_data['surface_tilt'].fillna(0)
azimuth = tracker_data['surface_azimuth'].fillna(0)

df_poa_tracker = pvlib.irradiance.get_total_irradiance(surface_tilt = tilt, 
                                                       surface_azimuth = azimuth, 
                                                       solar_zenith = solar_position['apparent_zenith'], 
                                                       solar_azimuth = solar_position['azimuth'], 
                                                       dni = df_tmy['DNI'], 
                                                       ghi = df_tmy['GHI'], 
                                                       dhi = df_tmy['DHI'])
tracker_poa = df_poa_tracker['poa_global']

#thermal parameters
all_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']
parameters = all_parameters['open_rack_glass_polymer']
cell_temperature = pvlib.temperature.sapm_cell(poa_global = tracker_poa, 
                                               temp_air = df_tmy['DryBulb'], 
                                               wind_speed = df_tmy['Wspd'], 
                                               a = parameters['a'], 
                                               b = parameters['b'],
                                               deltaT = parameters['deltaT'])
#%%
df_temperature = pd.DataFrame({
    'ambient': df_tmy['DryBulb'],
    'cell': cell_temperature})

df_temperature[['ambient', 'cell']].head(24*7).plot()
plt.grid()
plt.legend(['DeyBulb', 'Cell temperature'])#plt.title('Comparison between air temperature and cell temperature')
plt.ylabel('[Degrees]')
#%%
#scatter plot for wind speed effects
temperature_difference = cell_temperature - df_tmy['DryBulb']
plt.scatter(tracker_poa, temperature_difference, c = df_tmy['Wspd'])
plt.colorbar()
plt.ylabel('Temperature difference [$\degree$]')
plt.xlabel('POA irradiance [W/m$^2$]')
plt.title('Cell temperature rise, colored by wind speed')
#%%
