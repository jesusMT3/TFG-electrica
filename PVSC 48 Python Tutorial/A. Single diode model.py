# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 13:04:58 2023

@author: Jesús
"""

#%% Libraries

import pvlib
import pandas as pd
from matplotlib import pyplot as plt

#%% Dataframe for solar data
YEAR = 2002
STARTDATE = '%d-01-01T00:00:00' % YEAR
ENDDATE = '%d-12-31T23:59:59' % YEAR
TIMES = pd.date_range(start = STARTDATE, end = ENDDATE, freq = 'H')

#%% Retrieve CEC module and inverter parameters from SAM libraries

CECMODS = pvlib.pvsystem.retrieve_sam('CECMod')
INVERTERS = pvlib.pvsystem.retrieve_sam('CECInverter')

# dictionary for all the modules and inverters
df_modules = CECMODS.T.head(CECMODS.size)
df_inverters = INVERTERS.T.head(INVERTERS.size)

# family of modules
module_brand = 'Canadian'
modules = df_modules[df_modules.index.str.startswith(module_brand)]

module_mono = CECMODS['Canadian_Solar_Inc__CS6X_300P']
module_poly = CECMODS['Canadian_Solar_Inc__CS6X_300M']

#family of inverters
inverter_brand = 'SMA'
inverters = df_inverters[df_inverters.index.str.startswith(inverter_brand)]

inverter = INVERTERS['SMA_America__STP_60_US_10__480V_']

#%% Weather and solar data from pvgis (not tmy)

LATITUDE, LONGITUDE = 40.5, -3.75 # IES coordinates
data, months, inputs, meta = pvlib.iotools.get_pvgis_tmy(latitude = LATITUDE, 
                                                         longitude = LONGITUDE)

#solar position
data.index = TIMES
solar_position = pvlib.solarposition.get_solarposition(time = TIMES, 
                                                       latitude = LATITUDE, 
                                                       longitude = LONGITUDE)
solar_zenith = solar_position['apparent_zenith']
solar_azimuth = solar_position['azimuth']

#tracker positions
tracker = pvlib.tracking.singleaxis(apparent_zenith = solar_zenith, 
                                    apparent_azimuth = solar_azimuth)

surface_tilt = tracker['surface_tilt']
surface_azimuth = tracker['surface_azimuth']
aoi = tracker['aoi']

#irradiance
