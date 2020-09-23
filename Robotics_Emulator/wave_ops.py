# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 17:26:18 2020

@author: mohit

This file operates on waves, which are time list and amplitude list tuples.

combine_wave combines two waves using a linear interpolation for estimating the
value of waves between points

delay_wave delays the time value of a wave.
"""
import numpy as np
from wave_gen import wave_gen
import matplotlib.pyplot as plt

def combine_wave(packet1, packet2):
    '''
    A function that combines two waves together to superpose them, even if
    their times list do not line up properly. It adds the two waves, but
    linearly interpolates between points in the time lists. Can also handle
    time lists with different sampling rates (but this hasn't been tested
    properly).

    Parameters
    ----------
    packet1 : 2-tuple of 1d array-like
        The first array corresponds to the list of times, and the second to the
        amplitudes of the waves at those points. The output of wave_gen can
        directly feed into this argument. This is one of the waves being 
        combined.
    packet2 : 2-tuple of 1d array-like
        Same as above.

    Returns
    -------
    2-tuple of 1d array-like. This corresponds to the combined wave and has
    the same format as a wave_gen output.

    '''
    # Figure out which wave packet goes first. Order of inputs doesn't matter
    # because of this.
    times1 = packet1[0]
    waves1 = packet1[1]
    times2 = packet2[0]
    waves2 = packet2[1]
    firstt, firstw = (times1, waves1) if times1[0] < times2[0] else (times2, waves2)
    lastt, lastw = (times2, waves2) if times1[0] < times2[0] else (times1, waves1)
    firsti = 0
    lasti = 0
    final_times = []
    final_waves = []
    # Add points of the first (chronological) wave until the second wave starts
    # to matter.
    while firsti != len(firstt) and firstt[firsti] < lastt[lasti]:
        final_times.append(firstt[firsti])
        final_waves.append(firstw[firsti])
        firsti += 1
        
    # Loop until both lists are empty.
    while True:
        # Edge case firstt runs out. Add the rest of the points and break.
        if firsti == len(firstt):
            while lasti < len(lastt):
                final_times.append(lastt[lasti])
                final_waves.append(lastw[lasti])
                lasti += 1
            break
        # Edge case lastt runs out. Add the rest of the points and break.
        elif lasti == len(lastt):
            while firsti < len(firstt):
                final_times.append(firstt[firsti])
                final_waves.append(firstw[firsti])
                firsti += 1
            break
        # Case last time is less. Interpolate the value of the first wave and
        # add it to the value of the last wave.
        elif lastt[lasti] < firstt[firsti]:
            final_times.append(lastt[lasti])
            final_waves.append(lastw[lasti] + \
        (firstw[firsti] - firstw[firsti - 1]) /\
        (firstt[firsti] - firstt[firsti - 1]) * (lastt[lasti] - firstt[firsti - 1])\
            + firstw[firsti - 1])
            lasti += 1
        # Case first time is less. Interpolate the value of the last wave and
        # add it to the value of the first wave.
        elif lastt[lasti] > firstt[firsti]:
            final_times.append(firstt[firsti])
            final_waves.append(firstw[firsti] +\
        (lastw[lasti] - lastw[lasti - 1]) /\
        (lastt[lasti] - lastt[lasti - 1]) * (firstt[firsti] - lastt[lasti - 1])\
            + lastw[lasti - 1])
            firsti += 1
        # If they are equal, simply add the two waves together.
        else:
            final_times.append(firstt[firsti])
            final_waves.append(firstw[firsti] + lastw[lasti])
            firsti += 1
            lasti += 1
    return (np.array(final_times), np.array(final_waves))

def delay_wave(packet, delay):
    '''
    This function takes a wave packet and delays it by a certain amount of
    time.

    Parameters
    ----------
    packet : 2-tuple of 1d array-like
        The first array corresponds to the list of times, and the second to the
        amplitudes of the waves at those points. The output of wave_gen can
        directly feed into this argument. This is the wave being delayed
    delay : float
        Time delay to delay the wave by.

    Returns
    -------
    
    2-tuple of 1d array-like. This corresponds to the delayed wave and has
    the same format as a wave_gen output.

    '''
    return (packet[0] + delay, packet[1])

if __name__ == "__main__":
    # Code testing region
    # Combine a wave with itself
    packet = wave_gen([(0.001, 20000, 1, 0)])
    # Results in a wave of amplitude 2
    plt.figure()
    plt.plot(combine_wave(packet, packet)[0], combine_wave(packet, packet)[1])
    plt.show()
    # Combine waves of different frequencies
    packet1 = wave_gen([(0.001, 20000, 1, 0)])
    packet2 = wave_gen([(0.001, 30000, 1, 0)])
    plt.figure()
    plt.plot(combine_wave(packet1, packet2)[0], combine_wave(packet1, packet2)[1])
    plt.show()
    
    # Delay a wave by a small amount and plot it
    packet = wave_gen([(0.001, 20000, 1, 0)])
    plt.figure()
    # You can also switch the order for no consequence
    plt.plot(combine_wave(delay_wave(packet, 0.0004), packet)[0], \
             combine_wave(packet, delay_wave(packet, 0.0004))[1])
    plt.show()
        
    # Delay a complicated wave by a small and large amount and then plot
    waves = [(0.001, 20000, 1, 0), (0.003, 20000, 1, 90), 
                  (0.001, 20000, 1, 180)]
    # Show original wave
    packet = wave_gen(waves)
    plt.figure()
    plt.plot(packet[0], packet[1])
    plt.show()
    # Delay by small and large amount
    packet2 = delay_wave(packet, 0.002)
    packet3 = delay_wave(packet, 0.2)
    final_packet1 = combine_wave(packet, packet2)
    final_packet2 = combine_wave(packet, packet3)
    # Show small delay
    plt.figure()
    plt.plot(final_packet1[0], final_packet1[1])
    plt.show()
    # Show large delay
    plt.figure()
    plt.plot(final_packet2[0], final_packet2[1])
    plt.show()
        
            
            
    

