# -*- coding: utf-8 -*-
"""
Created on Tue May 12 18:57:06 2020

@author: iris0
"""

import numpy as np
import wave_gen as wg

import matplotlib.pyplot as plt


def phase_shift_checker(times, waveform, time_int, freq, error = .1):
    '''
    Checks if a phase shift has occured in the waveform.
    
    Parameters
    --------- 
    times: list of times
    
    waveform: The waveform to be checked, as a 1D numpy array
    
    time_int: the time interval over which a phase shift could occur
    
    frequency: the frequency of the waveform
    
    error: (crudely) accounts for noise
    
    Returns
    -------
    True if a phase shift occured
    
    False if a phase shift has not occured
    
    '''
    # Finding the phase based on the peaks
    bits = []
    
    waveform = np.array(waveform)
    times = np.array(times)
    
    period = 1/freq
    # periods in a time interval
    periods_per_interval = time_int // period

    # Set the first positive peak
    i = np.argmax(times > time_int/2)
    i_period = np.argmax(times > time_int/2 + period)
    wave_after = waveform[i: i_period]
    time_after = times[i: i_period]
    reference_peak = np.argmax(wave_after > 1 - error)
    reference_peak_time = time_after[reference_peak]
    
    while reference_peak_time + time_int + period < times[-1]:

        pos_peak_after = reference_peak_time + (periods_per_interval) * period
        # neg_peak_after = pos_peak_after + period/2 # for testing
        
        i_before = np.argmax(times > reference_peak_time + time_int)
        i_after = np.argmax(times > reference_peak_time + time_int + period)

        wave_after = waveform[i_before: i_after]
        times_after = times[i_before: i_after]
        
        actual_pos_peak_after = times_after[
            np.argmax(wave_after > 1 - error)]
        # actual_neg_peak_after = times_after[
        #    np.argmax(wave_after < -1 + error)] #for testing
        
        difference = abs(actual_pos_peak_after - pos_peak_after) % period
        
        # The margin is the margin of error for the value and is an order of 
        # magnitude smaller than the period
        margin = period/10
        
        if difference < margin:
            bits.append(0)
        elif difference < period/2 + margin and difference > period/2 - margin:
            bits.append(1)
        elif difference < period/4 + margin and difference > period/4 - margin:
            bits.append(3/2)
        elif (difference < period*(3/4) + margin and 
            difference > period*(3/4) - margin):
            bits.append(1/2)   
        else:
            bits.append(difference)
        reference_peak_time = actual_pos_peak_after
        
    
    return bits
        


# testing
if __name__ == '__main__':

    # List of times corresponding to each phase flip.
    wave =  [(0.001, 20000, 1, 0), (0.002, 20000, 1, 90), (0.002, 20000, 1, 90)]
    
    times, waveform = wg.wave_gen(wave)
    
    plt.figure()
    plt.plot(times, waveform, label='Combined Waveform')
    plt.legend
    plt.show()
    
    print(phase_shift_checker(times, waveform, .001, 20000))
    
