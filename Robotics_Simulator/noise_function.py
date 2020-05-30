# -*- coding: utf-8 -*-
"""
Created on Sat May  9 14:28:42 2020

@author: Tyler Colenbrander

This is a function to add noise to the waveforms.
"""

import numpy as np
import matplotlib.pyplot as plt
import waveform_generator_frequency_modulated as fm


#Function to add noise to an input waveform
def noise(input_waveform):

    output_waveform = input_waveform
    
    #Goes through each waveform value in the input_waveform and adds noise
    x = 0
    for waveform in output_waveform:
        output_waveform[x] = output_waveform[x] + np.random.normal(0,noise_variance)
        x += 1
    
    return output_waveform

# Code testing region.
if __name__ == '__main__':

    #Generate a waveform
    num_pts = 1000
    times, input_waveform = fm.wave_gen_FM([(10000, 1)], num_pts)
    noise_variance = 0.5
    
    output_waveform = noise(input_waveform)
    plt.figure()
    plt.plot(times, output_waveform)
    #plt.plot(times, input_waveform)
    plt.legend
    plt.show()