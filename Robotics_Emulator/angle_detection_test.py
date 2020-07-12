# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 18:30:31 2020

@author: mohit

This code is to use for testing the angle detection algorithm.
"""

import numpy as np
import matplotlib.pyplot as plt
import waveform_generator_phase_modulated as pm
import signal_angle_detect as sad

SPEED_OF_SOUND = 1480 # meters per second

def gen_doa_waveform(doa=np.array([0, 0, 1]), freq=30000, time_length = 0.003, 
                     spacing = 0.01778, time_shift='rand'):
    """
    

    Parameters
    ----------
    doa : numpy array 3-vector
        This describes in x, y, and z the direction of arrival of the ping
        signal. The coordinate system is
        
        y
        |
        |
     1  |  2
        |
________.________x
        |z
     4  |  3
        | 
        |
        
    The doa will get normalized, so its norm doesn't matter.
    freq : Float, units: Hz
        Frequency of the wave to be generated.
    time_length : Float, units: s
        Time length for the wave to be generated. Default is 3 ms.
    spacing : Float, units: m
        Spacing between the hydrophones. The default is 0.01778, which is 0.7in.
    time_shift : Float, units: s
        Global time shift for all input waves. The default is a random setting.

    Returns
    -------
    times
        A list of times at which sampled waveforms appear. There are 4 of these
        each corresponding to one of the hydrophones.
    waves
        A list of the actual waveforms at each of the hydrophones. Given that
        this is assumed to be a plane wave and the hydrophones don't affect 
        the wave at all by assumption, it's the same for all four.
    """
    # normalize doa
    ndoa = doa / np.linalg.norm(doa)
    if time_shift == 'rand':
        time_shift = 3*np.random.rand()
    # Assume that incident wave is at point 4.
    times4, waves4 = pm.wave_gen_phase_modulated([time_length], freq=freq, num_pts=3000000)
    # Global time shift
    times4 += time_shift * np.ones(times4.shape)
    # Generate individual time shifts based on their distance and direction.
    times3 = times4 + ndoa[0] / SPEED_OF_SOUND * spacing * np.ones(times4.shape)
    times1 = times4 + ndoa[1] / SPEED_OF_SOUND * spacing * np.ones(times4.shape)
    times2 = times3 + ndoa[1] / SPEED_OF_SOUND * spacing * np.ones(times4.shape)
    
    return ([times1, times2, times3, times4], [waves4, waves4, waves4, waves4])

if __name__=='__main__':
    # Code testing region
    # Generate DOA
    doa = np.array([1, 2, 0])
    freq = 25000 #Hz
    time_length = 0.002 #s
    spacing = 0.01778 #m, corresponds to 0.7in
    time_shift = 0.5 #s
    times, waves = gen_doa_waveform(doa, freq, time_length, spacing, time_shift)
    fig = plt.figure()
    for i in range(4):
        plt.plot(times[i], waves[i], label="{}".format(i + 1))
    fig.axes[0].set_xlim(0.500, 0.5001)
    plt.xlabel("Time (s)")
    plt.ylabel("Voltages (V)")
    plt.legend()
    
    chase_doa = sad.signal_angle_detect(SPEED_OF_SOUND, freq, spacing, times, waves)
    
    print(doa)
    print(chase_doa)
    