# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 17:20:36 2023

@author: Jesús
"""

import pandas as pd
from pvlib import pvsystem
from pvlib import location
from pvlib import modelchain
from pvlib import tracking
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS as PARAMS
from pvlib.bifacial.pvfactors import pvfactors_timeseries
import warnings

# supressing shapely warnings that occur on import of pvfactors
warnings.filterwarnings(action='ignore', module='pvfactors')

# weather data
latitude, longitude, tz = 40.453, -3.727, 'UTC/GMT+2'
site_location = location.Location(latitude, longitude)
# time dataframe
times = pd.date_range('2021-06-21', '2021-6-22', freq='1T')
# solar position and irradiance data
solar_position = site_location.get_solarposition(times)
cs = site_location.get_clearsky(times)

# create site system characteristics
axis_tilt = 0
axis_azimuth = 180
gcr = 0.35
max_angle = 60
pvrow_height = 3
pvrow_width = 4
albedo = 0.2
bifaciality = 0.75

# load temperature parameters and module/inverter specifications
temp_model_parameters = PARAMS['sapm']['open_rack_glass_glass']
cec_modules = pvsystem.retrieve_sam('CECMod')
cec_module = cec_modules['Trina_Solar_TSM_300DEG5C_07_II_']
cec_inverters = pvsystem.retrieve_sam('cecinverter')
cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']

# Create tracker data
sat_mount = pvsystem.SingleAxisTrackerMount(axis_tilt=axis_tilt,
                                            axis_azimuth=axis_azimuth,
                                            max_angle=max_angle,
                                            backtrack=True,
                                            gcr=gcr)

# created for use in pvfactors timeseries
orientation = sat_mount.get_orientation(solar_position['apparent_zenith'],
                                        solar_position['azimuth'])

# get bifacial irradiance
irrad = pvfactors_timeseries(solar_position['azimuth'],
                             solar_position['apparent_zenith'],
                             orientation['surface_azimuth'],
                             orientation['surface_tilt'],
                             axis_azimuth,
                             times,
                             cs['dni'],
                             cs['dhi'],
                             gcr,
                             pvrow_height,
                             pvrow_width,
                             albedo,
                             n_pvrows=3,
                             index_observed_pvrow=1
                             )

irrad = pd.concat(irrad, axis = 1)

# create bifacial effective irradiance using aoi-corrected timeseries values
irrad['effective_irradiance'] = (irrad['total_abs_front'] + (irrad['total_abs_back'] * bifaciality))

