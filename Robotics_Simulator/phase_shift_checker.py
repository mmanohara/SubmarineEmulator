# -*- coding: utf-8 -*-
"""
Created on Tue May 12 18:57:06 2020

@author: iris0
"""

import numpy as np
import waveform_generator_phase_modulated as wgpm


def phase_shift_checker(times, waveform, time_int, freq):
    '''
    Checks if a phase shift has occured in the waveform.
    
    Parameters
    --------- 
    times: list of times
    
    waveform: The waveform to be checked, as a 1D numpy array
    
    time_int: the time interval over which a phase shift could occur
    
    frequency: the frequency of the waveform
    
    Returns
    -------
    True if a phase shift occured
    
    False if a phase shift has not occured
    
    '''

    prev_time = 0
    prev_wave_point = 0
    target_time = time_int
    bits = ''
    
    for time, wave_point in zip(times, waveform):
        if time > target_time:
            # solve for the phase at the previous time interval
            phase = (np.arcsin(prev_wave_point) + 
                     2 * np.pi * freq * prev_time)
          
            # find the phase at current time point
            new_phase = (np.arcsin(wave_point) 
                         + 2 * np.pi * freq * time)
            
            phase_difference =  abs(new_phase - phase)
            
            if  (phase_difference < np.pi + .01 
                 and phase_difference > np.pi - .01):
                bits += '1'
            elif (phase_difference < 2 * np.pi + .01 
                 and phase_difference > 2 * np.pi - .01):
                bits  += '0'
            else:
                print(phase - new_phase)
            
            prev_wave_point = wave_point
            prev_time = target_time
            target_time += time_int
        
    return bits
        


# testing
if __name__ == '__main__':

    # List of times corresponding to each phase flip.
    wave_list = [1.5, 6, 6, 1.5]
    # should give 1000100010
    times, waveform = wgpm.wave_gen_phase_modulated(wave_list, freq=0.5)

    
    times = times.tolist()
    waveform = waveform.tolist()
    
    
    print(phase_shift_checker(times, waveform, 1.5, 0.5))
    
