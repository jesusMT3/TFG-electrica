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
from tkinter import filedialog, ttk
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
bifaciality = 0.75

type_options = ['Monthly Energy', 'Yield', 'Bifacial Gain', 'Performance Ratio']
track_options = ['Track', 'Backtrack', 'Fixed tilt']

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
    global my_module, opts_dict, my_inverter, location_dict, flag_inicio
       
    # Create main window
    
    root = tk.Tk()
    root.title('Bifacial Tool')
    
    # Set full screen height and width
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")
    
    # Dictionaries for changing variables
    opts_dict = {"type_plot": tk.StringVar(value = 'Monthly Energy'),
                 "module": tk.StringVar(value = module),
                 "inverter": tk.StringVar(value = inverter),
                 "tracking": tk.StringVar(value = 'Backtrack'),
                 'latitude': tk.DoubleVar(value = 40.45),
                 'longitude': tk.DoubleVar(value = -3.73),
                 'modules_per_string': tk.IntVar(value = 4),
                 'strings': tk.IntVar(value = 4),
                 'gcr': tk.DoubleVar(value = 0.27),
                 'pannel_azimuth': tk.DoubleVar(value = 180),
                 'pannel_tilt': tk.DoubleVar(value = 30),
                 'albedo': tk.DoubleVar(value = 0.2)}
    
    # TopLevel for the columns
    options_window = tk.Frame(root)
    plot_window = tk.Frame(root)
    
    # Options
    # Latitude and longitude settings
    lat_lon = tk.Frame(options_window, border = 50)
    
    lat_label = tk.Label(lat_lon, text="Set latitude: ")
    lat_label.grid(row = 0, column = 0)
    lat_entry = tk.Entry(lat_lon, textvariable=opts_dict['latitude'])
    lat_entry.grid(row = 0, column = 1)
    lat_entry.bind("<FocusOut>", lambda event: opts_dict['latitude'].set(float(lat_entry.get())))

    lon_label = tk.Label(lat_lon, text="Set longitude: ")
    lon_label.grid(row = 1, column = 0)
    lon_entry = tk.Entry(lat_lon, textvariable=opts_dict['longitude'])
    lon_entry.grid(row = 1, column = 1)
    lon_entry.bind("<FocusOut>", lambda event: opts_dict['longitude'].set(float(lon_entry.get())))
    solar_resource_button = tk.Button(lat_lon, text = 'Open Solar Resource', 
                                      command = lambda: calc_solar_resource(lat = lat_entry.get(),
                                                                     lon = lon_entry.get()))
    solar_resource_button.grid(row = 2, column = 1)
    lat_lon.pack()
    
    # Choose options
    mod_inv = tk.Frame(options_window, border = 50)
    
    module_label = tk.Button(mod_inv, text="Module", command = lambda: open_params(bifacial_modules[module_selector.get()]))
    module_label.grid(row = 0, column = 0)
    module_selector = ttk.Combobox(mod_inv, textvariable=opts_dict['module'], values=bifacial_modules.T.index.to_list())
    module_selector.configure(width = 30)
    module_selector.grid(row = 0, column = 1)
    
    inverter_label = tk.Button(mod_inv, text="Inverter", command = lambda: open_params(cec_inverters[inverter_selector.get()]))
    inverter_label.grid(row = 2, column = 0)
    inverter_selector = ttk.Combobox(mod_inv, textvariable=opts_dict['inverter'], values=cec_inverters.T.index.to_list())
    inverter_selector.configure(width = 30)
    inverter_selector.grid(row = 2, column = 1)
    
    mod_inv.pack()
    
    track_opts = tk.Frame(options_window)
    
    track_label = tk.Label(track_opts, text="Tracking: ")
    track_label.grid(row = 0, column = 0)
    track_selector = tk.OptionMenu(track_opts, opts_dict["tracking"], *track_options)
    track_selector.grid(row = 0, column = 1)
    
    track_opts.pack()
    
    
    #Pannel azimuth and tilt
    az_tilt = tk.Frame(options_window, border = 50)

    azimuth_label = tk.Label(az_tilt, text="Pannel azimuth:")
    azimuth_label.grid(row = 0, column = 0)
    azimuth_entry = tk.Entry(az_tilt, textvariable=opts_dict['pannel_azimuth'])
    azimuth_entry.grid(row = 0, column = 1)
    azimuth_entry.bind("<FocusOut>", lambda event: opts_dict['pannel_azimuth'].set(float(azimuth_entry.get())))
    
    tilt_label = tk.Label(az_tilt, text="Pannel tilt:")
    tilt_label.grid(row = 1, column = 0)
    tilt_entry = tk.Entry(az_tilt, textvariable=opts_dict['pannel_tilt'])
    tilt_entry.grid(row = 1, column = 1)
    tilt_entry.bind("<FocusOut>", lambda event: opts_dict['pannel_tilt'].set(float(tilt_entry.get())))
    
    az_tilt.pack()
    
    # modules per string and strings
    rows_strings = tk.Frame(options_window)
    
    mods_label = tk.Label(rows_strings, text="Modules per string: ")
    mods_label.grid(row = 0, column = 0)
    mods_entry = tk.Entry(rows_strings, textvariable=opts_dict['modules_per_string'])
    mods_entry.grid(row = 0, column = 1)
    mods_entry.bind("<FocusOut>", lambda event: opts_dict['modules_per_string'].set(int(mods_entry.get())))
    
    strings_label = tk.Label(rows_strings, text="Strings: ")
    strings_label.grid(row = 1, column = 0)
    strings_entry = tk.Entry(rows_strings, textvariable=opts_dict['strings'])
    strings_entry.grid(row = 1, column = 1)
    strings_entry.bind("<FocusOut>", lambda event: opts_dict['strings'].set(int(strings_entry.get())))
    
    rows_strings.pack()
    
    # Set GCR
    gcr_label = tk.Label(rows_strings, text="GCR: ")
    gcr_label.grid(row = 2, column = 0)
    gcr_entry = tk.Entry(rows_strings, textvariable=opts_dict['gcr'])
    gcr_entry.grid(row = 2, column = 1)
    gcr_entry.bind("<FocusOut>", lambda event: opts_dict['gcr'].set(float(gcr_entry.get())))
    
    # Albdedo
    albedo_label = tk.Label(rows_strings, text="Albedo: ")
    albedo_label.grid(row = 3, column = 0)
    albedo_entry = tk.Entry(rows_strings, textvariable=opts_dict['albedo'])
    albedo_entry.grid(row = 3, column = 1)
    albedo_entry.bind("<FocusOut>", lambda event: opts_dict['albedo'].set(float(albedo_entry.get())))
    
    # Calculate model
    calc_frame = tk.Frame(options_window, border = 50)
    
    calc_label = tk.Label(calc_frame, text="Calculate model:")
    calc_label.grid(row = 0, column = 0)
    button_calc_model = tk.Button(calc_frame, text = 'Calculate', command = calc_model)
    button_calc_model.grid(row = 0, column = 1)
    
    calc_frame.pack()
    
    # Plot
    # Label to select type of plot
    plottings = tk.Frame(plot_window)
    
    type_plot_label = tk.Label(plottings, text="Plot type:")
    type_plot_label.grid(row = 0, column = 0)
    type_plot = tk.OptionMenu(plottings, opts_dict["type_plot"], *type_options)
    type_plot.grid(row = 0, column = 1)
    
    # call the modified function to get the Figure instance
    plot_button = tk.Button(plottings, text = 'Plot', command = lambda: plot_on_canvas(canvas, opts_dict))
    plot_button.grid(row = 0, column = 2)
    
    plottings.pack()
    
    # Plot Canvas
    canvas = tk.Canvas(plot_window, width=800, height=400, bg = 'white')
    canvas.pack_propagate(0)
    canvas.pack()
    
    # Save results button
    save_button = tk.Button(plot_window, text = 'Save results', command = save_results)
    save_button.pack()
    
    # Place main Frame and run mainloop
    options_window.grid(row = 0, column = 0)
    plot_window.grid(row = 0, column = 1)
    root.mainloop()

