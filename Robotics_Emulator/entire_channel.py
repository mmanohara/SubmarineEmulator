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
from phase_shift_checker import fourier_phase_shift_checker, phase_to_bit
from testFrequencyDemodulation import decodeFrequencyModulation

'''
IMPORTANT NOTE: ALL UNITS ARE IN SI STANDARD UNITS. Thus, speed is in m/s,
frequency is in Hz, positions in m, etc.
'''
# Speed of sound in water
SPEED_OF_SOUND = 1480

def manual_demodulate(bitstream, quad=False):
    if not quad:
        correct_bitstream = []
        for i in range(1, len(bitstream)):
            correct_bitstream.append(0 if bitstream[i] == bitstream[i - 1] else 1)
        return np.array(correct_bitstream)
    else:
        correct_bitstream = []
        for i in range(1, len(bitstream)):
            correct_bitstream.append((bitstream[i] - bitstream[i - 1]) % 4)
        return np.array(correct_bitstream)
            

# Code testing region.

def psk_test():
    # Set initial sub positions and velocities
    transmitter_position_initial = np.array([0, 0])
    receiver_position_initial = np.array([SPEED_OF_SOUND/10, 0])
    receiver_orientation_initial = np.array([0, -1])
    transmitter_velocity = np.array([1.5, 0])
    receiver_velocity = np.array([-1.5, 0])
    receiver_spacing = 0.02
    
    #Noise for transmission channel
    noise_variance = 0.03#10000
    
    #Generate the bitstream
    bitstream = np.random.randint(0,2,size=100)
    correct_bitstream = manual_demodulate(bitstream)
    str_bitstream = [str(i) for i in bitstream]
    print("Initial Bitsream:")
    print(bitstream)
    
    #Make a waveform from the bitstream
    bit_rate = 1000
    frequency = 30000
    times, waveform = transmit(str_bitstream,bit_rate,encoding=None, 
                               encoding_arg=0,modulation_type='PSK', 
                               PSK_phase=180,frequency=frequency)
    
    #Send the waveform through the noise channel
    output_times, output_waveforms = channel(times, waveform,
    transmitter_position_initial, receiver_position_initial,
    receiver_orientation_initial, receiver_spacing, transmitter_velocity, 
    receiver_velocity, noise_variance, SPEED_OF_SOUND)
    
    #Demodulate each output waveform (0: center, 1: front left, 2: back left, 
    #3: back right, 4: front right)
    recieved_bits_phase_shift = [None] * 5
    
    time_int = 1/bit_rate
    
    """
    #Testing Phase Shift Checker
    test_times, test_waveform = times, waveform
    #print(test_times, test_waveform)
    phase_shift_bits = phase_shift_checker(test_times, test_waveform, time_int,
                                           10000)
    print(phase_shift_bits)
    """
    
    error_list = [None] * 5
    for i in range(5):
        recieved_bits_phase_shift[i] = phase_to_bit(fourier_phase_shift_checker(output_times[i], output_waveforms[i], 
                                               time_int, frequency))
        if len(recieved_bits_phase_shift[i]) < len(correct_bitstream):
            print(f"Lost {len(correct_bitstream)-len(recieved_bits_phase_shift[i])} bits")
            error_list[i] = sum(np.logical_xor(recieved_bits_phase_shift[i], correct_bitstream[0:len(recieved_bits_phase_shift[i])]))
        elif len(recieved_bits_phase_shift[i]) > len(correct_bitstream):
            print(f"Extra {len(recieved_bits_phase_shift[i]) - len(correct_bitstream)} bits")
            error_list[i] = sum(np.logical_xor(recieved_bits_phase_shift[i][0:len(correct_bitstream)], correct_bitstream))
        else: 
            error_list[i] = sum(np.logical_xor(recieved_bits_phase_shift[i][0:len(correct_bitstream)], correct_bitstream))
            
    #print("Phase Shifts of Output Waveforms:")
    #print(recieved_bits_phase_shift)
    print("Errors of output waveforms")
    print(error_list)
    
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
    
def f2phase(f_list, f1, f2):
    a = np.zeros(len(f_list))
    for i in range(len(f_list)):
        a[i] = 0 if np.abs(f_list[i] - f1) < np.abs(f_list[i] - f2) else 1
    return a
    
