
#Imports 
import math
import numpy as np
import matplotlib.pyplot as plt
import wave_gen as wg

#Constants
SPEED_SOUND = 1480 # m / s 
HYDRO_SPACING = 0.1 # m 

def decodeFrequencyModulation(time, voltage, freq, delT):
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
    bitPeriod : 

    Returns
    -------
    givenFrequency : float
        Returns the frequency from freq[] which aligns most with the given 
        time interval. 

    """
    currentTime = delT / 2
    delTPrime = delT / 4
    bit = 0 
    
    time = time - time[0]
    
    index = time[time < currentTime - delTPrime].size
    
    #Definition of Omega 
    omega = 2 * np.pi * freq     #Numpy array of all omega values 
    
    frequencyList = []
    
    while time[time > currentTime + delTPrime].size > 0:
        measureTime = time[time >= currentTime - delTPrime]
        
        measureTime = measureTime[measureTime < currentTime - delTPrime + delT]
        
        indexJump = measureTime.size
        
        measureTime = measureTime[measureTime < currentTime + delTPrime]
        
        measureVoltage = np.take(voltage, range(index, index + measureTime.size))
        
        
        amplitude = np.zeros(omega.size)

        for i in range(omega.size):
            kI = np.sum(measureVoltage * np.cos(omega[i] * measureTime))
            kQ = np.sum(measureVoltage * np.sin(omega[i] * measureTime))
            
            amplitude[i] = kI**2 + kQ**2
        
        
        frequencyList.append(freq[np.argmax(amplitude)])
        
        currentTime += delT
        index += indexJump
        bit += 1
    
    return frequencyList

if __name__ == "__main__": 
    waves = []
    
    # works on 90, 180, 270 - [.5, 1, 1.5, 0]
    waves.append([(0.001, 25000, 1, 0), (0.001, 25000, 1, 90),
            (0.001, 20000, 1, 180), (0.001, 20000, 1, 270),
            (0.001, 30000, 1, 0)])

    # works with arbitrary lengths of 0s - [0, 0, 0, 0, 0, 0, 0]
    waves.append([(0.004, 20000, 1, 0), (0.003, 20000, 1, 0), 
                  (0.001, 20000, 1, 0)])
    
    # works with phase shifts then holds - [.05, 0, 0 ,1]
    waves.append([(0.001, 25000, 1, 0), (0.003, 35000, 1, 90), 
                  (0.001, 30000, 1, 180)])
    
    # pushes to nearest phase- [.5, .5, 1, 1, 1.5]
    waves.append([(0.001, 24988, 1, 0), (0.001, 30021, 1, 95), 
                  (0.001, 20030, 1, 85), (0.001, 35041, 1, 190), 
                  (0.001, 34950, 1, 173), (0.001, 19949, 1, 274)])
    
    for wave in waves:
        times, waveform = wg.wave_gen(wave)
        #print(fourier_phase_shift_checker(times, waveform, .001, 20000))
        print(decodeFrequencyModulation(times, waveform, np.array([20000, 25000, 30000, 35000]), 0.001))
    
    """# works on an amplitude that is not 1, as long as amp is constant
    # it could work even if amp isnt constant, but mostly due to the error 
    # margins I allow and I wouldn't push it
    # [.5, 1, 1.5]
    wave = ([(0.001, 20000, 2, 0), (0.001, 20000, 2, 90),
            (0.001, 20000, 2, 180), (0.001, 20000, 2, 270)])
    times, waveform = wg.wave_gen(wave)
    print(phase_shift_checker(times, waveform, .001, 20000, amp = 2))"""
    