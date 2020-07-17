#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 23:28:29 2020

@author: Reuben

This file provides a function to emulate data transmission by encoding a
bitsteam into a modulated waveform.

"""

from matplotlib import pyplot as plt

# Error correcting codes.
import ecc

# Waveform generation.
from wave_gen import wave_gen


def transmit(bitstream, bit_rate, *, encoding=None, encoding_arg=0,
             modulation_type, modulation_frequencies=(0, 0),
             relative_phase=180, frequency=0, amplitude=1, num_pts=1000):
    """
    Encode the given bitsteam into a modulated waveform.

    Parameters
    ----------
    bitstream : 1D array_like of '0's and '1's
        Series of bits (as single-character strings) representing the message
        to be encoded.

    bit_rate : float
        The number of bits conveyed per second in the output waveform.

    encoding : str, optional {'repetition', 'hamming'}
        The type of encoding to be used, if any. The options are 'repetition'
        for a repetition code and 'hamming' for a Hamming code. The parameters
        for these encodings are provided in encoding_arg, described below.
        The default is None.

    encoding_arg : int, optional
        The appropriate parameter for the chosen type of encoding, if
        applicable. For a (2**n - 1, 2**n - n -1) Hamming code, this parameter
        is n, and for a repetition code, this parameter is the number of
        repetitions. The default is 0.

    modulation_type : str, {'FM', 'PM'}
        The type of modulation to use to transmit the encoded signal.
        The available options are 'FM' for frequency modulation and
        'PM' for phase modulation.

    modulation_frequencies : 2-tuple of float, optional
        The frequencies for '0' and '1', respectively, when using frequency
        modulation. This argument is ignored if frequency modulation is not
        used. The default is (0, 0)
        (for when frequency modulation is not used).

    relative_phase : float, optional
        The relative phase between different bits when using phase modulation.
        This parameter is ignored if phase modulation is not used.
        The default is 180.

    frequency : float, optional
        The frequency for a phase-modulated waveform. This argument is ignored
        if phase modulation is not used. The default is 0
        (for when phase modulation is not used).

    amplitude : float, optional
        The amplitude of the output waveform. The default is 1.

    num_pts : int, optional
        The total number of points in the output waveform. The default is 1000.

    Returns
    -------
    2-tuple
        Representation of the output waveform. Each of the two entries is a
        1D numpy array, the first containing a list of time points and the
        second containing the corresponding magnitudes.

    Examples
    --------
    Function call to encode 'msg' with a 3-repetition encoding in a
    frequency-modulated waveform with a bit rate of 10000, a zero-frequency
    of 20000Hz, a one-frequency of 50000Hz, and the default amplitude and
    number of points:

    >>> transmit(
            msg, bit_rate=10000, encoding='repetition', encoding_arg=3,
            modulation_type='FM', modulation_frequencies=(20000, 50000)
        )

    Function call to encode 'msg' with an n=3 Hamming code in a phase-modulated
    waveform with a bit rate of 30000 relative phase shift of 180 degrees
    between '0' and '1', an amplitude of 5, and the default number of points:

    >>> transmit(
            msg, bit_rate=30000, encoding='hamming', encoding_arg=3,
            modulation_type='PM', relative_phase=180, amplitude=5
        )

    """
    # Encode the supplied message using the desired encoding scheme.
    if encoding == 'repetition':
        # The encoding_arg gives the number of repetitions.
        code = ecc.repetition_encoder(
            bitstream, num_repetitions=encoding_arg
        )
    elif encoding == 'hamming':
        # The encoding_arg gives n, corresponding to a
        # (2**n - 1, 2**n - n - 1) Hamming code.
        code = ecc.hamming_encoder(bitstream, n=encoding_arg)
    # If no encoding scheme is selected, use the message itself.
    elif encoding is None:
        code = bitstream
    else:
        raise ValueError("Invalid encoding scheme. Available options are"
                         " 'repetition', 'hamming', or None.")

    # Each bit corresponds to a wave segment in the final waveform. The
    # parameters of each such segment are stored  in this list and
    # subsequently used to generate the output waveform.
    wave_segments = []

    bit_duration = 1 / bit_rate

    # Convert the encoded message bit by bit into  wave
    # segments, which together are passed into wave_gen to create the final
    # waveform.

    # Perform frequency modulation (if selected).
    if modulation_type == 'FM':
        # The frequencies corresponding to '0' and '1' are given by the first
        # two entries of modulation_frequencies, respectively.
        freq_0 = modulation_frequencies[0]
        freq_1 = modulation_frequencies[1]

        # For each bit, construct a new wave segment of the specified duration
        # appropriate frequency, specified amplitude, and zero phase shift,
        # (with the arguments in that order).
        for bit in code:
            wave_segments.append(
                (bit_duration, freq_0 if bit == '0' else freq_1, amplitude, 0)
            )
    # Perform phase modulation (if selected).
    elif modulation_type == 'PM':
        # For each bit, construct a new wave segment of the specified duration,
        # frequency, amplitude, and the correct relative phase
        # (with the arguments in that order).
        prev_bit = code[0]
        for bit in code:
            wave_segments.append(
                (bit_duration, frequency, amplitude,
                 relative_phase if bit != prev_bit else 0)
            )
            prev_bit = bit
    else:
        raise ValueError("Invalid modulation type. Available options are"
                         " 'FM' and 'PM'.")

    # Generate the waveform from the compiled wave segments.
    return wave_gen(wave_segments, num_pts=num_pts)


# Code testing region.
if __name__ == '__main__':
    message = '11010100'

    # Parameter for repetition encoding
    num_repetitions = 3
    # Parameter for Hamming encoding
    n = 3
    # Parameters for frequency modulation
    freq_0 = 20000
    freq_1 = 50000
    FM_bit_rate = 5000
    # Parameter for phase modulation
    PM_bit_rate = 1000

    # Encode the message with an 3-repetition code in a phase-modulated
    # waveform with a bit rate of PM_bit_rate, a frequency of 10 * PM_bit_rate,
    # a relative phase of 180 degrees between '0' and '1', and the default
    # amplitude and number of points.
    times, waveform = transmit(
        message, bit_rate=PM_bit_rate, frequency=10*PM_bit_rate,
        encoding='repetition', encoding_arg=num_repetitions,
        modulation_type='PM', relative_phase=180
    )

    plt.figure(figsize=(len(message) * num_repetitions, 5))
    plt.plot(times, waveform)
    plt.show()

    # Encode the message with an n=3 Hamming code in a frequency-modulated
    # waveform with a bit rate of FM_bit_rate, a zero-frequency
    # of freq_0, a one-frequency of freq_1, and the default amplitude and
    # number of points.
    times, waveform = transmit(
            message, bit_rate=FM_bit_rate, encoding='hamming', encoding_arg=n,
            modulation_type='FM', modulation_frequencies=(freq_0, freq_1)
    )
    plt.figure(figsize=(len(message) * min(freq_0, freq_1) / FM_bit_rate, 5))
    plt.plot(times, waveform)
    plt.show()
