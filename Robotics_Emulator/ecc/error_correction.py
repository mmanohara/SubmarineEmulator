#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 22:17:14 2020

@author: Reuben

This file provides a set of encoders and decoders for some basic
error-correcting schemes (basically a bunch of horrific type conversions
with some computations thrown in).

For a useful crash course on basic code, see here:
https://www.youtube.com/playlist?list=PLJHszsWbB6hqkOyFCQOAlQtfzC1G9sf2_

"""

import numpy as np

import ecc.error_correction_utils as utils


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
    if num_repetitions > len(message):
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
    if num_repetitions > len(code):
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
        # Compute the next codeword by multiplying the data chunk
        # by the generator matrix.
        codeword = utils.multiply_binary_finite_field_matrices(
             np.array([list(message[i:i+num_data_bits])]).astype(np.intc),
             generator_matrix
        )
        # Convert codeword from a column vector to a string and append.
        code += ''.join([str(bit) for bit in np.nditer(codeword)])

    return code


def hamming_decoder(code, n=3):
    """
    Decode the given message, assuming a (2**n - 1, 2**n - n - 1) Hamming code.

    Note that a Hamming code can only detect a single error in each codeword.
    If two bits are flipped in a given codeword, it will appear as though a
    single error has occured at a different location, and the mistake will be
    repaired incorrectly.

    See https://en.wikipedia.org/wiki/Hamming_code for more info.

    Parameters
    ----------
    code : str
        A binary vector of 0s and 1s to be decoded.
    n : int, optional
        The number n corresponding to a (2**n - 1, 2**n - n - 1) Hamming code
        (with 2**n - 1 bits per codeword, n parity bits per codeword, and thus
        2**n - n - 1 data bits per codeword). The default is 3.

    Returns
    -------
    message : str
        A binary vector of 0s and 1s representing the decoded message.

    """
    # The number of data bits and parity bits in each codeword.
    codeword_bits = 2**n - 1

    # The number of data bits per codeword.
    num_data_bits = codeword_bits - n

    if len(code) % codeword_bits != 0:
        raise ValueError('Input length is not divisible by the number of'
                         ' bits per codeword.')

    message = ''

    # Compute the parity check matrix for the assumed encoding.
    parity_check_matrix = utils.hamming_parity_check_matrix(n)

    # Loop through each codeword by index.
    for i in range(0, len(code), codeword_bits):
        # Convert codeword from a string to a column vector of integer bits.
        # I hope there is a better way to do this, because this is gross.
        codeword = np.array([[int(bit) for bit in code[i:i+codeword_bits]]]).T

        # Compute the product of the parity check matrix and the codeword,
        # called the syndome vector, to determine which error occurred, if any.
        syndrome_vector = utils.multiply_binary_finite_field_matrices(
            parity_check_matrix, codeword
        )

        # The new message bits before correction of any errors. The last n
        # bits in the codeword are parity bits, which are ignored.
        data = code[i:i+num_data_bits]

        # If the syndrome vector is nonzero, there is an error.
        if np.any(syndrome_vector):
            # The error is located at the index of the column of the parity
            # check matrix equal to the syndrome vector.
            error_location = int(np.where(
                np.all(parity_check_matrix == syndrome_vector, axis=0)
            )[0])
            # Convert the data bits of the codeword to a integer to make
            # correcting the error easier.
            data_val = int(sum(
                [bit * 2**j for j, bit in enumerate(reversed(
                    codeword[:num_data_bits]))]
            ))

            # If the error is in one of the data bits, correct it. Otherwise,
            # the output is unaffected.
            if error_location < num_data_bits:
                # Flip the erroneous bit (using xor at the appropriate
                # location).
                corrected = str(bin(data_val ^ int(2**(n-error_location)))[2:])

                # Finally, set the final value of the data by extending
                # corrected to the appropriate length.
                data = '0' * (num_data_bits - len(corrected)) + corrected

        # Add the corrected (if applicable) new message bits to the message.
        message += data

    return message


# Code testing region.
if __name__ == '__main__':
    num_tests = 10000

    # Test Hamming (7,4) encoder/decoder.
    for test in range(num_tests):
        message = ''

        # Generate a random 40-bit message, which will yield 10 codewords for
        # a Hamming (7,4) code.
        for bit in range(40):
            message += np.random.choice(['0', '1'])

        # Encode the message.
        code = hamming_encoder(message)

        code_distorted = ''

        # Create a distorted code by randomly flipping one bit in each word.
        for i in range(0, len(code), 7):
            index = np.random.randint(0, 6)
            code_distorted += (
                code[i:i+index]
                + ('0' if code[i+index] == '1' else '1')
                + code[i+index+1:i+7]
            )

        # Decode the code and the distorted code and check that both yield the
        # original message.
        assert hamming_decoder(code) == message \
            and hamming_decoder(code_distorted) == message, \
            'WRONG. YOUR CODE IS WRONG. SAD.'
