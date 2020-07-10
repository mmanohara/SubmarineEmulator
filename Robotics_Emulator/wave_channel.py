# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 16:10:09 2020

@author: tyler

This function takes an input waveform and gives the output waveform at the four
hydrophone positions and the center point.

Note: there is currently no functionality for setting the orientation of the
sub, will add that later.
"""

import numpy as np
import matplotlib.pyplot as plt
from main_test import emulate

'''
IMPORTANT NOTE: ALL UNITS ARE IN SI STANDARD UNITS. Thus, speed is in m/s,
frequency is in Hz, positions in m, etc.
'''
# Speed of sound in water
SPEED_OF_SOUND = 1480

#Function to calculate recieved waveforms at the hydrophone locations
def channel(wave_speed, freq, transmitter_pos_init, receiver_center_pos_init,
            spacing, transmitter_velo, receiver_velo, noise,
            duration=0.001, n_points=1000):
    
    #Calculate the initial positions of the 4 reciever (hydrophone) positions.
    #They are arranged in a d by d square with reciever_center_pos_init at the center,
    #with d being equal to spacing.
    
    #ORIENTATION: For now, assume that we orient the sub as if the front is facing towards 
    #the positive x-direction (right). So, looking at the sub, the front left 
    #would be the upper rightmost corner. 
    
    ######## Will need to code in orientation as a parameter later! ##########
    
    #This array will hold the values of the 5 receiver positions with these
    #indexes:
    #   0: center
    #   1: front left
    #   2: back left
    #   3: back right
    #   4: front right
    receiver_positions = [None] * 5
    
    #Setting all the receiver position values
    receiver_positions[0] = receiver_center_pos_init
    receiver_positions[1] = np.array([receiver_center_pos_init[0] \
                                             + spacing/2, \
                                            receiver_center_pos_init[1] \
                                            + spacing/2])
    receiver_positions[2] = np.array([receiver_center_pos_init[0] \
                                             - spacing/2, \
                                            receiver_center_pos_init[1] \
                                            + spacing/2])
    receiver_positions[3] = np.array([receiver_center_pos_init[0] \
                                             - spacing/2, \
                                            receiver_center_pos_init[1] \
                                            - spacing/2])
    receiver_positions[4] = np.array([receiver_center_pos_init[0] \
                                             + spacing/2, \
                                            receiver_center_pos_init[1] \
                                            - spacing/2])
    
    #Use emulate to get the output waveforms at each receiver position and 
    #then add noise
    output_times = [None] * 5
    output_waveforms = [None] * 5
    
    for i in range(5):
        in_, output_wave = emulate(wave_speed, freq, transmitter_pos_init,
                                       receiver_positions[i], transmitter_velo,
                                       receiver_velo)
        times, waveform = output_wave
        waveform = waveform + np.random.normal(0,noise,size=len(waveform))
        output_times[i] = times
        output_waveforms[i] = waveform
    
    #Return the input times,waveform and then the times,waveform received at 
    #each of the 5 points (center and 4 hydrophones). The waves received at the
    #4 hydrophones are listed counterclockwise, starting with front left.
    #So, the values returned are:
        #   Input times, waveform
        #   Output times
        #   Output waveforms 
        #where the outputs are indexed as:
        #   0: center
        #   1: front left
        #   2: back left
        #   3: back right
        #   4: front right
        
    return in_, output_times, output_waveforms   

# Code testing region.
if __name__ == '__main__':

    frequency = 30000
    noise_variance = 0.0005
    
    # Set initial sub positions and velocities
    transmitter_position_initial = np.array([0, 0])
    receiver_position_initial = np.array([SPEED_OF_SOUND/5, 0])
    transmitter_velocity = np.array([-10, 0])
    receiver_velocity = np.array([0, 0])
    receiver_spacing = 0.5
    
    # Emulate input and output waveforms
    in_, output_times, output_waveforms = channel(
    SPEED_OF_SOUND, frequency, transmitter_position_initial, receiver_position_initial,
    receiver_spacing, transmitter_velocity, receiver_velocity, noise_variance)
     
    plt.figure()
    plt.plot(in_[0], in_[1], c='r', label="Input waveform")
    plt.legend()
    
    #Plot the outputs (0: center, 1: front left, 2: back left, 3: back right, 
    #4: front right)
    for i in range(5):
        plt.figure()
        plt.plot(output_times[i], output_waveforms[i], c = 'b', label = 'Output ' + str(i) + ' Waveform')
        plt.legend()