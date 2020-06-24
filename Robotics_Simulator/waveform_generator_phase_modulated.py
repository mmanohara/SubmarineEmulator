#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 00:54:53 2020

@author: Reuben

This file prrovides a function to generate a phase-modulated sinusoidal
waveform of a given frequency and amplitude over a fixed time period with
optional phase shifting.

"""

import numpy as np
import matplotlib.pyplot as plt


def wave_gen_phase_modulated(
        wave_list=[], freq=2400, num_pts=1000, amplitude=1):
    """
    Stitch together a phase-modulated waveform.

    Parameters
    ----------
    wave_list : array_like of 2-tuples of float
        For each tuple, the first entry specifies a time interval for the wave
        segment, and the second entry specifies the phase shift in degrees.
        The default is [].

    num_pts : positive int
        Number of points to generate for each wave segment.
        The default is 1000.

    freq : float
        Frequency of the output waveform. The default is 2400Hz.

    amplitude : float
        Amplitude of the output waveform. The default is 1.

    Returns
    -------
    times : 1D numpy array
        List of times corresponding to each point in the waveform.

    waveform : 1D numpy array
        List of amplitudes comprising the final waveform.

    """
    waveform = np.zeros(1)
    times = np.zeros(1)

    # If optional phase shift is not provided, add shift of zero.
    for time, phase_shift in wave_list:

        # Generate evenly spaced array of points.
        wave_times = np.linspace(times[len(times)-1],
                                 times[len(times)-1] + time,
                                 int(num_pts * time))

        # Concatenate list of times with existing list.
        times = np.concatenate((times, wave_times))

        # Generate sinusoid.
        wave = amplitude * np.sin(
            2 * np.pi * (freq * wave_times + phase_shift / 360)
        )

        # Concatenate generated wave with existing waveform.
        waveform = np.concatenate((waveform, wave))

    return (times, waveform)


# Code testing region.
if __name__ == '__main__':

    # List of times corresponding to each phase flip.
    wave_list = [(1, 180), (3, 45), (4, 0),
                 (2.1, 180), (3.14, 90), (5.74, 270)]

    # Generate and store waveform and corresponding times.
    times, waveform = wave_gen_phase_modulated(wave_list, freq=0.5)

    plt.figure()
    plt.plot(times, waveform, label='Combined Waveform')
    plt.legend
    plt.show()
