# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 17:00:38 2023

@author: Jesús
"""

import pandas as pd
from pvlib import location
from pvlib import tracking
from pvlib.bifacial.pvfactors import pvfactors_timeseries
from pvlib import temperature
from pvlib import pvsystem
from pvlib import iotools
import matplotlib.pyplot as plt
import warnings, os

# supressing shapely warnings that occur on import of pvfactors
warnings.filterwarnings(action='ignore', module='pvfactors')

# custom location (IES)
# EPW data
file_path = os.path.dirname(__file__) + r'\tmy_40.453_-3.727_2005_2020.epw'
df_tmy, metadata = iotools.read_epw(file_path, coerce_year = 2021)

# times dataframe
times = pd.date_range('2021-06-21', '2021-06-22', freq='1T')

#solar data
site_location = location.Location(latitude = metadata['latitude'], longitude = metadata['longitude'])
solar_position = site_location.get_solarposition(times)

# clear sky data
cs = pd.DataFrame(site_location.get_clearsky(times))

# tracker data
gcr = 0.35
max_phi = 60
tracker_data = tracking.singleaxis(apparent_zenith = solar_position['apparent_zenith'], 
                                   apparent_azimuth = solar_position['azimuth'],
                                   max_angle=max_phi,
                                   backtrack=True,
                                   gcr=gcr)

# the pvfactors engine for both front and rear-side absorbed irradiance
axis_azimuth = 180
pvrow_height = 3
pvrow_width = 4
albedo = 0.2

# get bifacial irradiance
irrad = pvfactors_timeseries(solar_azimuth = solar_position['azimuth'], 
                             solar_zenith = solar_position['apparent_zenith'], 
                             surface_azimuth = tracker_data['surface_azimuth'], 
                             surface_tilt = tracker_data['surface_tilt'], 
                             axis_azimuth = axis_azimuth, 
                             timestamps = cs.index, 
                             dni = cs['dni'], 
                             dhi = cs['dhi'], 
                             gcr = gcr, 
                             pvrow_height = pvrow_height, 
                             pvrow_width = pvrow_width, 
                             albedo = albedo,
                             n_pvrows = 3,
                             index_observed_pvrow = 1)

irrad = pd.concat(irrad, axis = 1)

# using bifaciality factor and pvfactors results, create effective irradiance
bifaciality = 0.75
effective_irrad_bifi = irrad['total_abs_front'] + (irrad['total_abs_back']
                                                   * bifaciality)

# get cell temperature using the Faiman model
temp_cell = temperature.faiman(effective_irrad_bifi, temp_air=25,
                               wind_speed=1)

# using the pvwatts_dc model and parameters detailed above,
# set pdc0 and return DC power for both bifacial and monofacial
pdc0 = 1
gamma_pdc = -0.0043
pdc_bifi = pvsystem.pvwatts_dc(effective_irrad_bifi,
                               temp_cell,
                               pdc0,
                               gamma_pdc=gamma_pdc
                               ).fillna(0)
pdc_bifi.plot(title='Bifacial Simulation on June Solstice', ylabel='DC Power')

effective_irrad_mono = irrad['total_abs_front']
pdc_mono = pvsystem.pvwatts_dc(effective_irrad_mono,
                               temp_cell,
                               pdc0,
                               gamma_pdc=gamma_pdc
                               ).fillna(0)

# plot monofacial results
plt.figure()
plt.title('Bifacial vs Monofacial Simulation - June Solstice')
pdc_bifi.plot(label='Bifacial')
pdc_mono.plot(label='Monofacial')
plt.ylabel('DC Power')
plt.legend()