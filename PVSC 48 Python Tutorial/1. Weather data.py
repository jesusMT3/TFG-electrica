# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 09:55:28 2023

First chapter of the tutorial, in which we will learn how to get  wather data

@author: Jesús
"""
#import libraries (pvlib, pandas, and matplotlib)

import os #environment values
import pathlib #example datasheet
import pvlib
import pandas as pd #for data warngling
import matplotlib.pyplot as plt #plotting and general visualization
print('Current pvlib version: ', pvlib.__version__) #plot the current version of pvlib

#Reading a TMY dataset with pvlib
#help(pvlib.iotools.read_tmy3)

DATA_DIR = pathlib.Path(pvlib.__file__).parent / 'data'
df_tmy, meta_dict = pvlib.iotools.read_tmy3(DATA_DIR / '723170TYA.CSV', coerce_year= 1990)
#print(df_tmy.keys())

#irradiance, wind and air temperature
# GHI, DHI, DNI are irradiance measurements (W/m^2)
# DryBulb is the "dry-bulb" (ambient) temperature (ºC)
# Wspd is wind speed (m/s)

df = df_tmy[['GHI', 'DHI', 'DNI', 'DryBulb', 'Wspd']]
#print(df.head(15))

#plotting with panda

#irradiance
first_week = df.head(24*7) #7 days, 24h a day
first_week[['GHI', 'DHI', 'DNI']].plot()
plt.xlabel('days')
plt.ylabel('Irradiance (W/m$2$)')
plt.title('Irradiance per week')
plt.grid();

#temperature
first_week[['DryBulb']].plot()
plt.xlabel('days')
plt.ylabel('Temperature (ºC)')
plt.title('Temperature per week')
plt.legend(['temp'])
plt.grid();

#wind speed
first_week[['Wspd']].plot()
plt.xlabel('days')
plt.ylabel('Wind speed (m7s)')
plt.title('Wind speed per week')
plt.legend(['v'])
plt.grid();

#plot monthly sums
monthly_ghi = df['GHI'].resample('M').sum()
monthly_ghi.plot.bar()
plt.ylabel('Insolation (Wh/m$2$)')
plt.title('Monthly insolation');

#plot averages
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()  # add a second y-axis
monthly_average_temp_wind = df[['DryBulb', 'Wspd']].resample('M').mean()
monthly_average_temp_wind['DryBulb'].plot(ax=ax1, c='tab:blue')
monthly_average_temp_wind['Wspd'].plot(ax=ax2, c='tab:orange')
ax1.set_ylabel(r'Ambient Temperature [$\degree$ C]')
ax2.set_ylabel(r'Wind Speed [m/s]')
ax1.legend(loc='lower left')
ax2.legend(loc='lower right');

#plot direct and diffuse irradiance
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()  # add a second y-axis
monthly_average_temp_wind = df[['GHI', 'DHI']].resample('M').mean()
monthly_average_temp_wind['GHI'].plot(ax=ax1, c='tab:blue')
monthly_average_temp_wind['DHI'].plot(ax=ax2, c='tab:orange')
ax1.set_ylabel(r'Global horizontal irradiance [W/m$2$]')
ax2.set_ylabel(r'Diffuse horizontal irradiance [W/m$2$]')
ax1.legend(loc='lower left')
ax2.legend(loc='lower right');
