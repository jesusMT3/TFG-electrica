# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 11:14:52 2023

Second chapter of the tutorial, POA irradiance

@author: Jesús
"""

import pvlib
import pandas as pd
import matplotlib.pyplot as plt
import pathlib #example dataset

print(pvlib.__version__)

#data from previous chapter
DATA_DIR = pathlib.Path(pvlib.__file__).parent/'data'
df_tmy, metadata = pvlib.iotools.read_tmy3(DATA_DIR/'723170TYA.CSV', coerce_year=1990)

#location object to this TMY
location = pvlib.location.Location(latitude = metadata['latitude'], longitude = metadata['longitude'])
print("We are looking at data from ", metadata['Name'], metadata['State'])

# Note: TMY datasets are right-labeled hourly intervals, e.g. the
# 10AM to 11AM interval is labeled 11.  We should calculate solar position in
# the middle of the interval (10:30), so we subtract 30 minutes:

times = df_tmy.index - pd.Timedelta('30min')
solar_position = location.get_solarposition(times)
#shift the index back to TMY data
solar_position.index += pd.Timedelta('30min')
print(solar_position.head())
#apparent zenith includes effect of atmospheric refraction

#transposition model to get total irradiance (20º facing south (180º))
df_poa = pvlib.irradiance.get_total_irradiance(surface_tilt = 20, 
                                               surface_azimuth = 180, 
                                               solar_zenith = solar_position['apparent_zenith'], 
                                               solar_azimuth = solar_position['azimuth'], 
                                               dni = df_tmy['DNI'], ghi = df_tmy['GHI'], dhi = df_tmy['DHI'])

#difference between GHI and POA
df = pd.DataFrame({
    'ghi': df_tmy['GHI'],
    'poa': df_poa['poa_global'],})

df_monthly = df.resample('M').sum()
df_monthly[['ghi', 'poa']].plot.bar()
plt.title("Comparison between GHI and POA")
plt.ylabel('Monthly insolation [Wh/m$^2$]')


#POA for a tracking system
tracker_data = pvlib.tracking.singleaxis(apparent_zenith = solar_position['apparent_zenith'], 
                                         apparent_azimuth = solar_position['azimuth'], 
                                         axis_azimuth = 180)

day_data = tracker_data.head(24).fillna(0)
day_data[['tracker_theta']].plot() #plot daily tracking
plt.title('Single axis tracking')
plt.ylabel('Tracker rotation [degrees]')

df_poa_tracking = pvlib.irradiance.get_total_irradiance(surface_tilt = tracker_data['surface_tilt'], 
                                                        surface_azimuth = tracker_data['surface_azimuth'], 
                                                        solar_zenith = solar_position['apparent_zenith'], 
                                                        solar_azimuth = solar_position['azimuth'], 
                                                        dni = df_tmy['DNI'], 
                                                        ghi = df_tmy['GHI'], 
                                                        dhi = df_tmy['DHI'])

df_global = pd.DataFrame({
    'ghi': df_tmy['GHI'],
    'poa': df_poa_tracking['poa_global'].fillna(0)})

df_day = df_global.loc['1990-01-15']
df_day[['ghi', 'poa']].plot()
plt.title('Daily comparison between ghi and global poa tracking')
plt.ylabel('Irradiance [W/m$^2$]')

df_global_monthly = df_global.resample('M').sum()#monthly
df_global_monthly[['ghi', 'poa']].plot.bar()
plt.title('Monthly comparison between ghi and global poa irradiance')
plt.ylabel('Monthly insolation [Wh/m$^2$]')