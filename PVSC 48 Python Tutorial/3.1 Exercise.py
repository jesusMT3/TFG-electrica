# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 13:14:59 2023

@author: Jesús
"""

import pvlib
import pathlib
import pandas as pd
import matplotlib.pyplot as plt

#1. Create a path to the tmy3 file
DATA_DIR = pathlib.Path(pvlib.__file__).parent / 'data'
my_path = DATA_DIR / "703165TY.csv"

#2. Read the timeseries and metadata from file
df_tmy, metadata = pvlib.iotools.read_tmy3(my_path, coerce_year= 2005)

#3. Assuming a glass polymer module on a horizontally flat rooftop,
# use the SAPM to calculate the cell temperature
all_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']
parameters = all_parameters['open_rack_glass_polymer']
cell_temperature = pvlib.temperature.sapm_cell(poa_global = df_tmy['GHI'], 
                                               temp_air = df_tmy['DryBulb'], 
                                               wind_speed = df_tmy['Wspd'], 
                                               a = parameters['a'], 
                                               b = parameters['b'], 
                                               deltaT = parameters['deltaT'])

#4. Compare the first week of ambient temperature with cell temperature
df_temperature = pd.DataFrame({
    'ambient': df_tmy['DryBulb'].head(24*7),
    'cell': cell_temperature.head(24*7)})

df_temperature[['ambient', 'cell']].plot()
plt.title('Comparison between ambient temperature and cell temperature')
plt.ylabel('[degrees]')
plt.grid()