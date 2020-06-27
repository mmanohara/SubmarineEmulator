#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 22:53:06 2020

@author: Reuben

This file provides a function that generates an amplitude-modulated sinusoidal
waveform over a fixed time period.

# TODO: Fix FM generator to match this one.

"""

import numpy as np
import matplotlib.pyplot as plt


def wave_gen(wave_segments=[], num_pts=1000, smoothing="None"):
    """
    Stitch together a series of sinusoids of based on the given parameters.

    Each segment is specified by its duration, frequency, amplitude, and
    relative phase to allow for phase, amplitude, or frequency modulation
    or some combination. The input format for specifying each wave segment is
    (duration, frequency, amplitude, relative phase). The phase for each wave
    segment is relative to the previous segment (with the phase initialized to
    zero for the first segment).

    Smoothing using phase shifting is available, but it is obviously not
    compatible with any form of phase modulation.

    Parameters
    ----------
    wave_segments : 1D array-like of 4-tuples
        Each tuple represents a single wave segment, with the duration,
        frequency, amplitude, and the phase shift (relative to the previous
        segment) specified by the entries in that order. The default is [].

    num_pts : positive int
        Number of points to generate for each wave segment.
        The default is 1000.

    Returns
    -------
    times : 1D numpy array
        List of times corresponding to each point in the combined waveform.

    waveform : 1D numpy array
        List of magnitudes comprising the combined waveform.

    """
    waveform = np.zeros(1)
    times = np.zeros(1)
    phase = 0

    # Generate each wave and concatenate with existing waveform.
    for time, frequency, amplitude, phase_shift in wave_segments:
        # Generate evenly spaced array of points.
        wave_times = np.linspace(
            times[len(times)-1], times[len(times)-1] + time, num_pts
        )

        # Concatenate list of times with existing list.
        times = np.concatenate((times, wave_times))

        # Update phase.
        phase = (phase + phase_shift) % 360
        print(phase)

        # Generate sinusoidal segment.
        wave = amplitude * np.sin(
            2 * np.pi * (frequency * wave_times + phase / 360)
        )

        # Concatenate generated wave segment with existing waveform.
        waveform = np.concatenate((waveform, wave))

    return (times, waveform)


# Code testing region.
if __name__ == '__main__':
    waves = []

    # Example of frequency modulation
    waves.append(
        [(0.001, 4000, 1, 0), (0.002, 2000, 1, 0), (0.005, 3000, 1, 0)]
    )

    # Example of phase modulation
    waves.append(
        [(0.001, 2000, 1, 0), (0.001, 2000, 1, 180), (0.001, 2000, 1, 270)]
    )

    # Example of amplitude modulation
    waves.append(
        [(0.001, 2000, 3.5, 0), (0.001, 2000, 25, 0), (0.001, 2000, 10, 0)]
    )

    # Example of mixed amplitude and phase modulation
    waves.append(
        [(0.001, 2000, 5.6, 0), (0.001, 2000, 12, 180), (0.001, 2000, 29, 0)]
    )

    # Example of mixed amplitude and frequency modulation
    waves.append(
        [(0.001, 4000, 3, 0), (0.002, 2000, 1.6, 0), (0.005, 3000, 6, 0)]
    )

    # Generate and plot example waveforms.
    for wave in waves:
        times, waveform = wave_gen(wave)

        # Plot test output.
        plt.figure()
        plt.plot(times, waveform, label='Combined Waveform')
        plt.legend
        plt.show()
