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
from wave_gen import wave_gen

'''
IMPORTANT NOTE: ALL UNITS ARE IN SI STANDARD UNITS. Thus, speed is in m/s,
frequency is in Hz, positions in m, etc.
'''
# Speed of sound in water
SPEED_OF_SOUND = 1480


def single_channel(input_times, input_waveform, transmitter_pos_init, 
                   receiver_pos_init, transmitter_velocity, 
                   receiver_velocity, wave_speed):
     # Velocity of the transmitter relative to the receiver.
    relative_velocity = transmitter_velocity - receiver_velocity

    # Initial position of the transmitter relative to the receiver.
    relative_pos_init = transmitter_pos_init - receiver_pos_init

    # Relative position of the transmitter every time it makes a ping.
    relative_positions = np.array([
        relative_pos_init + time * relative_velocity for time in input_times
    ])

    # Distance the wave travels for each sample.
    travel_distances = np.linalg.norm(relative_positions, axis=1)

    # The velocity of the ping obtained by the receiver in the 'rest' frame
    # of the medium (water in our case) is given by the speed of the wave
    # in the medium multiplied by the unit vector pointing from the transmitter
    # to the receiver.
    wave_velocities = np.array([
        -wave_speed * relative_position / np.linalg.norm(relative_position)
        for relative_position in relative_positions
    ])

    # The speed of the ping obtained in the receiver's rest frame.
    relative_wave_speeds = \
        np.linalg.norm(wave_velocities - receiver_velocity, axis=1)

    # The time at which each point is received is given by the distance
    # travelled divided by the wave speed relative to the receiver.
    output_times = input_times + travel_distances / relative_wave_speeds

    # Calculate the magnitude of the pings at the received sub.
    output_waveform = input_waveform / travel_distances

    return (output_times, output_waveform)



#Function to calculate recieved waveforms at the hydrophone locations
def channel(input_times, input_waveform, transmitter_pos_init, receiver_center_pos_init,
            receiver_orientation, spacing, transmitter_velo, receiver_velo, 
            noise, wave_speed):
    
    #Calculate the initial positions of the 4 reciever (hydrophone) positions.
    #They are arranged in a d by d square with reciever_center_pos_init at the center,
    #with d being equal to spacing.
    
    #ORIENTATION: For now, assume that we orient the sub as if the front is facing towards 
    #the positive x-direction (right). So, looking at the sub, the front left 
    #would be the upper rightmost corner. 
    
    #Make reciver_orientation into a unit vector
    receiver_orientation_normalized = receiver_orientation/np.linalg.norm(receiver_orientation)
    #Make a vector of length d/2 pointing in the same direction as the 
    #orientation vector
    r_orient_d_over_2 = receiver_orientation_normalized * spacing/2
    #Make another vector of length d/2 that is perpendicular to the orientation
    #vector by rotating it 90 degress counterclockwise.
    r_perp_orient_d_over_2 = np.array([-r_orient_d_over_2[1], r_orient_d_over_2[0]])
    #To find the four hydrophone positions, we will have to add both of the
    #above vectors to the center point and then rotate that 90 degrees to get
    #all 4 points.
    r_hydrophone_pos_vector = r_orient_d_over_2 + r_perp_orient_d_over_2
    
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
    
    for i in range(4):
        receiver_positions[i+1] = receiver_center_pos_init + r_hydrophone_pos_vector
        #Rotate the hydrophone_pos_vector by 90 degrees to get to the next position
        r_hydrophone_pos_vector = np.array([-r_hydrophone_pos_vector[1], \
                                            r_hydrophone_pos_vector[0]])
    
    #Use emulate to get the output waveforms at each receiver position and 
    #then add noise
    output_times = [None] * 5
    output_waveforms = [None] * 5
    
    for i in range(5):
        output_wave = single_channel(input_times, input_waveform, transmitter_pos_init, 
                                     receiver_positions[i], transmitter_velo, 
                                     receiver_velo, wave_speed)
        
        times, waveform = output_wave
        waveform = waveform + np.random.normal(0,noise,size=len(waveform))
        output_times[i] = times
        output_waveforms[i] = waveform
    
    #Return the times,waveform received at each of the 5 points (center and 
    #4 hydrophones). The waves received at the 4 hydrophones are listed 
    #counterclockwise, starting with front left.
    #So, the values returned are:
        #   Output times
        #   Output waveforms 
        #where the outputs are indexed as:
        #   0: center
        #   1: front left
        #   2: back left
        #   3: back right
        #   4: front right
        
    return output_times, output_waveforms

# Code testing region.
if __name__ == '__main__':

    noise_variance = 0.0005
    
    # Set initial sub positions and velocities
    transmitter_position_initial = np.array([0, 0])
    receiver_position_initial = np.array([SPEED_OF_SOUND/5, 0])
    receiver_orientation_initial = np.array([1, 0])
    transmitter_velocity = np.array([-10, 0])
    receiver_velocity = np.array([0, 0])
    receiver_spacing = 0.0254
    
    #Create the input wave
    input_times, input_waveform = wave_gen(
        [(0.00025, 20000, 1, 0), (0.0005, 40000, 1, 0),
         (0.00025, 20000, 1, 0)],
        num_pts=1000
    )
    
    # Emulate input and output waveforms
    output_times, output_waveforms = channel(input_times, input_waveform,
    transmitter_position_initial, receiver_position_initial,
    receiver_orientation_initial, receiver_spacing, transmitter_velocity, 
    receiver_velocity, noise_variance, SPEED_OF_SOUND)
    

    plt.figure()
    plt.plot(input_times, input_waveform, c='r', label="Input waveform")
    plt.legend()
    
    #Plot the outputs (0: center, 1: front left, 2: back left, 3: back right, 
    #4: front right)
    fig = plt.figure()
    for i in range(5):
        
        plt.plot(output_times[i], output_waveforms[i], label = 'Output ' + str(i) + ' Waveform')
        plt.legend()
    
    #Set the x axis limits
    fig.axes[0].set_xlim(0.2, 0.2001)
