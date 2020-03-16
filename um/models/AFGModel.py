
import os.path, sys
import numpy as np


class Afg():
    ''' 
    General class for function generators, defice-speficic function
    generator classes should inherit from this class.
    '''
    def __init__(self):
        self.instrument = ''
        self.channel = 1
        self.amplitude = 1      # V
        self.offset = 0
        self.frequency = 30e6   # Hz
        self.state = False      # Off = False; On = True
        self.waveform = None    # arbitrary waveform numpy array
        self.mode = 2           # 0 = continuous; 1 = n-burst; 2 = single; 
        self.connected = False
        
    

    def read_file(self, filename=''):
        pass
        
    def set_waveform(self, waveform):
        self.waveform = waveform

    def set_frequency(self, freq):
        self.freq = freq

    def set_amplitude(self, amplitude):
        self.voltage = amplitude

    def set_output_state(self, state):
        self.state = state

    def get_frequency(self):
        return self.freq

    def get_amplitude(self):
        return self.voltage

    def get_output_state(self):
        return self.state
