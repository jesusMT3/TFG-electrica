# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 12:16:33 2023

@author: Jesús
"""
#%% Libraries
import pvlib
import pandas as pd
from matplotlib import pyplot as plt
import pathlib

#%% general data

#weather data
DATA_DIR = pathlib.Path(pvlib.__file__).parent /'data'
filename = DATA_DIR / '723170TYA.CSV'
df_tmy, metadata = pvlib.iotools.read_tmy3(filename, coerce_year = 1990)

location = pvlib.location.Location(latitude = metadata['latitude'], 
                                   longitude = metadata['longitude'])
#solar angles
times = df_tmy.index - pd.Timedelta('30min')
solar_position = location.get_solarposition(times)
solar_position.index += pd.Timedelta('30min')
#tracker data
tracker_data = pvlib.tracking.singleaxis(apparent_zenith = solar_position['apparent_zenith'], 
                                         apparent_azimuth = solar_position['azimuth'],
                                         axis_azimuth = 180)

tilt = tracker_data['surface_tilt'].fillna(0)
azimuth = tracker_data['surface_azimuth'].fillna(0)
#poa of tracker
df_poa_tracker = pvlib.irradiance.get_total_irradiance(surface_tilt = tilt, 
                                                       surface_azimuth = azimuth, 
                                                       solar_zenith = solar_position['apparent_zenith'], 
                                                       solar_azimuth = solar_position['azimuth'], 
                                                       dni = df_tmy['DNI'], 
                                                       ghi = df_tmy['GHI'], 
                                                       dhi = df_tmy['DHI'])

tracker_poa = df_poa_tracker['poa_global']
#cell temperature
parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']
cell_temperature = pvlib.temperature.sapm_cell(poa_global = tracker_poa, 
                                               temp_air = df_tmy['DryBulb'], 
                                               wind_speed = df_tmy['Wspd'], 
                                               **parameters)

# 1kW and 0,004W/ºC coefficients
gamma_pdc = -0.004
nameplate = 1000
array_power = pvlib.pvsystem.pvwatts_dc(g_poa_effective = tracker_poa, 
                                        temp_cell = cell_temperature, 
                                        pdc0 = nameplate, 
                                        gamma_pdc = gamma_pdc)

#%% Plot 1 week

array_power.head(24*7).plot()
plt.ylabel('Array Power [W]')
plt.title('Arry Power in one week')

#%% Scatter with ambient temperature

plt.scatter(x = tracker_poa, 
            y = array_power, 
            c = df_tmy['DryBulb'])
plt.colorbar()
plt.ylabel('Array Power')
plt.xlabel('POA irradiance [W/m$^2$]')
plt.title('Power vs POA, colored by air temperature')

#%% Scatter with cell temperature

plt.scatter(x = tracker_poa, 
            y = array_power, 
            c = cell_temperature)
plt.colorbar()
plt.ylabel('Array Power')
plt.xlabel('POA irradiance [W/m$^2$]')
plt.title('Power vs POA, colored by cell temperature')

#%% Comparison between monthly production and POA

df_plot = pd.DataFrame({
    'poa': tracker_poa / 1000,
    'production': array_power / 1000})
df_monthly = df_plot.resample('M').sum().plot.bar()
plt.ylabel('Energy [kWh]')

#%% Simplified inverter model (800W inverter with ratio of 1.2 and efficiency of 96%)

eff = 0.96
p_inverter = 800
pdc0 = p_inverter / eff
ac = pvlib.inverter.pvwatts(pdc = array_power, 
                            pdc0 = pdc0)

plt.rcParams['font.size'] = 14
ax = ac.resample('D').sum().plot(figsize = (15,10), label = 'AC')
array_power.resample('D').sum().plot(ax = ax, label = 'DC')
plt.title('AC POWER')
plt.ylabel('Output [Wh/day]')
plt.grid(True)
plt.legend()