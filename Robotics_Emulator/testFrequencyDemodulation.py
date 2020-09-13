
#Imports 
import math
import numpy as np
import matplotlib.pyplot as plt

#Constants
SPEED_SOUND = 1480 # m / s 
HYDRO_SPACING = 0.1 # m 

def decodeFrequencyModulation(time, voltage, freq):
    """

    Parameters
    ----------
    time : 1-D Numpy array 
        List of the times which correspond to the measured voltages with the
        waveform. 
    voltage : 1-D Numpy array
        List of the voltages of the waveform which correspond to the given times.
    freq  :  1-D Numpy array
        List of possible frequencies which could correspond to the given data

    Returns
    -------
    givenFrequency : float
        Returns the frequency from freq[] which aligns most with the given 
        time interval. 

    """
    #Definition of Omega 
    omega = 2 * np.pi * freq     #Numpy array of all omega values 
    
    #Trim the Signal Times, constrict to first millisecond
    time = time[time < time[0] + 0.001]
    
    #Check that signal exists
    if (time.size < 1):
        return 0
    
    #Trim the voltage given the constricted time 
    voltage = np.resize(voltage, time.size)
    
    #Define Amplitudes
    amplitude = np.zeros(omega.size)
    
    #find kI and kQ values for different frequencies 
    for i in range(omega.size):
        kI = np.sum(voltage * np.cos(omega[i] * time))
        kQ = np.sum(voltage * np.sin(omega[i] * time))
        #Find the Amplitude of the wave (Voltage value) at the given frequency
        amplitude[i] = kI**2 + kQ**2 
        
    #Compare the amplitudes - the highest amplitude corresponds with the frequency we want
    maxAmplitude, givenFrequency = amplitude[0], freq[0]
    
    for i in range(amplitude.size):
        if amplitude[i] > maxAmplitude:
            maxAmplitude = amplitude[i]
            givenFrequency = freq[i]   
            
    return givenFrequency

#if __name__ == "__main__": 
    #Insert 
    