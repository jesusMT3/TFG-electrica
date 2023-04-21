# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 10:21:14 2023

https://re.jrc.ec.europa.eu/pvg_tools/en/#TMY

@author: Jesús
"""

# Libraries

import warnings, webbrowser, os, sys
from pvlib import pvsystem, iotools, location, modelchain, ivtools
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS as PARAMS
import tkinter as tk
from tkinter import filedialog
from pvlib.bifacial.pvfactors import pvfactors_timeseries
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

def main():
    
    # Global variables and objects
    global my_module, my_inverter
    
    # Create main window
    root = tk.Tk()
    root.title('main')
    
    # PVGIS TMY data website
    url_button = tk.Button(root, text="PVGIS data web site", command=open_url)
    url_button.pack()
    
    # Load meteorological data
    button_load_data = tk.Button(root, text='Load data', command=load_data)
    button_load_data.pack()
    
    # Choose solar pannels and inverters, and the temperature models
    my_module = bifacial_modules[module]
    my_inverter = cec_inverters[inverter]
    
    # Calculate model
    button_calc_model = tk.Button(root, text = 'Calculate model', command = calc_model)
    button_calc_model.pack()
    
    # create a tkinter frame for the plot
    plot_frame = tk.Frame(root)
    plot_frame.pack()
    
    # call the modified function to get the Figure instance
    plot_button = tk.Button(root, text = 'Plot monthly', command = lambda: plot_on_canvas(canvas))
    plot_button.pack()
    
    canvas = tk.Canvas(root, width=10*100, height=6*100)
    canvas.pack()

    # start the tkinter event loop
    root.mainloop()

####################################################################################################
# Functions

# Load data from .epw file
def load_data():
    
    global data, metadata, site_location, solar_position
    meteo_file = filedialog.askopenfilename()
    data, metadata = iotools.read_epw(meteo_file, coerce_year = 2020)
    site_location = location.Location(latitude = metadata['latitude'],
                                      longitude = metadata['longitude'])

    solar_position = site_location.get_solarposition(data.index)
    return data, metadata, site_location, solar_position

# Open TMY data URL    
def open_url():
    url = "https://re.jrc.ec.europa.eu/pvg_tools/en/#TMY"
    webbrowser.open_new(url)
    
# Plot energy data by months graph bar
def plot_monthly(units, title):
    global fig
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
    
    fig, ax = plt.subplots(figsize=(10, 6))

    array_monthly.plot(kind='bar', ax=ax)

    # add the values to the top of each bar
    for i in ax.containers:
        ax.bar_label(i, label_type='edge')

    ax.set_ylabel('Energy [' + units + ']')
    ax.set_title(title)

    plt.tight_layout()

    return fig


# Plot energy data by hourly power data
def plot_daily(day, units):
    
    df_meteo = pd.DataFrame(data.loc[day])
    df_day = pd.DataFrame(results.loc[day])
    df_day = df_day.clip(lower=0)
    
    if units == 'W':
        df_day /= 1
    
    elif units == 'kW':
        df_day /= 1000
        
    elif units == 'MW':
        df_day /= 1000000
    
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
    ax1.set_ylabel(units)
    ax2.set_ylabel('W/m$^2$')
    
    # add legend
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # show the plot
    plt.tight_layout()
    plt.show()
    
def plot_on_canvas(frame):
    # Remove any previous plot from the frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Get the figure from the plot_monthly function
    fig = plot_monthly('kWh', 'Monthly Energy Data')
    
    # Get the Tkinter widget for the figure
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    
    # Pack the canvas widget inside the frame
    canvas_widget.pack(side="top", fill="both", expand=True)
    
    # Set the row and column of the frame to expand with window size changes
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
def calc_model():
    
    global results
    
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