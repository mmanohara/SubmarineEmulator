#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 00:54:53 2020

@author: Reuben

Provides a function to generate a phase-modulated waveform of a given
frequency over a fixed time period.

"""

import numpy as np
import matplotlib.pyplot as plt


def wave_gen_phase_modulated(time_list=[], freq=2400, num_pts=1000):
    """Stitch together a waveform with a 180-degree phase shift occuring after
    each listed amount of time. The phase shift begins at 0.

    Parameters
    ----------
    time_list : 1D array_like of reals
        Each real number represents a time interval, after which the phase
        will be flipped 180 degrees. The default is [].

    num_pts : positive int
        Number of points to generate for each wave in the waveform per unit
        time. The default is 1000.

    freq : real
        Frequency of the output waveform. The default is 2400Hz.

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

    for time in time_list:
        # Flip the phase.
        phase_shift += np.pi

        # Generate evenly spaced array of points.
        wave_times = np.linspace(times[len(times)-1],
                                 times[len(times)-1] + time,
                                 int(num_pts * time))

        # Concatenate list of times with existing list.
        times = np.concatenate((times, wave_times))

        # Generate sinusoid.
        wave = np.sin(2 * np.pi * freq * wave_times + phase_shift + 10)

        # Concatenate generated wave with existing waveform.
        waveform = np.concatenate((waveform, wave))

    return (times, waveform)



# Code testing region.
if __name__ == '__main__':

    # List of times corresponding to each phase flip.
    wave_list = [1, 3, 4, 2.1, 3.14, 5.74]

    # Generate and store waveform and corresponding times.
    times, waveform = wave_gen_phase_modulated(wave_list, freq=0.5)

    plt.figure()
    plt.plot(times, waveform, label='Combined Waveform')
    plt.legend
    plt.show()