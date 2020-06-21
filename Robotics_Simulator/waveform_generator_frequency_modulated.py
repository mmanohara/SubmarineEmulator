#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 18:58:09 2020

@author: Reuben Rosenberg

Provides a function to generate a frequency modulated waveform over a fixed
time period with optional smoothing implemented through phase shifts.

"""

import numpy as np
import matplotlib.pyplot as plt

# Constant for the minimum amplitude gap left between waves at a
# frequency transition when phase smoothin is enabled.
SMOOTHING_GAP = 10e-5


def wave_gen_FM(wave_set=[], num_pts=1000, smoothing="None"):
    """Stitch together a series of waveforms of given frequency and length.

    Parameters
    ----------
    wave_set : 1D array_like of 2-tuples
        Each 2-tuple represents a wave, with the first value being
        the frequency and the second the duration. The default is [].

    num_pts : positive int
        Number of points to generate for each wave in the waveform per unit
        time. The default is 1000.

    smoothing : {'None', 'phase'}
        If set to 'phase', smooth frequency transitions by performing phase
        shifts. Perform no smoothing if 'None'. The default is 'None'.

    Returns
    -------
    times : 1D numpy array
        List of times corresponding to each point in the waveform.

    waveform : 1D numpy array
        Combined waveform.

    """
    waveform = np.zeros(1)
    times = np.zeros(1)
    phase_shift = 0

    # Generate each wave and concatenate with existing waveform.
    for freq, time in wave_set:
        # Generate evenly spaced array of points.
        wave_times = np.linspace(times[len(times)-1],
                                 times[len(times)-1] + time,
                                 int(num_pts * time))

        # Concatenate list of times with existing list.
        times = np.concatenate((times, wave_times))

        # If set to perform phase smoothing, add a phase shift to bring
        # starting value of new wave within the preset threshold of the ending
        # value of the previous wave, preventing sudden jumps in the waveform.
        if smoothing == 'phase':
            phase_shift = (np.arcsin(waveform[-1] - SMOOTHING_GAP)
                            - 2 * np.pi * freq * wave_times[0])

        # Generate sinusoid.
        wave = np.sin(2 * np.pi * freq * wave_times + phase_shift)

        # Concatenate generated wave with existing waveform.
        waveform = np.concatenate((waveform, wave))

    return (times, waveform)


# Code testing region.
if __name__ == '__main__':

    # List of waves to combine define in terms of frequency and duration.
    wave_list = [(3.564, 5), (1.3, 5), (2.5839, 5)]

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
