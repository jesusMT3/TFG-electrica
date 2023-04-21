# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 10:21:14 2023

https://re.jrc.ec.europa.eu/pvg_tools/en/#TMY

@author: Jesús
"""

# Libraries

import warnings
from pvlib import pvsystem, iotools, location, modelchain, ivtools
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

module = 'LONGi_Green_Energy_Technology_Co___Ltd__LR6_72BP_350M'
inverter = 'ABB__PVI_10_0_I_OUTD_x_US_480_y_z__480V_'
temp_model_parameters = PARAMS['sapm']['open_rack_glass_glass']
cec_modules = pvsystem.retrieve_sam('CECMod')
cec_inverters = pvsystem.retrieve_sam('cecinverter')
bifacial_modules = cec_modules.T[cec_modules.T['Bifacial'] == 1].T

results = pd.DataFrame()

def main():
    
    # Global variables and objects
    global my_module, my_inverter, results, temp_model_parameters
    
    # Load meteorological data
    load_data()
    
    # Choose solar pannels and inverters, and the temperature models
    my_module = bifacial_modules[module]
    my_inverter = cec_inverters[inverter]
    
    results = calc_model()
    
    # plot results
    title = 'IES data'
    plot_monthly('kWh', title)
    plot_daily('2020-07-21')

def load_data():
    global data, metadata, site_location, solar_position
    meteo_file = filedialog.askopenfilename()
    data, metadata = iotools.read_epw(meteo_file, coerce_year = 2020)
    site_location = location.Location(latitude = metadata['latitude'],
                                      longitude = metadata['longitude'])

    solar_position = site_location.get_solarposition(data.index)


def plot_monthly(units, title):
    
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
    plt.title(title)
    plt.tight_layout()

def plot_daily(day):
    
    global df_merged
    
    df_meteo = pd.DataFrame(data.loc[day])
    df_day = pd.DataFrame(results.loc[day])
    df_day = df_day.clip(lower=0)
    
    df_merged = pd.merge(df_day, df_meteo[['dhi', 'dni']], left_index=True, right_index=True)
    df_merged = df_merged.rename(columns = {0: 'Power'})
    df_merged = df_merged[df_merged['Power'] > 0]
    # Plot data
    fig, ax1 = plt.subplots(figsize = (10, 6))

    # create second axis
    ax2 = ax1.twinx()
    
    # plot df_day on the left axis
    ax1.plot(df_merged.index, df_merged['Power'], color='blue', label='Power')
    
    # plot df_meteo on the right axis
    ax2.plot(df_merged.index, df_merged['dhi'], color='red', label='dhi')
    ax2.plot(df_merged.index, df_merged['dni'] , color='green', label='dni')
    
    # Make the axis better
    
    # set axis labels
    ax1.set_xlabel(day)
    ax1.set_ylabel('kWh')
    ax2.set_ylabel('W/m$^2$')
    
    # add legend
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # show the plot
    plt.tight_layout()
    plt.show()
    
def calc_model():
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
                           module_parameters = my_module,
                           temperature_model_parameters = temp_model_parameters,
                           modules_per_string = modules_per_string,
                           strings = strings)
    
    # create system object
    system = pvsystem.PVSystem(arrays = [array],
                               inverter_parameters = my_inverter,
                               modules_per_string = modules_per_string,
                               strings_per_inverter = strings,
                               albedo = albedo)
    
    mc_bifi = modelchain.ModelChain(system, site_location, aoi_model='no_loss')
    mc_bifi.run_model_from_effective_irradiance(irrad)
    results = pd.DataFrame(mc_bifi.results.ac)
    return results
    
if __name__ == "__main__":
    main()