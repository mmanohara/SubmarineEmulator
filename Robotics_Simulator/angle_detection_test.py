# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 18:30:31 2020

@author: mohit

This code is to use for testing the angle detection algorithm.
"""

import numpy as np
import matplotlib.pyplot as plt
import waveform_generator_phase_modulated as pm

SPEED_OF_SOUND = 1480 # meters per second

def gen_doa_waveform(doa=np.array([0, 0, 1]), freq=30000, time_length = 0.001, 
                     spacing = 0.01778, time_shift='rand'):
    """
    

    Parameters
    ----------
    angle : 3-vector or DOA
       The angle at which the incoming waveform is arriving (x, y, z). Assume the 
       following coordinate system with hydrophone positions:
           y
           |
           |
        1  |  2
           |
    _____Z(.)__________x
           |
        4  |  3
           |
        
    time_shift : float, optional
        Global time shift of all waveforms, corresponding to shift from 
        origin of wave. Default is randomly generated.

    Returns
    -------
    Tuple of lists of arrays. First is the 4 times arrays, second is the 4 
    waveform arrays.
    """
    # normalize doa
    ndoa = doa / np.linalg.norm(doa)
    if time_shift == 'rand':
        time_shift = 3*np.random.rand()
    # Assume that incident wave is at point 4.
    times4, waves4 = pm.wave_gen_phase_modulated([time_length], freq=freq, num_pts=1000000)
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
    