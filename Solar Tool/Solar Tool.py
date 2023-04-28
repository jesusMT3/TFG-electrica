# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 10:21:14 2023

https://re.jrc.ec.europa.eu/pvg_tools/en/#TMY

@author: Jesús
"""

# Libraries

import warnings, webbrowser, os
from pvlib import pvsystem, iotools, location, modelchain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS as PARAMS
import tkinter as tk
from tkinter import filedialog
from pvlib.bifacial.pvfactors import pvfactors_timeseries
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# supressing shapely warnings that occur on import of pvfactors
warnings.filterwarnings(action='ignore', module='pvfactors')

# IES ISI logo
ISI_logo = os.getcwd() + '\IES_logo.jpg'

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

type_options = ['Monthly Energy', 'Yield', 'Bifacial Gain', 'Performance Ratio']
track_options = ['Track', 'Backtrack', 'None']

module = 'LONGi_Green_Energy_Technology_Co___Ltd__LR6_72BP_350M'
inverter = 'ABB__PVI_10_0_I_OUTD_x_US_480_y_z__480V_'
temp_model_parameters = PARAMS['sapm']['open_rack_glass_glass']
cec_modules = pvsystem.retrieve_sam('CECMod')
cec_inverters = pvsystem.retrieve_sam('cecinverter')
bifacial_modules = cec_modules.T[cec_modules.T['Bifacial'] == 1].T

my_module = bifacial_modules[module]
my_inverter = cec_inverters[inverter]

def main():
    
    # Global variables and objects
    global my_module, my_inverter, opts_dict
       
    # Create main window
    root = tk.Tk()
    root.title('main')
    
    opts_dict = {"type_plot": tk.StringVar(value = 'Monthly Energy'),
                 "module": tk.StringVar(value = module),
                 "inverter": tk.StringVar(value = inverter),
                 "tracking": tk.StringVar(value = 'Backtrack')}
    
    # PVGIS TMY data website
    url_label = tk.Label(root, text="1. Access PVIS data web site to gather .epw file data of location:")
    url_label.pack()
    url_button = tk.Button(root, text="PVGIS data web site", command=open_url)
    url_button.pack()
    
    # Load meteorological data
    url_load_data = tk.Label(root, text="2. Load .epw file containing TMY data from desired location:")
    url_load_data.pack()
    button_load_data = tk.Button(root, text='Load data', command=load_data)
    button_load_data.pack()
    
    # Choose options
    module_label = tk.Label(root, text="Module selector:")
    module_label.pack()
    module_selector = tk.OptionMenu(root, opts_dict["module"], *bifacial_modules)
    module_selector.pack()
    
    inverter_label = tk.Label(root, text="Inverter selector:")
    inverter_label.pack()
    inverter_label = tk.OptionMenu(root, opts_dict["inverter"], *cec_inverters)
    inverter_label.pack()
    
    tracking_label = tk.OptionMenu(root, opts_dict["tracking"], *track_options)
    tracking_label.pack()
    
    # Calculate model
    button_calc_model = tk.Button(root, text = 'Calculate model', command = calc_model)
    button_calc_model.pack()
    
    # create a tkinter frame for the plot
    plot_frame = tk.Frame(root)
    plot_frame.pack()
    
    # Label to select type of plot
    type_plot_label = tk.Label(root, text="Plot type:")
    type_plot_label.pack()
    type_plot = tk.OptionMenu(root, opts_dict["type_plot"], *type_options)
    type_plot.pack()
    
    # call the modified function to get the Figure instance
    plot_button = tk.Button(root, text = 'Plot', command = lambda: plot_on_canvas(canvas, opts_dict))
    plot_button.pack()
    
    canvas = tk.Canvas(root, width=900, height=500)
    canvas.pack_propagate(0)
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
def plot_monthly():
    
    global fig
    
    df = pd.DataFrame(results)
    
    # Cut powers lower to zero
    df = df.clip(lower=0)
    
    # Get energy into kWh
    df /= 1000
    
    # Resample data into monthly energy produced
    array_monthly = df.resample('M').sum()
    
    # Reshape the dataframe 
    new_index = pd.Index([d.strftime('%Y-%m') for d in array_monthly.index])
    array_monthly.index = new_index
    
    fig, ax = plt.subplots(figsize=(10, 6))

    array_monthly['bifacial'].plot(kind='bar', ax=ax)

    # add the values to the top of each bar
    for i in ax.containers:
        ax.bar_label(i, label_type='edge')

    ax.set_ylabel('[kWh]')
    ax.set_title('Monthly energy generated')

    plt.tight_layout()
    return fig

def plot_yield():
    global fig
    
    pp = my_module['STC'] * modules_per_string * strings
    df = pd.DataFrame(results)
    
    # Cut powers lower to zero
    df = df.clip(lower=0)
    
    # Get energy per peak power
    df /= pp
    
    # Resample data into monthly energy produced
    array_monthly = df.resample('M').sum()
    
    # Reshape the dataframe 
    new_index = pd.Index([d.strftime('%Y-%m') for d in array_monthly.index])
    array_monthly.index = new_index
    
    fig, ax = plt.subplots(figsize=(10, 6))
    array_monthly['bifacial'].plot(kind='bar', ax=ax)

    # add the values to the top of each bar
    for i in ax.containers:
        ax.bar_label(i, label_type='edge')

    ax.set_ylabel('[kWh/kWp]')
    ax.set_title('Yield ratio')

    plt.tight_layout()
    return fig

def plot_bifacial_gains():
    
    global fig
    
    df = pd.DataFrame(results)
    
    # Cut powers lower to zero
    df = df.clip(lower=0)
    
    # Resample data into monthly energy produced
    array_monthly = df.resample('M').sum()
    bif_gains = 100 * (array_monthly['bifacial'] - array_monthly['non bifacial']) / array_monthly['bifacial']
    
    # Reshape the dataframe 
    new_index = pd.Index([d.strftime('%Y-%m') for d in array_monthly.index])
    bif_gains.index = new_index
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bif_gains.plot(kind='bar', ax=ax)

    # add the values to the top of each bar
    for i in ax.containers:
        ax.bar_label(i, label_type='edge')


    ax.set_ylabel('[%]')
    ax.set_title('Bifacial gains')

    plt.tight_layout()
    return fig

    
def plot_pr():
    global fig
    pr = pd.DataFrame({})
    
    df = pd.DataFrame(results)
    
    # Cut powers lower to zero
    df = df.clip(lower=0)
    
    # Resample data into monthly energy produced
    array_monthly = df.resample('M').sum()
    dc_power = my_module['STC'] * strings * modules_per_string
    pr = 100 * ((array_monthly['bifacial'] / dc_power) / (array_monthly['effective irradiance'] / 1000))
    
    # Reshape the dataframe 
    new_index = pd.Index([d.strftime('%Y-%m') for d in array_monthly.index])
    pr.index = new_index
    
    fig, ax = plt.subplots(figsize=(10, 6))
    pr.plot(kind='bar', ax=ax)

    # add the values to the top of each bar
    for i in ax.containers:
        ax.bar_label(i, label_type='edge')


    ax.set_ylabel('[%]')
    ax.set_title('Performance Ratio')

    plt.tight_layout()
    return fig
    
def plot_on_canvas(frame, opts_dict):
    
    fig = plt.Figure()
    
    # Remove any previous plot from the frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Get the figure from the plot_monthly function
    if (opts_dict['type_plot'].get() == 'Monthly Energy'):
        fig = plot_monthly()
        
    elif (opts_dict['type_plot'].get() == 'Yield'):        
        fig = plot_yield()
        
    elif (opts_dict['type_plot'].get() == 'Bifacial Gain'): 
        fig = plot_bifacial_gains()
        
    elif (opts_dict['type_plot'].get() == 'Performance Ratio'): 
        fig = plot_pr()
    
    # Get the Tkinter widget for the figure
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    
    # Pack the canvas widget inside the frame
    canvas_widget.pack(side="top", fill="both", expand=True)
    
    # Set the row and column of the frame to expand with window size changes
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

def calc_model():
    
    global results, total_results
    
    # Update parameters
    my_module = bifacial_modules[opts_dict['module'].get()]
    my_inverter = cec_inverters[opts_dict['inverter'].get()]
    track = opts_dict['tracking'].get()
    
    results = pd.DataFrame({})
    total_results = pd.DataFrame({})
    
    if track == 'Backtrack':
        sat_mount = pvsystem.SingleAxisTrackerMount(axis_tilt=axis_tilt,
                                                axis_azimuth=axis_azimuth,
                                                max_angle=max_angle,
                                                backtrack=True,
                                                gcr=gcr)
    
        # created for use in pvfactors timeseries
        orientation = sat_mount.get_orientation(solar_position['apparent_zenith'],
                                            solar_position['azimuth'])
        
    elif track == 'Track':
        sat_mount = pvsystem.SingleAxisTrackerMount(axis_tilt=axis_tilt,
                                                axis_azimuth=axis_azimuth,
                                                max_angle=max_angle,
                                                backtrack=False,
                                                gcr=gcr)
    
        # created for use in pvfactors timeseries
        orientation = sat_mount.get_orientation(solar_position['apparent_zenith'],
                                            solar_position['azimuth'])
        
    elif track == 'None':
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
    
    # Run model without bifacial gains
    irrad['effective_irradiance'] = irrad['total_abs_front']
    mc_bifi.run_model_from_effective_irradiance(irrad)
    results_non_bifacial = pd.DataFrame(mc_bifi.results.ac)
    
    # Run model with bifacial gains
    irrad['effective_irradiance'] = irrad['total_abs_front'] + (irrad['total_abs_back'] * bifaciality)
    mc_bifi.run_model_from_effective_irradiance(irrad)
    results_bifacial = pd.DataFrame(mc_bifi.results.ac)
    
    # Create results dataframe
    results = pd.DataFrame(index = data.index)
    results['bifacial'] = results_bifacial
    results['non bifacial'] = results_non_bifacial
    results['effective irradiance'] = irrad['effective_irradiance']
    
    # Compute total results
    dc_power = my_module['STC'] * strings * modules_per_string
    total_results['Energy'] = results_bifacial.sum() / 1e6
    total_results['Yield'] = results_bifacial.sum() / dc_power
    total_results['Bifacial gains'] = ((results_bifacial.sum() - results_non_bifacial.sum()) / results_bifacial.sum()) * 100
    total_results['PR'] = (results_bifacial.sum() / irrad['effective_irradiance'].sum()) / (dc_power / 1000)
    
    return results
    
if __name__ == "__main__":
    main()