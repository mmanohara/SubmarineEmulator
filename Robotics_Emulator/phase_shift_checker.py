# -*- coding: utf-8 -*-
"""
Created on Tue May 12 18:57:06 2020

@author: iris0
@contributor: chase
"""

import numpy as np
import wave_gen as wg



def phase_shift_checker(times, waveform, time_int, freq, error = .1, amp = 1):
    '''
    Checks if a phase shift has occured in the waveform.
    
    Phase shifts ideally occur at integer multiples of the time interval. 
    This code may not work if phase shift occurs in the middle of the time int.
    Be warned.
    
    Parameters
    --------- 
    times: 1D nympy array of times
    
    waveform: The waveform to be checked, as a 1D numpy array
    
    time_int: the time interval over which a phase shift could occur
    
    frequency: the frequency of the waveform
    
    error: (crudely) accounts for noise. the error is the distance from the 
        amplitude that can be considered a peak. Default is .1
    
    amp: an integer amplitude, as long as amplitude is constant. Default is 1
    
    Returns
    -------
    a list of values where each element corresponds to a phase shift evaluated
    at the time int
    
    the value is:
    0 if a phase shift has not occured
    .5 if a phase shift of 90 deg has occured
    1 if a phase shift of 180 has occured
    1.5 if a phase shift of 270 has occured
    
    '''
    # Finding the phase based on the peaks
    bits = []
    
    waveform = np.array(waveform)
    times = np.array(times)
    
    period = 1/freq
    # periods in a time interval
    periods_per_interval = time_int // period

    # Set the first positive peak
    i = np.argmax(times > (times[0] + time_int/2))
    i_period = np.argmax(times > (times[0] + time_int/2 + period))
    wave_after = waveform[i: i_period]
    time_after = times[i: i_period]
    reference_peak = np.argmax(wave_after > amp - error)
    reference_peak_time = time_after[reference_peak]
    
    target_time = times[0] + time_int / 2 + time_int
    
    while target_time +  period < times[-1]:
        
        # the pos peak if phase doesn't change, based on the last peak
        pos_peak_after = reference_peak_time + (periods_per_interval) * period
        
        
        i_before = np.argmax(times > target_time)
        i_after = np.argmax(times > target_time + period)

        wave_after = waveform[i_before: i_after]
        times_after = times[i_before: i_after]
        
        actual_pos_peak_after = times_after[
            np.argmax(wave_after > amp - error)]
        
        difference = abs(actual_pos_peak_after - pos_peak_after) % period
        
        # The margin is the margin of error for the value. a margin of a 
        # period/8 should push the output to the closest of the four phases
        margin = period/8
        
        if difference < margin or difference > period - margin:
            bits.append(0)
        elif difference < period/2 + margin and difference > period/2 - margin:
            bits.append(1)
        elif difference < period/4 + margin and difference > period/4 - margin:
            bits.append(3/2)
        elif (difference < period*(3/4) + margin and 
            difference > period*(3/4) - margin):
            bits.append(1/2)   
        else:
            # for debugging purposes. should never get to this point
            bits.append(difference)
            
        reference_peak_time = actual_pos_peak_after
        target_time += time_int
        
    
    return bits
        
def fourier_phase_shift_checker(times, waveform, delT, freq):
    '''
    

    Parameters
    ----------
    times : TYPE 1D numpy array
        array of times of each measurement of the wave
    waveform : TYPE 1D numpy array
        array of values for each point in the wave
    delT : TYPE float
        time interval between each bit change
    freq : TYPE float
        frequency of the carrier signal

    Returns
    -------
    phases - 1D numpy array of the phase shifts of each bit

    '''
    
    #TODO: What if time is initially not zero
    
    waveform = np.array(waveform) #in case it isn't already
    times = np.array(times)
    
    omega = 2 * np.pi * freq
    
    phases = [] # to be returned
    phase_diffs = [] # it's DIFFERENT from phases (haha)
    currentTime = delT/2 # start at middle of first bit
    delTPrime = 3 * delT/8 # measure outwards 1/4 of a time interval from center
    bit = 0 # keep track of which bit we're on
    
    # index of data to help us determine what to take from waveform
    index = times[times < currentTime - delTPrime].size
    
    # only return phases of bits where enough data is received to make full 
    # measurement
    while times[times > currentTime + delTPrime].size > 0:
        # trim time to relevant period
        # start by trimming above lower bound
        measureTimes = times[times >= currentTime - delTPrime]
        
        # trim top by one bit-length away to get number of indices to jump 
        # in order to get to beginning of next relevant period (if needed)
        measureTimes = measureTimes[measureTimes < currentTime - delTPrime + delT]
        
        indexJump = measureTimes.size
        
        # trim top to top of actual relevant period inside this bit
        measureTimes = measureTimes[measureTimes < currentTime + delTPrime]

        # trim wave to relevant period
        # use index and add length of measureTimes to insure both are the 
        # same length
        measureWave = np.take(waveform, range(index, index + measureTimes.size))
        
        # sums to find kI and kQ for Fourier inner product
        kI = np.sum(measureWave * np.cos(omega * measureTimes))
        kQ = np.sum(measureWave * np.sin(omega * measureTimes))
        
        phases.append(np.arctan2(kQ, kI))
        
        if (bit > 0):
            phase_diffs.append(phases[bit] - phases[bit - 1])

        # move index up to the beginning of the next relevant period
        index += indexJump
        
        # move currentTime up to the middle of the next relevant period
        currentTime += delT
        
        bit += 1
        
    return np.array(phase_diffs) * 180 / np.pi
    

# testing
if __name__ == '__main__':

    waves = []
    
    # works on 90, 180, 270 - [.5, 1, 1.5, 0]
    waves.append([(0.001, 20000, 1, 0), (0.001, 20000, 1, 90),
            (0.001, 20000, 1, 180), (0.001, 20000, 1, 270),
            (0.001, 20000, 1, 0)])

    # works with arbitrary lengths of 0s - [0, 0, 0, 0, 0, 0, 0]
    waves.append([(0.004, 20000, 1, 0), (0.003, 20000, 1, 0), 
                  (0.001, 20000, 1, 0)])
    
    # works with phase shifts then holds - [.05, 0, 0 ,1]
    waves.append([(0.001, 20000, 1, 0), (0.003, 20000, 1, 90), 
                  (0.001, 20000, 1, 180)])
    
    # pushes to nearest phase- [.5, .5, 1, 1, 1.5]
    waves.append([(0.001, 20000, 1, 0), (0.001, 20000, 1, 95), 
                  (0.001, 20000, 1, 85), (0.001, 20000, 1, 190), 
                  (0.001, 20000, 1, 173), (0.001, 20000, 1, 274)])
    
    for wave in waves:
        times, waveform = wg.wave_gen(wave)
        print("iteration begins")
        print(fourier_phase_shift_checker(times, waveform, .001, 20000))
    
    # works on an amplitude that is not 1, as long as amp is constant
    # it could work even if amp isnt constant, but mostly due to the error 
    # margins I allow and I wouldn't push it
    # [.5, 1, 1.5]
    wave = ([(0.001, 20000, 2, 0), (0.001, 20000, 2, 90),
            (0.001, 20000, 2, 180), (0.001, 20000, 2, 270)])
    times, waveform = wg.wave_gen(wave)
    print(phase_shift_checker(times, waveform, .001, 20000, amp = 2))
