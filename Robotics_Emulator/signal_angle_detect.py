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

def find_origin(c, freq, d, p):
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
        
    p : TYPE 1D array of floats (each between 0 and 2pi)
        DESCRIPTION.
        Phases of wave at each of the hydrophones
        0 is upper left
        1 is upper right
        2 is bottom right
        3 is bottom left

    Returns
    -------
    Normalized 1D numpy array representing the direction of origin of the wave

    '''
    
    # find phase differences
    # diffs[0] and [1] are x phase diffs on top and bottom, respectively
    # diffs[2] and [3] are y phase diffs on the left and right, respectively
    diffs = np.array([p[1]-p[0], p[2]-p[3], p[0]-p[3], p[1]-p[2]])
    
    #trim phase differences to force between +/- pi
    diffs = diffs % (2 * np.pi) 
    
    for x in range(4):
        if diffs[x] > np.pi:
            diffs[x] = diffs[x] - (2 * np.pi)
            
    # v_x, v_y, and v_z are the x, y, and z components of the wave direction
    v_x = c * (diffs[0] + diffs[1])/(4 * np.pi * d * freq)
    v_y = c * (diffs[2] + diffs[3])/(4 * np.pi * d * freq)
    v_z = 1 - pow(v_x, 2) - pow(v_y, 2)
    if v_z < 0:
        v_z = 0
    else:
        v_z = np.sqrt(v_z)
        
    
    return np.array([v_x, v_y, v_z])
    
def find_phase(freq, times, waves):
    '''
    Finds the phase of a given signal given its frequency and 1D arrays of 
    times and amplitudes at those times

    Parameters
    ----------
    freq : TYPE float (preferably integer)
        DESCRIPTION.
        Frequency we are transmitting waves at.
    
    times : TYPE 1D numpy array
        DESCRIPTION.
        List of times corresponding to each point in the waveform. Assumed to
        be ordered and in seconds.
        
    waves : TYPE 1D numpy array
        DESCRIPTION.
        List of amplitudes comprising the final waveform

    Returns
    -------
    The phase difference of this particular wave

    '''
    
    omega = 2 * np.pi * freq
    
    # Trim this signal to the first ms, which is all we need
    times = times[times < times[0] + 0.001]
    if (times.size < 1):
        # If no measurements taken in the first millisecond, something wrong
        return 0; # what should I do?
    
    # Trim the wave using the times as a guide
    waves = np.resize(waves, times.size)
    
    # sums to find kI and kQ for Fourier inner product
    kI = np.sum(waves * np.cos(omega * times))
    kQ = np.sum(waves * np.sin(omega * times))
    
    # Am I correct in using arctan2 here?
    phase = np.arctan2(kQ, kI)

    return phase

def signal_angle_detect(c, freq, d, times, waves):
    '''
    Combines find_phase and find_origin to 

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
        
    times : list of four 1D numpy arrays
        DESCRIPTION.
        List of four 1D numpy arrays representing the times of each 
        measurement by each of the four hydrophones.
    
    waves : list of four 1D numpy arrays
        DESCRIPTION.
        List of four 1D numpy arrays representing the amplitudes of each 
        measurement (corresponding to the times in times) by each of the four
        hydrophones.

    Returns
    -------
    A 1D array of the x, y, and z components of the detected direction of the
    signal

    '''
    phases = np.zeros(4)
    for i in range(0, 4):
        phases[i] = find_phase(freq, times[i], waves[i])
        
    doa = find_origin(c, freq, d, phases)
    
    return doa
    
#if __name__ == "__main__": 
    # Executed when invoked directly