####################################################################################################
# Functions

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
    
    # Update parameters
    modules_per_string = opts_dict['modules_per_string'].get()
    strings = opts_dict['strings'].get()
    gcr = opts_dict['gcr'].get()
    my_module = bifacial_modules[opts_dict['module'].get()]
    my_inverter = cec_inverters[opts_dict['inverter'].get()]
    track = opts_dict['tracking'].get()
    pannel_azimuth = opts_dict['pannel_azimuth'].get()
    pannel_tilt = opts_dict['pannel_tilt'].get()
    albedo = opts_dict['albedo'].get()
    
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
    

    
    
    results = pd.DataFrame({})
    total_results = pd.DataFrame({})
    
    if track == 'Backtrack':
        sat_mount = pvsystem.SingleAxisTrackerMount(axis_tilt=axis_tilt,
                                                axis_azimuth=axis_azimuth,
                                                max_angle=max_angle,
                                                backtrack=True,
                                                gcr=gcr)
        
    elif track == 'Track':
        sat_mount = pvsystem.SingleAxisTrackerMount(axis_tilt=axis_tilt,
                                                axis_azimuth=axis_azimuth,
                                                max_angle=max_angle,
                                                backtrack=False,
                                                gcr=gcr)
           
        
    elif track == 'Fixed tilt':
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
                                  index_observed_pvrow=1)

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
    
    global df_results
    df_results = pd.DataFrame({})
    df_results = total_results.T
    df_results = df_results.rename(columns = {0: 'Value'})
    df_results['units'] = ('MWh', 'h', '%', 'pu')
    
    metadata = {}
    for key, value in opts_dict.items():
        metadata[key] = value.get()
        
    metadata_df = pd.DataFrame.from_dict(metadata, orient='index', columns=['Value'])
    df_results = pd.concat([df_results, metadata_df])
    file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    df_results.to_csv(file_path, index = True)
    
