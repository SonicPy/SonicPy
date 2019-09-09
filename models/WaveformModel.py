
import os.path, sys
from utilities.utilities import *
import numpy as np

class Waveform():
    def __init__(self,x,y):
        self.waveform = (x,y)
        self.envelope = None
    
    def get_xy(self):
        return self.waveform

    def set_waveform(self, x, y):
        self.waveform = (x,y)

    def set_envelope(self, envelope):
        self.envelope = envelope

    def get_envelope(self):
        return self.envelope
        
    def get_x(self):
        if self.waveform is not None:
            return self.waveform[0]
        else:
            return None

    def get_y(self):
        if self.waveform is not None:
            return self.waveform[1]
        else:
            return None


        
    