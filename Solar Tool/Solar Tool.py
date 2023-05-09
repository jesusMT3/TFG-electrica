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

# Global variables
axis_tilt = 0
axis_azimuth = 180
max_angle = 60
pvrow_height = 3
pvrow_width = 4
albedo = 0.2
bifaciality = 0.75
pannel_azimuth = 180
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
    global my_module, opts_dict, my_inverter, location_dict
       
    # Create main window
    
    root = tk.Tk()
    root.title('Bifacial Tool')
    
    # Dictionaries for changing variables
    opts_dict = {"type_plot": tk.StringVar(value = 'Monthly Energy'),
                 "module": tk.StringVar(value = module),
                 "inverter": tk.StringVar(value = inverter),
                 "tracking": tk.StringVar(value = 'Backtrack'),
                 'latitude': tk.DoubleVar(value = 40.45),
                 'longitude': tk.DoubleVar(value = -3.73),
                 'modules_per_string': tk.IntVar(value = 4),
                 'strings': tk.IntVar(value = 4),
                 'gcr': tk.DoubleVar(value = 0.27)}
    
    # TopLevel for the columns
    options_window = tk.Frame(root)
    plot_window = tk.Frame(root)
    var_window = tk.Frame(root)
    
    # Options
    # Latitude and longitude settings
    lat_label = tk.Label(options_window, text="Set latitude:")
    lat_label.pack()
    lat_entry = tk.Entry(options_window, textvariable=opts_dict['latitude'])
    lat_entry.pack()
    lat_entry.bind("<FocusOut>", lambda event: opts_dict['latitude'].set(float(lat_entry.get())))

    lon_label = tk.Label(options_window, text="Set longitude")
    lon_label.pack()
    lon_entry = tk.Entry(options_window, textvariable=opts_dict['longitude'])
    lon_entry.pack()
    lon_entry.bind("<FocusOut>", lambda event: opts_dict['longitude'].set(float(lon_entry.get())))
    
    # Choose options
    module_label = tk.Label(options_window, text="Module selector:")
    module_label.pack()
    module_selector = tk.OptionMenu(options_window, opts_dict["module"], *bifacial_modules)
    module_selector.pack()
    
    inverter_label = tk.Label(options_window, text="Inverter selector:")
    inverter_label.pack()
    inverter_label = tk.OptionMenu(options_window, opts_dict["inverter"], *cec_inverters)
    inverter_label.pack()
    
    inverter_label = tk.Label(options_window, text="Tracking options:")
    inverter_label.pack()
    tracking_selector = tk.OptionMenu(options_window, opts_dict["tracking"], *track_options)
    tracking_selector.pack()
    
    # Calculate model
    calc_label = tk.Label(options_window, text="Calculate model:")
    calc_label.pack()
    button_calc_model = tk.Button(options_window, text = 'Calculate', command = calc_model)
    button_calc_model.pack()
    
    # Plot
    # Label to select type of plot
    type_plot_label = tk.Label(plot_window, text="Plot type:")
    type_plot_label.pack()
    type_plot = tk.OptionMenu(plot_window, opts_dict["type_plot"], *type_options)
    type_plot.pack()
    
    # call the modified function to get the Figure instance
    plot_button = tk.Button(plot_window, text = 'Plot', command = lambda: plot_on_canvas(canvas, opts_dict))
    plot_button.pack()
    
    # Plot Canvas
    canvas = tk.Canvas(plot_window, width=900, height=500)
    canvas.pack_propagate(0)
    canvas.pack()
    
    # Save results button
    save_button = tk.Button(plot_window, text = 'Save results', command = save_results)
    save_button.pack()
    
    # Variables
    # modules per string and strings
    mods_label = tk.Label(var_window, text="Modules per string:")
    mods_label.pack()
    mods_entry = tk.Entry(var_window, textvariable=opts_dict['modules_per_string'])
    mods_entry.pack()
    mods_entry.bind("<FocusOut>", lambda event: opts_dict['modules_per_string'].set(int(mods_entry.get())))
    
    strings_label = tk.Label(var_window, text="Strings:")
    strings_label.pack()
    strings_entry = tk.Entry(var_window, textvariable=opts_dict['strings'])
    strings_entry.pack()
    strings_entry.bind("<FocusOut>", lambda event: opts_dict['strings'].set(int(strings_entry.get())))
    
    # Set GCR
    gcr_label = tk.Label(var_window, text="Ground to Coverage Ratio:")
    gcr_label.pack()
    gcr_entry = tk.Entry(var_window, textvariable=opts_dict['gcr'])
    gcr_entry.pack()
    gcr_entry.bind("<FocusOut>", lambda event: opts_dict['gcr'].set(int(gcr_entry.get())))
    
    # Place main Frame and run mainloop
    options_window.grid(row = 0, column = 0)
    plot_window.grid(row = 0, column = 1)
    var_window.grid(row = 0, column = 2)
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
    
    total = total_results['Energy'].values[0]
    text = f'Total: {total:.2f} MWh'
    plt.text(0, 0, text, fontsize = 12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

    # add the values to the top of each bar
    for i in ax.containers:
        ax.bar_label(i, label_type='edge')

    ax.set_ylabel('[kWh]')
    ax.set_title('Monthly energy generated')

    # plt.tight_layout()
    return fig

def plot_yield():
    global fig
    
    modules_per_string = opts_dict['modules_per_string'].get()
    strings = opts_dict['strings'].get()
    
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
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    array_monthly['bifacial'].plot(kind='bar', ax=ax)
    
    # Print total
    total = total_results['Yield'].values[0]
    text = f'Total: {total:.2f} h'
    plt.text(0, 0, text, fontsize = 12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

    # add the values to the top of each bar
    for i in ax.containers:
        ax.bar_label(i, label_type='edge')

    ax.set_ylabel('[kWh/kWp]')
    ax.set_title('Yield ratio')

    # plt.tight_layout()
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
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    bif_gains.plot(kind='bar', ax=ax)
    
    # Print total
    total = total_results['Bifacial gains'].values[0]
    text = f'Total: {total:.2f} %'
    plt.text(0, 0, text, fontsize = 12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

    # add the values to the top of each bar
    for i in ax.containers:
        ax.bar_label(i, label_type='edge')


    ax.set_ylabel('[%]')
    ax.set_title('Bifacial gains')

    # plt.tight_layout()
    return fig

    
def plot_pr():
    global fig
    pr = pd.DataFrame({})
    
    modules_per_string = opts_dict['modules_per_string'].get()
    strings = opts_dict['strings'].get()
    
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
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    pr.plot(kind='bar', ax=ax)

    # Print total
    total = total_results['PR'].values[0]
    text = f'Total: {total:.2f} pu'
    plt.text(0, 0, text, fontsize = 12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
    
    # add the values to the top of each bar
    for i in ax.containers:
        ax.bar_label(i, label_type='edge')


    ax.set_ylabel('[%]')
    ax.set_title('Performance Ratio')

    # plt.tight_layout()
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
    
    modules_per_string = opts_dict['modules_per_string'].get()
    strings = opts_dict['strings'].get()
    gcr = opts_dict['gcr'].get()
    
    global data, months_selected, inputs, metadata 
    data, months_selected, inputs, metadata = iotools.get_pvgis_tmy(opts_dict['latitude'].get(), 
                                                                    opts_dict['longitude'].get(),
                                                                    map_variables=True)
    
    # get the latest year in the index
    latest_year = max(data.index.year)
    
    # create a new index with the latest year
    new_index = data.index.map(lambda x: x.replace(year=latest_year))
    
    # set the new index on the dataframe
    data = data.set_index(new_index)
    
    site_location = location.Location(latitude = opts_dict['latitude'].get(),
                                      longitude = opts_dict['longitude'].get())

    solar_position = site_location.get_solarposition(data.index)
    
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

# Save total results
def save_results():
    df_results = pd.DataFrame({})
    df_results = total_results.T
    df_results = df_results.rename(columns = {0: 'Value'})
    df_results['units'] = ('MWh', 'h', '%', 'pu')
    
    file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    df_results.to_csv(file_path, index = True)
    
if __name__ == "__main__":
    main()