#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 22:17:14 2020

@author: Reuben

This file provides a set of encoders and decoders for some basic
error-correcting schemes.

"""

import numpy as np


def repetition_encoder(input_vector, num_repetitions):
    """
    Encode the given input using a basic repetition code.

    Parameters
    ----------
    input_vector : str
        A binary vector of 0s and 1s to be encoded.
    num_repetitions : int
        Number of times to repeat each input bit.

    Returns
    -------
    str
        Input vector with each bit repeated 'num_repetitions' times.

    """
    if num_repetitions >= len(input_vector):
        raise ValueError('Error: the number of repetitions cannot be greater'
                         ' than the length of the input.')
    for bit in input_vector:
        if bit not in ['0', '1', 'x']:
            raise ValueError("Bit values must be '0', '1', or 'x'.")

    return "".join([num_repetitions * bit for bit in input_vector])


def repetition_decoder(input_vector, num_repetitions):
    """
    Decode the give input assuming a basic repetition code.

    Parameters
    ----------
    input_vector : str
        A binary vector of 0s and 1s to be decoded. The value 'x' can also be
        included for any bits with unknown value.
    num_repetitions : int
        Number of times each bit is repeated in the encoding scheme.

    Returns
    -------
    str
        Decoded output vector. The output consists of 0s and 1s
        (and x's in the case that num_repetitions is even, and the value of a
        bit cannot be determined or if an unknown bit is passed in).

    """
    if num_repetitions >= len(input_vector):
        raise ValueError('The number of repetitions cannot be greater'
                         ' than the length of the input.')
    if len(input_vector) % num_repetitions != 0:
        raise ValueError('The length of the input is not an integer multiple'
                         ' of the number of repetitions.')

    output_vector = ''

    # Loop through each chunk of repeated bits.
    for i in range(0, len(input_vector), num_repetitions):
        bit_sum = 0

        # Sum the bits in the chunk.
        for j in range(num_repetitions):
            # If a bit has an unknown value (represented by 'x'), set
            # the average to 0.5 to signify an unknown chunk and exit loop.
            if input_vector[i+j] == 'x':
                bit_sum = 0.5 * num_repetitions     # Sets average to 0.5
                break
            # If the input is a 0 or a 1, add the value to the sum.
            elif input_vector[i+j] == '0' or input_vector[i+j] == '1':
                bit_sum += int(input_vector[i+j])
            # If the input value is an invalid character, raise an error.
            else:
                raise ValueError("Bit values must be '0', '1', or 'x'.")

        # Calculate the average bit value in the chunk.
        average = bit_sum / num_repetitions

        # Set the value of the chunk.
        output_vector += \
            '1' if average > 0.5 else ('0' if average < 0.5 else 'x')

    return output_vector