def fsk_test():
    # Set initial sub positions and velocities
    transmitter_position_initial = np.array([0, 0])
    receiver_position_initial = np.array([SPEED_OF_SOUND/10, 0])
    receiver_orientation_initial = np.array([0, -1])
    transmitter_velocity = np.array([1.5, 0])
    receiver_velocity = np.array([-1.5, 0])
    receiver_spacing = 0.02
    
    #Noise for transmission channel
    noise_variance = 0.03
    
    #Generate the bitstream
    bitstream = correct_bitstream = np.random.randint(0,2,size=100)
    str_bitstream = [str(i) for i in bitstream]
    #correct_bitstream = manual_demodulate(bitstream)
    print("Initial Bitsream:")
    print(bitstream)
    
    #Make a waveform from the bitstream
    bit_rate = 1000
    f1 = 42000
    f2 = 44000
    times, waveform = transmit(str_bitstream,bit_rate,encoding=None, 
                               encoding_arg=0,modulation_type='FSK', 
                               FSK_freqs=(f1, f2))
    
    #Send the waveform through the noise channel
    output_times, output_waveforms = channel(times, waveform,
    transmitter_position_initial, receiver_position_initial,
    receiver_orientation_initial, receiver_spacing, transmitter_velocity, 
    receiver_velocity, noise_variance, SPEED_OF_SOUND)
    
    #Demodulate each output waveform (0: center, 1: front left, 2: back left, 
    #3: back right, 4: front right)
    recieved_bits_phase_shift = [None] * 5
    
    time_int = 1/bit_rate
    
    """
    #Testing Phase Shift Checker
    test_times, test_waveform = times, waveform
    #print(test_times, test_waveform)
    phase_shift_bits = phase_shift_checker(test_times, test_waveform, time_int,
                                           10000)
    print(phase_shift_bits)
    """
    
    error_list = [None] * 5
    for i in range(5):
        flist = decodeFrequencyModulation(output_times[i], output_waveforms[i], np.array([f1, f2]), time_int)
        #print(f"flist: {flist}")
        recieved_bits_phase_shift[i] = f2phase(flist, f1, f2)
        #print(f"Rec_bits: {recieved_bits_phase_shift[i]}")
        if len(recieved_bits_phase_shift[i]) < len(correct_bitstream):
            print(f"Lost {len(correct_bitstream)-len(recieved_bits_phase_shift[i])} bits")
            error_list[i] = sum(np.logical_xor(recieved_bits_phase_shift[i], correct_bitstream[0:len(recieved_bits_phase_shift[i])]))
        elif len(recieved_bits_phase_shift[i]) > len(correct_bitstream):
            print(f"Extra {len(recieved_bits_phase_shift[i]) - len(correct_bitstream)} bits")
            error_list[i] = sum(np.logical_xor(recieved_bits_phase_shift[i][0:len(correct_bitstream)], correct_bitstream))
        else: 
            error_list[i] = sum(np.logical_xor(recieved_bits_phase_shift[i][0:len(correct_bitstream)], correct_bitstream))
    #print("Phase Shifts of Output Waveforms:")
    #print(recieved_bits_phase_shift)
    print("Errors of output waveforms")
    print(error_list)
    
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
        
def qpsk_test():
    # Set initial sub positions and velocities
    transmitter_position_initial = np.array([0, 0])
    receiver_position_initial = np.array([SPEED_OF_SOUND/10, 0])
    receiver_orientation_initial = np.array([0, -1])
    transmitter_velocity = np.array([1.5, 0])
    receiver_velocity = np.array([-1.5, 0])
    receiver_spacing = 0.02
    
    #Noise for transmission channel
    noise_variance = 0.03
    
    #Generate the bitstream
    bitstream = np.random.randint(0,4,size=100)
    print(f"Bitstream: {bitstream}")
    correct_bitstream = bitstream[1:]
    correct_str_bitstream = [str(i) for i in bitstream]
    print(f"Corrected: {correct_bitstream}")
    #print("Initial Bitsream:")
    #print(bitstream)
    
    #Make a waveform from the bitstream
    bit_rate = 1000
    frequency = 30000
    times, waveform = transmit(correct_str_bitstream,bit_rate,encoding=None, 
                               encoding_arg=0,modulation_type='QPSK', 
                               QPSK_phases=(0, 90, 180, 270), frequency=frequency)
    
    #Send the waveform through the noise channel
    output_times, output_waveforms = channel(times, waveform,
    transmitter_position_initial, receiver_position_initial,
    receiver_orientation_initial, receiver_spacing, transmitter_velocity, 
    receiver_velocity, noise_variance, SPEED_OF_SOUND)
    
    #Demodulate each output waveform (0: center, 1: front left, 2: back left, 
    #3: back right, 4: front right)
    recieved_bits_phase_shift = [None] * 5
    
    time_int = 1/bit_rate
    
    """
    #Testing Phase Shift Checker
    test_times, test_waveform = times, waveform
    #print(test_times, test_waveform)
    phase_shift_bits = phase_shift_checker(test_times, test_waveform, time_int,
                                           10000)
    print(phase_shift_bits)
    """
    
    error_list = [None] * 5
    for i in range(5):
        phases = fourier_phase_shift_checker(output_times[i], output_waveforms[i], 
                                               time_int, frequency)
        #if i == 0:
            #print(f"Phases: {phases.astype(int)}")
        recieved_bits_phase_shift[i] = phase_to_bit(phases, quad=True)
        if len(recieved_bits_phase_shift[i]) < len(correct_bitstream):
            print(f"Lost {len(correct_bitstream)-len(recieved_bits_phase_shift[i])} bits")
            error_list[i] = sum(np.logical_xor(recieved_bits_phase_shift[i], correct_bitstream[0:len(recieved_bits_phase_shift[i])]))
        elif len(recieved_bits_phase_shift[i]) > len(correct_bitstream):
            print(f"Extra {len(recieved_bits_phase_shift[i]) - len(correct_bitstream)} bits")
            error_list[i] = sum(np.logical_xor(recieved_bits_phase_shift[i][0:len(correct_bitstream)], correct_bitstream))
        else: 
            error_list[i] = sum(np.logical_xor(recieved_bits_phase_shift[i][0:len(correct_bitstream)], correct_bitstream))
    #print("Phase Shifts of Output Waveforms:")
    #print(recieved_bits_phase_shift)
    print("Errors of output waveforms")
    print(error_list)
    
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
if __name__ == '__main__':
   qpsk_test()