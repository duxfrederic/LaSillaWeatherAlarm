#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 00:30:45 2022

@author: fred
"""

URL = 'https://www.ls.eso.org/lasilla/dimm/meteo_light.html'

property_lines = {
        'Humidity': 22,
        'Temperature': 30,
        'Dew Point': 38,
        'Wind Speed': 45,
        'Pressure': 53,
        'Clouds': 62,
        'Sun Altitude': 71,
        'Domes Status': 115
}


# in seconds:
update_frequency = 600
