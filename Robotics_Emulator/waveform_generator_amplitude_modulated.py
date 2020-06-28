#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 17:16:38 2020

@author: Reuben

This file provides a function that generates an amplitude-modulated sinusoidal
waveform over a fixed time period.

# TODO: Fix FM generator to match this one.

"""

import numpy as np
import matplotlib.pyplot as plt


def wave_gen_AM(wave_list=[], num_pts=1000, frequency=2400, smoothing="None"):
    """
    Stitch together a series of sinusoids of given amplitude and length.

    Parameters
    ----------
    wave_list : 1D array_like of 2-tuples
        Each 2-tuple represents a wave segment, with the first value specifying
        the duration and the second specifying the amplitude.
        The default is [].

    num_pts : positive int
        Number of points to generate for each wave. The default is 1000.

    frequency : float
        Frequency of the waveform in Hertz.

    Returns
    -------
    times : 1D numpy array
        List of times corresponding to each point in the combined waveform.

    waveform : 1D numpy array
        List of amplitudes comprising the combined waveform.

    """
    waveform = np.zeros(1)
    times = np.zeros(1)

    # Generate each wave and concatenate with existing waveform.
    for time, amplitude in wave_list:
        # Generate evenly spaced array of points.
        wave_times = np.linspace(
            times[len(times)-1], times[len(times)-1] + time, num_pts
        )

        # Concatenate list of times with existing list.
        times = np.concatenate((times, wave_times))

        # Generate sinusoidal segment.
        wave = amplitude * np.sin(2 * np.pi * frequency * wave_times)

        # Concatenate generated wave with existing waveform.
        waveform = np.concatenate((waveform, wave))

    return (times, waveform)


# Code testing region.
if __name__ == '__main__':

    # List of waves to combine define in terms of frequency and duration.
    wave_list = [(1, 3.5), (1, 25), (1, 10)]

    # Generate and store waveform and corresponding times.
    times, waveform = wave_gen_AM(wave_list, frequency=10)

    # Plot test output.
    plt.figure()
    plt.plot(times, waveform, label='Combined Waveform')
    plt.legend
    plt.show()
