
from argparse import FileType
import enum
import os.path, sys
from utilities.utilities import *
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import numpy as np
from numpy import argmax, c_, nan, greater,less, append, sort, array, argmin

from scipy import optimize
from scipy.signal import argrelextrema, tukey
from functools import partial
from um.models.tek_fileIO import *
from scipy import signal
import pyqtgraph as pg
from utilities.utilities import zero_phase_bandpass_filter,  \
                                 zero_phase_highpass_filter, \
                                zero_phase_bandstop_filter, zero_phase_lowpass_filter

from ua.models.WaterfallModel import WaterfallModel
import json
import glob
import time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject
from natsort import natsorted 
 



class EchoesResultsModel():
    def __init__(self):
        
        self.echoes_p = {}
        self.echoes_s = {}

    def add_echoe(self, correlation):
        
        wave_type = correlation['wave_type']
        if wave_type == "P":

            self.echoes_p[correlation['filename_waweform']] = correlation
        elif wave_type == "S":

            self.echoes_s[correlation['filename_waweform']] = correlation

    def clear(self):
        self.__init__()

    
    def get_echoes(self):
        return self.echoes_p, self.echoes_s
 
 
    def save_result(self, filename='test_output.json'):
        
        data = {'P':self.echoes_p, 'S':self.echoes_s}
        
        if filename.endswith('.json'):
            with open(filename, 'w') as json_file:
                json.dump(data, json_file,indent = 2)    

    def load_result_from_file(self, filename= 'test_output.json'):
        if filename.endswith('.json'):
            with open(filename, 'r') as json_file:
                correlations = json.load(json_file)   
                self.clear()
                echoes_p = correlations['P']
                echoes_s = correlations['S']
                
                for fname in echoes_p:
                    
                    echo = echoes_p[fname]
                    self.add_echoe(echo)
                for fname in echoes_s:
                    
                    echo = echoes_s[fname]
                    self.add_echoe(echo)
        