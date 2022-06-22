
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
        
        self.echoes = {}

    def add_echoes(self, correlation):
        


        self.echoes[correlation['filename_waweform']] = correlation

    def clear(self):
        self.__init__()

    

 
 
    def save_result(self, filename='test_output.json'):
        
        data = self.echoes
        
        if filename.endswith('.json'):
            with open(filename, 'w') as json_file:
                json.dump(data, json_file,indent = 2)    

