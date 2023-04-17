# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 10:21:14 2023

https://re.jrc.ec.europa.eu/pvg_tools/en/#TMY

@author: Jesús
"""

# Libraries

import warnings
from pvlib import pvsystem, iotools, location, modelchain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS as PARAMS
import tkinter as tk
from tkinter import filedialog
from pvlib.bifacial.pvfactors import pvfactors_timeseries
import pandas as pd
import matplotlib.pyplot as plt

# supressing shapely warnings that occur on import of pvfactors
warnings.filterwarnings(action='ignore', module='pvfactors')

# Global variables
backtrack = True
axis_tilt = 0
axis_azimuth = 180
gcr = 0.35
max_angle = 60
pvrow_height = 3
pvrow_width = 4
albedo = 0.2
bifaciality = 0.75
modules_per_string = 10
strings = 4
pannel_azimuth = 30
pannel_tilt = 30
albedo = 0.2


def main():
    
    # Global variables and objects
<<<<<<< HEAD
    global site_location, orientation, irrad, system, array_monthly, array_power, cec_inverters, results
    
    # Load meteorological data
    load_data()
     
=======
    global site_location, orientation, irrad, system, array_monthly, array_power, cec_inverters
    module = 'LONGi_Green_Energy_Technology_Co___Ltd__LR6_72BP_350M'
    inverter = 'ABB__PVI_10_0_I_OUTD_x_US_480_y_z__480V_'
    
    # Load meteorological data
    meteo_file = tk.filedialog.askopenfilename()
    data, metadata = iotools.read_epw(meteo_file, coerce_year = 2020)
    site_location = location.Location(latitude = metadata['latitude'],
                                      longitude = metadata['longitude'])
      
    solar_position = site_location.get_solarposition(data.index)
    
>>>>>>> 92fba3471085c8f94a2c07aa68f6b4e175ebad37
    # Choose solar pannels and inverters, and the temperature models
    temp_model_parameters = PARAMS['sapm']['open_rack_glass_glass']
    cec_modules = pvsystem.retrieve_sam('CECMod')
    cec_inverters = pvsystem.retrieve_sam('cecinverter')
    
    bifacial_modules = cec_modules.T[cec_modules.T['Bifacial'] == 1].T
    module = bifacial_modules[module]
    inverter = cec_inverters[inverter]
    
    if backtrack == True:
        sat_mount = pvsystem.SingleAxisTrackerMount(axis_tilt=axis_tilt,
                                                axis_azimuth=axis_azimuth,
                                                max_angle=max_angle,
                                                backtrack=True,
                                                gcr=gcr)
    
        # created for use in pvfactors timeseries
        orientation = sat_mount.get_orientation(solar_position['apparent_zenith'],
                                            solar_position['azimuth'])
    else:
        sat_mount = pvsystem.FixedMount(surface_tilt = pannel_tilt,
                                        surface_azimuth = pannel_azimuth)
        
        orientation = sat_mount.get_orientation(solar_position['apparent_zenith'],
                                            solar_position['azimuth'])

    # get bifacial irradiance
    irrad = pvfactors_timeseries(solar_position['azimuth'],
                                 solar_position['apparent_zenith'],
                                 orientation['surface_azimuth'],
                                 orientation['surface_tilt'],
                                 axis_azimuth,
                                 data.index,
                                 data['dni'],
                                 data['dhi'],
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

    # dc arrays
    array = pvsystem.Array(mount=sat_mount,
                           module_parameters = module,
                           temperature_model_parameters = temp_model_parameters,
                           modules_per_string = modules_per_string,
                           strings = strings)
    
    # create system object
    system = pvsystem.PVSystem(arrays = [array],
                               inverter_parameters = inverter,
                               modules_per_string = modules_per_string,
                               strings_per_inverter = strings,
                               albedo = albedo)
    
    mc_bifi = modelchain.ModelChain(system, site_location, aoi_model='no_loss')
    mc_bifi.run_model_from_effective_irradiance(irrad)
    results = pd.DataFrame(mc_bifi.results.ac)
    
    # plot results
    plot_monthly('kWh')
    plot_daily('2020-12-21')

def load_data():
    global data, metadata, site_location, solar_position
    meteo_file = tk.filedialog.askopenfilename()
    data, metadata = iotools.read_epw(meteo_file, coerce_year = 2020)
    site_location = location.Location(latitude = metadata['latitude'],
                                      longitude = metadata['longitude'])

    solar_position = site_location.get_solarposition(data.index)

def plot_monthly(units):
    
    df = pd.DataFrame(results)
    
    # Cut powers lower to zero
    df = df.clip(lower=0)
    
    # Reshape with units parameter
    if units == 'Wh':
        df /= 1
    
    elif units == 'kWh':
        df /= 1000
        
    elif units == 'MWh':
        df /= 1000000
    
    # Resample data into monthly energy produced
    array_monthly = df.resample('M').sum()
    
    # Reshape the dataframe 
    new_index = pd.Index([d.strftime('%Y-%m') for d in array_monthly.index])
    array_monthly.index = new_index
    
    ax = array_monthly.plot(kind='bar', figsize=(10, 6))
    
    # add the values to the top of each bar
    for i in ax.containers:
        ax.bar_label(i, label_type='edge')
    
    plt.ylabel('Energy [' + units + ']')
    plt.tight_layout()

def plot_daily(day):
    
    global df_meteo, df_day
    df_meteo = pd.DataFrame(data.loc[day])
    df_day = pd.DataFrame(results.loc[day])
    df_day = df_day.clip(lower=0)
    
    
    
    

if __name__ == "__main__":
    main()