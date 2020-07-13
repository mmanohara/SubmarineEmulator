#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 18:58:09 2020

@author: Reuben Rosenberg

This file provides a function to generate a frequency-modulated sinusoidal
waveform of a given amplitude over a fixed time period with optional
smoothing implemented via phase shifts.

"""

import numpy as np
import matplotlib.pyplot as plt

# Constant for the minimum amplitude gap left between waves at a
# frequency transition when phase smoothin is enabled.
SMOOTHING_GAP = 10e-5


def wave_gen_FM(wave_list=[], num_pts=1000, smoothing="None", amplitude=1):
    """Stitch together a series of waveforms of given frequency and length.

    Parameters
    ----------
    wave_list : 1D array_like of 2-tuples
        Each 2-tuple represents a wave segment, with the first value specifying
        the duration and the second the frequency. The default is [].

    num_pts : positive int
        Number of points to generate for each wave in the waveform.
        The default is 1000.

    smoothing : {'None', 'phase'}
        If set to 'phase', smooth frequency transitions by performing phase
        shifts. Perform no smoothing if 'None'. The default is 'None'.

    amplitude : float
        Amplitude of the generated waveform. The default is 1.

    Returns
    -------
    times : 1D numpy array
        List of times corresponding to each point in the waveform.

    waveform : 1D numpy array
        List of amplitudes comprising the combined waveform.

    """
    waveform = np.zeros(1)
    times = np.zeros(1)
    phase_shift = 0

    # Generate each wave and concatenate with existing waveform.
    for time, frequency in wave_list:
        # Generate evenly spaced array of points.
        wave_times = np.linspace(times[len(times)-1],
                                 times[len(times)-1] + time,
                                 num_pts)

        # Concatenate list of times with existing list.
        times = np.concatenate((times, wave_times))

        # If set to perform phase smoothing, add a phase shift to bring
        # starting value of new wave within the preset threshold of the ending
        # value of the previous wave, preventing sudden jumps in the waveform.
        if smoothing == 'phase':
            phase_shift = (np.arcsin(waveform[-1] - SMOOTHING_GAP)
                           - 2 * np.pi * frequency * wave_times[0])

        # Generate sinusoid.
        wave = amplitude * np.sin(2 * np.pi * frequency
                                  * wave_times + phase_shift)

        # Concatenate generated wave with existing waveform.
        waveform = np.concatenate((waveform, wave))

    return (times, waveform)


# Code testing region.
if __name__ == '__main__':

    # List of waves to combine define in terms of frequency and duration.
    wave_list = [(0.00025, 20000), (0.0005, 40000), (0.00025, 20000)]

    # Generate and store waveform and corresponding times.
    times, waveform = wave_gen_FM(wave_list, smoothing='phase')

    plt.figure()
    plt.plot(times, waveform, label='Combined Waveform')
    plt.legend
    plt.show()

    times, waveform = wave_gen_FM(wave_list, smoothing='None')

    plt.figure()
    plt.plot(times, waveform, label='Combined Waveform')
    plt.legend
    plt.show()
