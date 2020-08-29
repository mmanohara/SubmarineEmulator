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
    Check the phase shift of the wave at regular intervals (once per bit)
    Based on the bit length specified by delT

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
    phase_diffs - 1D numpy array of the phase shifts of each bit relative to
    previous bit

    '''
    
    waveform = np.array(waveform) # make it a np array in case it isn't already
    times = np.array(times)
    
    # adjust times array to start at t=0
    times = times - times[0]
    
    # define omega
    omega = 2 * np.pi * freq
    
    phases = [] # will hold the phase of the wave at each interval
   
    phase_diffs = [] # will hold the difference of the phase at one interval
    # from the phase of the wave in the previous time interval
    # it's DIFFERENT from phases (haha)
    
    # Each bit has a width of delT. The first bit runs from t = 0 to t = delT
    # we set currentTime to the middle of the bit we are measuring
    # thanks to our excellent foresight, we've adjusted everything to t = 0
    currentTime = delT/2 # thus, this starts us at the middle of the first bit.
    
    # Fourier phase detection requires measurement over an interval
    # delTPrime measures the "radius" outward from the center of that interval
    # The Fourier interval ranges from t = currentTime - delTPrime
    # to t = currentTime + delTPrime
    # so if delTPrime = delT/4, the first bit interval would run from 
    # delT/4 to 3*delT/4, and the interval in the next bit would run from
    # (delT + delT/4) to (delT + 3*delT/4) because the length of a bit is delT
    # delTPrime must remain less than delT/2.
    delTPrime = 3 * delT/8 
    
    bit = 0 # keep track of which bit we're on
    
    # Trimming the arrays to keep only the relevant data to integrate over
    # for our measurement interval is a real pain, so I use this index value
    # to help mark off intervals.
    # Here, I want to set the index value to indicate the index (in the times
    # array) of the first element that WILL be included in the very first
    # Fourier measurement interval (beginning @ t = 0). The value in brackets
    # ("times < currentTime - delTPrime") is true for all elements that 
    # PRECEDE the first element to be included in measurement. ".size" counts
    # how many such elements are in the times array, and that number will be 
    # the index of the next element - the first one that is IN the measurement
    # interval. 
    index = times[times < currentTime - delTPrime].size
    
    # The value in the bracket ("times > currentTime + delTPrime") is true 
    # for any values lying above the upper bound of the current measurement 
    # interval. Thus, if .size here is nonzero, more values exist beyond the 
    # top of the current interval, and enough values exist to take a full 
    # interval measurement. If .size is zero, not enough values exist for a 
    # full Fourier interval to be taken, and the while loop ends.
    while times[times > currentTime + delTPrime].size > 0:
        # We trim off any time values below the lower bound of the measurement 
        # interval - any lying more than delTPrime below currentTime
        # (where currentTime is the middle of the bit)
        measureTimes = times[times >= currentTime - delTPrime]
        
        # We then trim off any time values that are more than one bit-length
        # ABOVE the lower bound of our Fourier interval. measureTimes now 
        # spans from the beginning of this interval to what will become the 
        # beginning of the next interval.
        measureTimes = measureTimes[measureTimes < currentTime - delTPrime + delT]
        
        # Given the span of measureTimes, we take its size. Now, we can use
        # indexJump to move the current index from the beginning of this
        # interval to the beginning of the next interval once we're done here.
        indexJump = measureTimes.size
        
        # Now, we trim the top off of measureTimes again - now it contains
        # only the time values that are inside our measurement interval.
        measureTimes = measureTimes[measureTimes < currentTime + delTPrime]

        # "index" is the index in times/waveform where our measurement begins
        # Using index (as a start point) and the size of measureTimes
        # (which now holds only the measurement interval), 
        # we can trim measureWave from waveform so that it holds the waveform
        # values that correspond to each of the time values in measureTimes.
        # measureTimes and measureWave should now be the same length.
        measureWave = np.take(waveform, range(index, index + measureTimes.size))
        
        # With the appropriately trimmed intervals, we now
        # sum to find kI and kQ for Fourier inner product
        kI = np.sum(measureWave * np.cos(omega * measureTimes))
        kQ = np.sum(measureWave * np.sin(omega * measureTimes))
        
        phases.append(np.arctan2(kQ, kI))
        
        # We don't calculate a phase difference for the first bit
        # It's the baseline
        if (bit > 0):
            phase_diffs.append(phases[bit] - phases[bit - 1])

        # Move index up to the beginning of the next relevant period
        index += indexJump
        
        # Move currentTime up to the middle of the next relevant period
        currentTime += delT
        
        # Move on to the next bit
        bit += 1
        
    # Negative to counteract the integrals that make it negative (??)
    return -np.array(phase_diffs) * 180 / np.pi
    

def phase_to_bit(phase_diffs):
    '''
    

    Parameters
    ----------
    phases : TYPE 1D numpy array
        1D numpy array of phase shifts relative to previous bit

    Returns
    bits : TYPE 1D numpy array of bits (1, 0)
    -------
    None.

    '''
    
    bits = []
    
    for diff in phase_diffs:
        diff = diff % 360
        if diff < 90:
            bits.append(0)
        elif diff < 270:
            bits.append(1)
        else:
            bits.append(0)
    
    bits = np.array(bits)
    
    return bits

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
        #print(fourier_phase_shift_checker(times, waveform, .001, 20000))
        print(phase_to_bit(fourier_phase_shift_checker(times, waveform, .001, 20000)))
    
    # works on an amplitude that is not 1, as long as amp is constant
    # it could work even if amp isnt constant, but mostly due to the error 
    # margins I allow and I wouldn't push it
    # [.5, 1, 1.5]
    wave = ([(0.001, 20000, 2, 0), (0.001, 20000, 2, 90),
            (0.001, 20000, 2, 180), (0.001, 20000, 2, 270)])
    times, waveform = wg.wave_gen(wave)
    print(phase_shift_checker(times, waveform, .001, 20000, amp = 2))
