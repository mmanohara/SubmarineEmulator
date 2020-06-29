# -*- coding: utf-8 -*-
"""
Created on Tue May 5 21:08:03 2020

@author: chase

Returns a vector representing the direction of origin of the pings 

"""

# This has not actually been done yet
# TODO: Use Reuben's code to generate a waveform and determine the phases
# from that
# the waveform you can expect in from tyler is in the form of two one
# dimensional arrays, one of times and one of voltages
# I can assume that the ping will be more than 1 millisecond long
# I know that for the most part 1 millisecond is an integer number of periods
# But I can also use the known period based on the frequency to round the time
# down to an integer multiple of the period to make my math actually work out

import math
import numpy as np
import matplotlib.pyplot as plt

# Known constants
SPEED_OF_SOUND = 1480 # meters per second
HYDROPHONE_SPACING = 0.1 # meters
# NOTE: Hydrophone spacing must be less than half of a wavelength

# hydrophones are in a square, numbered 1-4 like the quadrants 
# (phones 1 and 2 are on same x axis, 3 and 4 on same y)

def find_origin(c, freq, d, p1, p2, p3, p4):
    '''
    Finds a normalized vector pointing towards the source of the ping
    given phase values measured at each hydrophone

    Parameters
    ----------
    c : TYPE float
        DESCRIPTION.
        Speed of the wave. This will be the speed of sound in water for most
        applications.
        
    freq : TYPE float (preferably integer)
        DESCRIPTION.
        Frequency we are transmitting waves at.
        
    d : TYPE float (preferably integer)
        DESCRIPTION.
        Distance between adjacent hydrophones (side length of square)
        
    p1 : TYPE float (between 0 and 2pi)
        DESCRIPTION.
        Phase of wave at hydrophone 1 (upper left)
    
    p2 : TYPE float (between 0 and 2pi)
        DESCRIPTION.
        Phase of wave at hydrophone 2 (upper right)
        
    p3 : TYPE float (between 0 and 2pi)
        DESCRIPTION.
        Phase of wave at hydrophone 3 (bottom right)
        
    p4 : TYPE float (between 0 and 2pi)
        DESCRIPTION.
        Phase of wave at hydrophone 4 (bottom left)

    Returns
    -------
    Normalized 1D numpy array representing the direction of origin of the wave

    '''
    
    # v_x, v_y, and v_z are the x and y components of the wave direction
    v_x = c * (p2 - p1 - p4 + p3)/(4 * np.pi * d * freq)
    v_y = (p2 + p1 - p4 - p3)/(4 * np.pi * d * freq)
    v_z = math.sqrt(1 - pow(v_x, 2) - pow(v_y, 2))
    
    return np.array([v_x, v_y, v_z])
    
def find_phase():
    return
    
    
if __name__ == "__main__": 
    print("Executed when invoked directly")
    
    