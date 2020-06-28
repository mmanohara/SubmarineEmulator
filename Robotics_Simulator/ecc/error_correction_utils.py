#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 16:26:59 2020

@author: Reuben

This file provides a set of utility function for the error correction file.

"""

import numpy as np


def hamming_generator_matrix(n):
    """
    Return a 2D numpy array containing a Hamming code generator matrix.

    The matrix given for a systematic (2**n - 1, 2**n - n - 1) Hamming code
    (systematic means all the parity bits are at the end of each codeword).
    Such a code has 2**n - 1 bits per codeword, n parity bits per codeword,
    and thus 2**n - n - 1 data bits per codeword.

    Any 2**n - n - 1 bit message x can be encoded by encoded by evaluating the
    matrix product xG, where G is the generator matrix.

    See https://en.wikipedia.org/wiki/Hamming_code for more info.

    Note that systematic parity check matrices are not unique for a given n,
    so this result is only guaranteed to work with its accompanying parity
    check matrix function in this file.

    Parameters
    ----------
    n : int
        The number n corresponding to a (2**n - 1, 2**n - n - 1) Hamming code
        (with 2**n - 1 bits per codeword, n parity bits per codeword, and thus
        2**n - n - 1 data bits per codeword).

    Returns
    -------
    2D numpy array of int
        A systematic Hamming code generator matrix with 2**n - n - 1 rows and
        2**n - 1 columns (systematic meaning the first n columns are the
        identity matrix).

    """
    # The generator matrix is constructed by appendig the transpose of the
    # first 2**n - n - 1 columns of the parity check matrix to the
    # 2**n - n - 1 identity matrix.
    return np.concatenate((
        np.identity(2**n - n - 1),
        (hamming_parity_check_matrix(n)[:, :2**n-n-1]).T
        ), axis=1
    ).astype(int)


def hamming_parity_check_matrix(n):
    """
    Return a 2D numpy array containing a Hamming code parity check matrix.

    The matrix given is for a systematic (2**n - 1, 2**n - n - 1) Hamming code
    (systematic means all the parity bits are at the end of each codeword).
    Such a code has 2**n - 1 bits per codeword, n parity bits per codeword,
    and thus 2**n - n - 1 data bits per codeword.
    See https://en.wikipedia.org/wiki/Hamming_code for more info.

    Note that systematic parity check matrices are not unique for a given n,
    so this result is only guaranteed to work with its accompanying generator
    matrix function in this file.

    Parameters
    ----------
    n : int
        The number n corresponding to a (2**n - 1, 2**n - n - 1) Hamming code
        (with 2**n - 1 bits per codeword, n parity bits per codeword, and thus
        2**n - n - 1 data bits per codeword).

    Returns
    -------
    parity_check_matrix : 2D numpy array of int
        A systematic Hamming code parity check matrix with n rows and 2**n - 1
        columns (systematic meaning the first n columns are the identity
        matrix).

    """
    # Initialize the parity check matrix as the nxn identity.
    parity_check_matrix = np.identity(n)

    # Append every nonzero n-bit vector to the matrix, excluding those
    # already contained in the identity. This is equivalent to appending
    # every binary number from 1 to 2**n - 1, excluding powers of 2.
    num = 3     # The first nonzero vector that is not a power of 2.
    while np.ceil(np.log2(num)) <= n:
        # Make sure num is not a power of two. If it is, it is skipped.
        if (num & (num - 1) != 0):
            # Convert num to binary form.
            binary = bin(num)[2:]

            # Extend the binary num to match the necessary column length.
            bin_col = np.array([list('0' * (n - len(binary)) + binary)]).T

            # Append column to the parity check matrix.
            parity_check_matrix = np.concatenate(
                (bin_col, parity_check_matrix), axis=1
            )

        num += 1

    # Convert matrix elements from type str to int.
    # This might be a very stupid way to do this. I don't know.
    return parity_check_matrix.astype(float).astype(int)
