# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 11:09:42 2023

@author: Jesus
"""
# Import libraries

import warnings
from pvlib import pvsystem, iotools, location, modelchain, ivtools
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS as PARAMS
import tkinter as tk
from tkinter import filedialog
from pvlib.bifacial.pvfactors import pvfactors_timeseries
import pandas as pd
import matplotlib.pyplot as plt


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

def main():
    
    
def calc_module():
    
    
    
if __name__ == "__main__":
    main()