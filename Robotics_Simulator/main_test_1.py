# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 19:35:25 2020

@author: Mohith Manohara

For now, all the code is in one file. However, we may want to branch out to
multiple files as we add different capabilities.

Things to consider:
    1. We want the receiver to detect the frequency of the input waveform, so
        we need a "sampling" mechanism on the receiver and a quick frequency
        detection algorithm (can do via inner products; will explain)
    2. We want to be able to generate waveforms of different frequencies and
        phase settings, so we should have functionality to add (for example)
        200us of 30kHz sine, 200us of 40kHz sine, and stitch them together.
        We also want to be able to arbitrarily adjust the starting phase of the
        signals; For example, we start off with a sine but what if we instead
        generated a negative sine to implement differential phase key shifting?
    3. We need a way to incorporate noise; white gaussian noise, etc
    4. We should try to also incorporate angle of detection; to do this we will
        need to model the four hydrophones' positions and the received waveform
        at each hydrophone to calculate direction of arrival of the signal.

    As we implement more functionality, we will get a better and better
    emulator of our system, and this will be an extremely useful tool for
    comms; we can test different signal encoding mechanisms and ultimately
    decide on one to implement and test first.

    Hydrophones are wack.

"""
import numpy as np
import matplotlib.pyplot as plt
import waveform_generator_frequency_modulated as fm

'''
IMPORTANT NOTE: ALL UNITS ARE IN SI STANDARD UNITS. Thus, speed is in m/s,
frequency is in Hz, positions in m, etc.
'''
# Speed of sound in water
speed_of_sound = 1480

def simulate(c, freq, sub_position_1, sub_position_2, sub_velocity_1, \
             sub_velocity_2, simulated_time = 0.001, n_points = 1000):
    '''
    Holy crap Anaconda Spyder is very nice at autogenerating these docstrings
    Anyways this is the simulation function. We can change the organization of
    these simul

    Parameters
    ----------
    c : TYPE float
        DESCRIPTION.
        Speed of the wave. This will be the speed of sound in water for most
        applications.

    freq : TYPE float (preferably integer)
        DESCRIPTION.
        Frequency we are transmitting waves at.

    sub_position_1 : TYPE 2D (3D) numpy array
        DESCRIPTION.
        Position of the first submarine (for now doing 2D sims, will do 3D sims
                                         when it becomes appropriate.)
    sub_position_2 : TYPE 2D (3D) numpy array
        DESCRIPTION.
        Position of the second submarine

    sub_velocity_1 : TYPE 2D (3D) numpy array
        DESCRIPTION.
        Velocity of the first submarine

    sub_velocity_2 : TYPE 2D (3D) numpy array
        DESCRIPTION.
        Velocity of the second submarine. Currently not implemented.

    simulated_time : TYPE, optional
        DESCRIPTION.
        Time to run the simulation for.
        The default is 0.001, which is 1ms of waves.

    n_points : TYPE, optional
        DESCRIPTION.
        Number of points to ping from one sub to another, equally spaced out in
        the simulated time.
        The default is 1000.

    Operation:
        The way the function works is that we generate a set of times that we
        send samples of the waveform from sub 1 to sub 2. That is, we generate
        samples of a pure sine wave and the times corresponding to the samples.
        We then calculate 2 things: first, the times that each sample get to
        the second submarine; second, the amplitude of the sample as it gets
        to the second submarine (because it will decrease in amplitude). We
        work in the reference frame of the receiving submarine because then
        calculating the time the wave arrives is simply distance over velocity.
        The amplitude scales as 1/r so we simply use that.

    Returns
    -------
    Returns a tuple containing the input waveform pinged by sub 1 (as numpy
                                                                   array)
    and a tuple containing the received waveform by sub 2 (as numpy array)

    '''
    lamb = c / freq # wavelength
    # Generate a waveform
    times, input_waveform = fm.wave_gen_FM([(20000, 0.00025), (40000, 0.0005), (20000, 0.00025)])
    #input_waveform = np.sin(2*np.pi*freq * times) # Need angular velocity for
                                                  # waveforms
    # For simplicity, calculate the relative velocity of sub 1 relative to sub 2.
    sub1_rel_velo = sub_velocity_1 - sub_velocity_2

    # Calculate the initial position of sub 1 relative to sub 2
    sub1_init_pos = sub_position_1 - sub_position_2

    # Relative positions of sub 1 every time it makes a ping.
    sub1_poses = np.array([sub1_init_pos + times[i]*sub1_rel_velo \
                           for i in range(len(times))])

    # Calculate the distance the wave travels for each sample; axis=1 lets us
    # calculate the distance for each sample.
    travel_distances = np.linalg.norm(sub1_poses, axis=1)

    # times at which points are received is just distance divided by wave speed
    received_times = times + travel_distances / c

    # Calculate the magnitude of the pings at the received sub
    output_waveform = input_waveform / travel_distances

    # Return (input_times, input_wave) and (received_times, received_wave)
    return ((times, input_waveform), (received_times, output_waveform))

def main():
    '''
    The function starts with a simulation of the transmitted vs received
    waveform of one sub to another at user defined frequency and positions. The
    subs may be moving relative to one another, which we need to account for.

    Returns
    -------
    None.

    '''
    c = speed_of_sound
    # Frequencies are on the order of kilohertz so we will use those
    freq = 30000
    # Calculate the wavelength in case it's used for something
    lamb = c/freq
    # Set initial sub positions and velocities (can modify as necessary)
    sub_position_1 = np.array([0, 0])
    sub_position_2 = np.array([c/5, 0])
    sub_velocity_1 = np.array([-10, 0])
    sub_velocity_2 = np.array([0, 0])
    # Simulate and get the input and output waveforms
    in_, out = simulate(c, freq, sub_position_1, sub_position_2, \
             sub_velocity_1, sub_velocity_2)
    # Plot the waveforms.
    plt.figure()
    plt.plot(in_[0], in_[1], c='b', label="Input waveform")
    plt.legend()
    plt.show()
    plt.figure()
    plt.plot(out[0], out[1], c='r', label="Output waveform")
    plt.legend()
    plt.show()

if __name__=='__main__':
    main()