#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 18:58:09 2020

@author: Reuben Rosenberg

Provides a function to generate a frequency modulated waveform over a fixed
 time period.

"""

import numpy as np
import matplotlib.pyplot as plt


def wave_gen_FM(wave_set=[], num_pts=1000):
    """Stitch together a series of waveforms of given frequency and length.

    Parameters
    ----------
    wave_set : 1D array_like of 2-tuples
        Each 2-tuple represents a wave, with the first value being
        the frequency and the second the duration. The default is [].

    num_pts : positive int
        Number of points to generate for each wave in the waveform.
        The default is 1000.

    Returns
    -------
    times : 1D numpy array
        List of times corresponding to each point in the waveform.

    waveform : 1D numpy array
        Combined waveform.

    """
    waveform = np.zeros(1)
    times = np.zeros(1)

    # Generate each wave and concatenate with existing waveform.
    for freq, time in wave_set:
        # Generate evenly spaced array of points.
        wave_times = np.linspace(times[len(times)-1],
                                 times[len(times)-1] + time, num_pts)

        # Concatenate list of times with existing list.
        times = np.concatenate((times, wave_times))

        # Generate sinusoid.
        wave = np.sin(2 * np.pi * freq * wave_times)

        # Concatenate generated wave with existing waveform.
        waveform = np.concatenate((waveform, wave))

    return (times, waveform)


# Code testing region.
if __name__ == '__main__':

    # List of waves to combine define in terms of frequency and duration.
    wave_list = [(1000, .002), (5000, .001), (3000, .004), (554, 0.003)]

    # Generate and store waveform and corresponding times.
    times, waveform = wave_gen_FM(wave_list)

    plt.figure()
    plt.plot(times, waveform, label='Combined Waveform')
    plt.legend
    plt.show()

