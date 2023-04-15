# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 10:21:14 2023

@author: Jesús
"""

# Libraries

from pvlib import pvsystem, iotools, location
import tkinter as tk
from tkinter import filedialog

# Global variables
latitude, longitude = 40.453, -3.727
backtrack = True

def main():
    
    # Global variables and objects
    global site_location, data, metadata
    
    # Load meteorological data
    meteo_file = tk.filedialog.askopenfilename()
    data, metadata = iotools.read_epw(meteo_file)
    
    
    


if __name__ == "__main__":
    main()