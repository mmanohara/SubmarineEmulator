#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 22:17:14 2020

@author: Reuben

This file provides a set of encoders and decoders for some basic
error-correcting schemes.

"""

import numpy as np

import error_correction_utils as utils


def repetition_encoder(message, num_repetitions):
    """
    Encode the given input using a basic repetition code.

    Parameters
    ----------
    message : str
        A binary vector of 0s and 1s to be encoded.
    num_repetitions : int
        Number of times to repeat each input bit.

    Returns
    -------
    str
        Input vector with each bit repeated 'num_repetitions' times.

    """
    if num_repetitions >= len(message):
        raise ValueError('Error: the number of repetitions cannot be greater'
                         ' than the length of the input.')
    for bit in message:
        if bit not in ['0', '1', 'x']:
            raise ValueError("Bit values must be '0', '1', or 'x'.")

    return "".join([num_repetitions * bit for bit in message])


def repetition_decoder(code, num_repetitions):
    """
    Decode the given input assuming a basic repetition code.

    Parameters
    ----------
    code : str
        A binary vector of 0s and 1s to be decoded. The value 'x' can also be
        included for any bits with unknown value.
    num_repetitions : int
        Number of times each bit is repeated in the encoding scheme.

    Returns
    -------
    message : str
        Decoded output vector. The output consists of 0s and 1s
        (and x's in the case that num_repetitions is even, and the value of a
        bit cannot be determined or if an unknown bit ('x') is passed in).

    """
    if num_repetitions >= len(code):
        raise ValueError('The number of repetitions cannot be greater'
                         ' than the length of the input.')
    if len(code) % num_repetitions != 0:
        raise ValueError('The length of the input is not an integer multiple'
                         ' of the number of repetitions.')

    message = ''

    # Loop through each chunk of repeated bits (codeword).
    for i in range(0, len(code), num_repetitions):
        bit_sum = 0

        # Sum the bits in the chunk.
        for j in range(num_repetitions):
            # If a bit has an unknown value (represented by 'x'), set
            # the average to 0.5 to signify an unknown chunk and exit loop.
            if code[i+j] == 'x':
                bit_sum = 0.5 * num_repetitions     # Sets average to 0.5
                break
            # If the input is a 0 or a 1, add the value to the sum.
            elif code[i+j] == '0' or code[i+j] == '1':
                bit_sum += int(code[i+j])
            # If the input value is an invalid character, raise an error.
            else:
                raise ValueError("Bit values must be '0', '1', or 'x'.")

        # Calculate the average bit value in the chunk.
        average = bit_sum / num_repetitions

        # Set the value of the chunk.
        message += \
            '1' if average > 0.5 else ('0' if average < 0.5 else 'x')

    return message


def hamming_encoder(message, n=3):
    """
    Encode the given message using a (2**n - 1, 2**n - n - 1) Hamming code.

    See https://en.wikipedia.org/wiki/Hamming_code for more info.

    Parameters
    ----------
    message : str
        A binary vector of 0s and 1s to be encoded.
    n : int, optional
        The number n corresponding to a (2**n - 1, 2**n - n - 1) Hamming code
        (with 2**n - 1 bits per codeword, n parity bits per codeword, and thus
        2**n - n - 1 data bits per codeword). The default is 3.

    Returns
    -------
    code : str
        A binary vector of 0s and 1s representing the encoded message.

    """
    # Number of bits containing information from the message per codeword
    # (the other bits are parity bits used for error-detection/correction).
    num_data_bits = 2**n - n - 1

    if len(message) % num_data_bits != 0:
        raise ValueError('Input length is not divisible by the number of data'
                         ' bits per codeword.')

    code = ''
    generator_matrix = utils.hamming_generator_matrix(n)

    # Loop through each chunk of data bits by index.
    for i in range(0, len(message), num_data_bits):
        # Append the next codeword, computed by multiplying the data chunk
        # by the generator matrix.
        codeword = utils.multiply_binary_finite_field_matrices(
             np.array([list(message[i:i+num_data_bits])]).astype(np.intc),
             generator_matrix
        )
        code += ''.join([str(bit) for bit in np.nditer(codeword)])

    return code
