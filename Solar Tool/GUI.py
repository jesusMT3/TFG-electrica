# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 10:04:51 2023

@author: Jesus
"""

# Import libraries
import webbrowser, warnings, pvfactors
import tkinter as tk
import pandas as pd
from tkinter import filedialog, ttk
from pvlib import iotools, location, pvsystem
from pandastable import Table, TableModel


# supressing shapely warnings that occur on import of pvfactors
warnings.filterwarnings(action='ignore', module='pvfactors')

# Options for the calculations
type_options = ['monthly', 'daily']
unit_options = ['Wh', 'kWh', 'MWh']
tracking_options = ['track', 'backtrack', 'none']

# Database for modules and inverters
cec_modules = pvsystem.retrieve_sam('CECMod').T
cec_inverters = pvsystem.retrieve_sam('cecinverter').T
bifacial_modules = cec_modules[cec_modules['Bifacial'] == 1]
my_module = pd.DataFrame(bifacial_modules.loc['LONGi_Green_Energy_Technology_Co___Ltd__LR6_72BP_350M'])

def main():
    
    global data_dict, my_module, my_inverter, data
    
    # Create main window
    root = tk.Tk()
    root.title('main')
    
    data_dict = {"type_plot": tk.StringVar(value = 'monthly'),
                 "units": tk.StringVar(value = 'kWh'),
                 "tracking": tk.StringVar(value = 'backtrack'),
                 "module": tk.StringVar(value = 'LONGi_Green_Energy_Technology_Co___Ltd__LR6_72BP_350M'),
                 "inverter": tk.StringVar(value = 'ABB__PVI_10_0_I_OUTD_x_US_480_y_z__480V_')}

    # my_module = pd.DataFrame(cec_modules.loc[data_dict['module'].get()])
    # my_inverter = pd.DataFrame(cec_inverters.loc[data_dict['inverter'].get()])
    
    # Set size to the pc's window size
    root.geometry("1080x720")
    root_width = root.winfo_screenwidth()
    root_height = root.winfo_screenheight()
    
    # Print options
    opts_button = tk.Button(root, text="Print options", command=print_data)
    opts_button.pack()
    
    # URL button
    url_button = tk.Button(root, text="PVGIS data web site", command=open_url)
    url_button.pack()

    # Load data button
    data_button = tk.Button(root, text = 'Load meteorological data', command = load_data)
    data_button.pack()  
    
    # Plot options option
    type_plot_label = tk.Label(root, text="Plot type:")
    type_plot_label.pack()
    type_plot = tk.OptionMenu(root, data_dict["type_plot"], *type_options)
    type_plot.pack()
    
    # Units option
    units_label = tk.Label(root, text="Units:")
    units_label.pack()
    units = tk.OptionMenu(root, data_dict["units"], *unit_options)
    units.pack()
    
    # Tracking option
    track_label = tk.Label(root, text="Tracking option:")
    track_label.pack()
    track_button = tk.OptionMenu(root, data_dict["tracking"], *tracking_options)
    track_button.pack()
    
    # Module selector
    module_selector = ttk.Combobox(root, values = bifacial_modules.index.tolist(), textvariable=data_dict["module"])
    module_selector.pack() 
    
    # Module parameters configuration
    name_module = tk.Button(root, textvariable=data_dict['module'], command = open_module_parameters)
    name_module.pack()
    
    # List of module atributes

    # Main loop
    root.mainloop()
    
# Load meteorological .epw file data
def load_data():
    global data, metadata, site_location, solar_position
    print('Loading data...')
    meteo_file = tk.filedialog.askopenfilename()
    data, metadata = iotools.read_epw(meteo_file, coerce_year = 2020)
    site_location = location.Location(latitude = metadata['latitude'],
                                      longitude = metadata['longitude'])

    solar_position = site_location.get_solarposition(data.index)   
    print('Data loaded')
 
# URL to get the meteorological data
def open_url():
    url = "https://re.jrc.ec.europa.eu/pvg_tools/en/#TMY"
    webbrowser.open_new(url)

# Plot energy in a year
def plot_year():
    units = data_dict['units'].get()
    
# Plot energy in a month
def plot_monthly():
    units = data_dict['units'].get()
    
 # Plot energy in a day   
def plot_daily():
    units = data_dict['units'].get()
    
def load_parameters():
    print(my_module)
    
def print_data():
    print(my_module)
    
def open_module_parameters():
    my_module = pd.DataFrame(cec_modules.loc[data_dict['module'].get()])
    my_module.insert(0, "Index", my_module.index)
    module_window = tk.Toplevel()
    module_window.title("Módulo de parámetros")

    # crea el modelo de datos de la tabla
    model = TableModel()
    model.df = my_module

    # crea el marco para la tabla
    table_frame = tk.Frame(module_window)
    table_frame.pack(fill="both", expand=True)

    # crea la tabla utilizando el modelo de datos
    table = Table(table_frame, model=model, showtoolbar=True, showstatusbar=True)
    table.show()

    # inicia el bucle principal de Tkinter
    module_window.mainloop()

if __name__ == "__main__":
    main()