# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 14:08:22 2020

This should take all the different operations done on the signal and combine 
them into one file.

@author: tyler
"""

import numpy as np
import matplotlib.pyplot as plt
from wave_channel import channel
from transmit import transmit
from phase_shift_checker import phase_shift_checker

'''
IMPORTANT NOTE: ALL UNITS ARE IN SI STANDARD UNITS. Thus, speed is in m/s,
frequency is in Hz, positions in m, etc.
'''
# Speed of sound in water
SPEED_OF_SOUND = 1480

# Code testing region.
if __name__ == '__main__':
    
    # Set initial sub positions and velocities
    transmitter_position_initial = np.array([0, 0])
    receiver_position_initial = np.array([SPEED_OF_SOUND/5, 0])
    receiver_orientation_initial = np.array([1, 0])
    transmitter_velocity = np.array([-10, 0])
    receiver_velocity = np.array([0, 0])
    receiver_spacing = 0.0254
    
    #Noise for transmission channel
    noise_variance = 0.0005
    
    #Generate the bitstream
    bitstream = np.random.randint(0,2,size=5)
    
    #Make a waveform from the bitstream
    times, waveform = transmit(bitstream,bit_rate=10000,encoding=None, 
                               encoding_arg=0,modulation_type='FM', 
                               modulation_frequencies=(20000, 50000)
                               )
    
    #Send the waveform through the noise channel
    output_times, output_waveforms = channel(times, waveform,
    transmitter_position_initial, receiver_position_initial,
    receiver_orientation_initial, receiver_spacing, transmitter_velocity, 
    receiver_velocity, noise_variance, SPEED_OF_SOUND)
    
    #Demodulate each output waveform (0: center, 1: front left, 2: back left, 
    #3: back right, 4: front right)
    recieved_bits = [None] * 5
    
    #Work in Progress
    
    #Plot the input waveform
    plt.figure()
    plt.plot(times, waveform, c='r', label="Input waveform")
    plt.legend()
    
    #Plot the outputs (0: center, 1: front left, 2: back left, 3: back right, 
    #4: front right)
    fig = plt.figure()
    for i in range(5):
        
        plt.plot(output_times[i], output_waveforms[i], label = 'Output ' + str(i) + ' Waveform')
        plt.legend()
    
    #Set the x axis (Time) limits if desired
    #fig.axes[0].set_xlim(0.2, 0.2001)
