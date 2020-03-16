
import os.path, sys
import numpy as np
from utilities.utilities import *

class Scope():
    def __init__(self):
        
        self.instrument = ''
        self.channel = 1
        self.scale = 100
        self.resolution = 100e-12       # second / sample
        self.accumulations = 1000   
        self.go = False                # stop = False; run = True
        self.waveform = None
        self.mode = 1                   # 0 = single; 1 = n-accumulate; 2 = inf-accumulate
    
        self.ind = 0
        
    def get_waveform(self): 
        return self.waveform
        
    

    def read_file(self, filename=''):
        pass