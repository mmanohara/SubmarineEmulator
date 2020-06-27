# -*- coding: utf-8 -*-
"""
Created on Sat May  9 14:28:42 2020

@author: Tyler Colenbrander

This is a function to add noise to the waveforms.
"""

import numpy as np
import matplotlib.pyplot as plt
from main_test_1 import simulate

'''
IMPORTANT NOTE: ALL UNITS ARE IN SI STANDARD UNITS. Thus, speed is in m/s,
frequency is in Hz, positions in m, etc.
'''
# Speed of sound in water
speed_of_sound = 1480

#Function to add noise to an input waveform
def noise(times,input_wave,noise):

    output_waveform = input_wave + np.random.normal(0,noise,size=len(input_wave))
    
    return (times,output_waveform)

# Code testing region.
if __name__ == '__main__':

    c = speed_of_sound
    freq = 30000
    noise_variance = 0.0005
    # Set initial sub positions and velocities
    sub_position_1 = np.array([0, 0])
    sub_position_2 = np.array([c/5, 0])
    sub_velocity_1 = np.array([-10, 0])
    sub_velocity_2 = np.array([0, 0])
    # Simulate input and output waveforms
    in_, out = simulate(c, freq, sub_position_1, sub_position_2, sub_velocity_1, sub_velocity_2)
    
    #Add noise to output waveform
    out = noise(out[0],out[1],noise_variance)    
    
    plt.figure()
    plt.plot(out[0],out[1], c='r', label="Output waveform")
    plt.legend()
    
    plt.figure()
    plt.plot(in_[0],in_[1], c='b', label="Input waveform")
    plt.legend()
    