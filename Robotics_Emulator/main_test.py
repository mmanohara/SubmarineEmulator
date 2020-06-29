# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 19:35:25 2020

@author: Mohith Manohara

This file provides the main function for running the inter-sub communication
emulator.

NOTE: ALL QUANTITIES ARE IN SI UNITS.
Thus, speed is in m/s,frequency is in Hz, positions in m, etc.

Considerations:
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
from wave_gen import wave_gen


# Speed of sound in water
SPEED_OF_SOUND = 1480


def emulate(wave_speed, frequency, transmitter_pos_init, receiver_pos_init,
            transmitter_velocity, receiver_velocity,
            duration=0.001, n_points=1000):
    """
    Holy crap Anaconda Spyder is very nice at autogenerating these docstrings.

    (Thanks, Mohith.) Anyways this is the emulation function. We can change
    the organization of these emulations as we develop the code further.

    Problems
    --------
    The duration parameter is currently unused.

    The change in wave speed when switching from the 'rest' frame of the
    water to the rest frame of the receiver is unaccounted for.


    Parameters
    ----------
    wave_speed : float
        Speed of the wave. This will be the speed of sound in water for most
        applications.

    frequency : float (preferably integer)
        Frequency of the transmitted wave.

    transmitter_pos_init : 2D (3D) numpy array
        Initial position of the transmitting submarine.
        (For now we are doing 2D emulations.We will do 3D when it becomes
         appropriate.)

    receiver_pos_init : 2D (3D) numpy array
        Initial position of the receiving submarine.

    transmitter_velocity : 2D (3D) numpy array
        Velocity of the transmitting submarine.

    receiver_velocity : 2D (3D) numpy array
        Velocity of the receiving submarine.

    duration : float, optional
        Duration for which to run the emulation.
        The default is 0.001, which is 1ms of waves.

    n_points : int, optional
        Number of points to ping from one sub to another, equally spaced in
        the duration of emulation. The default is 1000.

    Returns
    -------
    2-tuple
       The first entry a 2-tuple (of numpy arrays) containing the input
       waveform pinged by the transmitter and a 2-tuple containing the
       waveform obtained by the receiver.

    Notes
    -----
    This function works by generating a set of times at which samples of the
    waveform are sent from the transmitter to the receiver.
    That is, we generate samples of a pure sine wave and the times
    corresponding to the samples.
    We then calculate 2 things: first, the times that each sample get to
    the second submarine; second, the amplitude of the sample as it gets
    to the second submarine (because it will decrease in amplitude). We
    work in the reference frame of the receiving submarine because then
    calculating the time the wave arrives is simply distance over velocity.
    The amplitude scales as 1/r so we simply use that.

    """
    # Generate a waveform.
    times, input_waveform = wave_gen(
        [(0.00025, 20000, 1, 0), (0.0005, 40000, 1, 0),
         (0.00025, 20000, 1, 0)],
        num_pts=n_points
    )

    # Velocity of the transmitter relative to the receiver.
    relative_velocity = transmitter_velocity - receiver_velocity

    # Initial position of the transmitter relative to the receiver.
    relative_pos_init = transmitter_pos_init - receiver_pos_init

    # Relative position of the transmitter every time it makes a ping.
    relative_positions = np.array([
        relative_pos_init + time * relative_velocity for time in times
    ])

    # Distance the wave travels for each sample.
    travel_distances = np.linalg.norm(relative_positions, axis=1)

    # The velocity of the ping obtained by the receiver in the 'rest' frame
    # of the medium (water in our case) is given by the speed of the wave
    # in the medium multiplied by the unit vector pointing from the transmitter
    # to the receiver.
    wave_velocities = np.array([
        -wave_speed * relative_position / np.linalg.norm(relative_position)
        for relative_position in relative_positions
    ])

    # The speed of the ping obtained in the receiver's rest frame.
    relative_wave_speeds = \
        np.linalg.norm(wave_velocities - receiver_velocity, axis=1)

    # The time at which each point is received is given by the distance
    # travelled divided by the wave speed relative to the receiver.
    received_times = times + travel_distances / relative_wave_speeds

    # Calculate the magnitude of the pings at the received sub.
    output_waveform = input_waveform / travel_distances

    return ((times, input_waveform), (received_times, output_waveform))


def main():
    """Run an emulation of waveform transmission from one sub to another."""
    # Frequencies are on the order of kilohertz so we will use those.
    freq = 30000

    # Set initial sub positions and velocities (can modify as necessary).
    transmitter_pos_init = np.array([0, 0])
    receiver_pos_init = np.array([SPEED_OF_SOUND/5, 0])
    transmitter_velocity = np.array([-10, 0])
    receiver_velocity = np.array([0, 0])

    # Emulate and get the input and output waveforms.
    in_, out = emulate(
        SPEED_OF_SOUND, freq, transmitter_pos_init, receiver_pos_init,
        transmitter_velocity, receiver_velocity
    )

    # Plot the waveforms.
    plt.figure()
    plt.plot(in_[0], in_[1], c='b', label="Input waveform")
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(out[0], out[1], c='r', label="Output waveform")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