# Solar resource graph
def calc_solar_resource(lat, lon):
    
    global data, probability, ghi_daily
    
    solar_resource_window = tk.Tk()
    solar_resource_window.title('Solar Resource')
    data, months_selected, inputs, metadata = iotools.get_pvgis_tmy(opts_dict['latitude'].get(), 
                                                                    opts_dict['longitude'].get(),
                                                                    map_variables=True)
    
    # get the latest year in the index
    latest_year = max(data.index.year)
    
    # create a new index with the latest year
    new_index = data.index.map(lambda x: x.replace(year=latest_year))
    
    # set the new index on the dataframe
    data = data.set_index(new_index)
    ghi_daily = data['ghi']
    
    thresholds = list(range(0, 1200, 50))
    ghi_daily['bins'] = pd.cut(ghi_daily, thresholds)
    probability = ghi_daily['bins'].value_counts().sort_index()

    # Convert the Interval objects into string representations
    bin_labels = [str(bin_) for bin_ in probability.index]
    
    # Create the bar graph
    figure = plt.Figure(figsize=(10, 6))
    ax = figure.add_subplot(111)
    ax.bar(bin_labels, probability)
    ax.set_xlabel('Irradiance Threshold (W/m²)')
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylabel('Number of Hours')
    ax.set_title('Irradiance Distribution')
    plt.tight_layout()
    
    # Create the Tkinter canvas and embed the graph
    canvas = FigureCanvasTkAgg(figure, master=solar_resource_window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    # Start the Tkinter event loop
    solar_resource_window.mainloop()
    
def open_params(my_module):
    
    global module_parameters
    module_parameters = my_module.to_dict()    
    
    module_params_window = tk.Tk()
    module_params_window.title('Parameters')
    
    # Create treeview
    module_params = ttk.Treeview(module_params_window)
    module_params['columns'] = ('Index', 'Value')
    module_params['show'] = 'headings'
    module_params.heading('Index', text='Index')
    module_params.heading('Value', text='Value')
    
    # Insert dictionary items into the Treeview
    for key, value in module_parameters.items():
        module_params.insert('', 'end', values=(key, value))
        
    module_params.pack()
    module_params_window.mainloop()
   
if __name__ == "__main__":
    main()