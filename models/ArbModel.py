
import os.path, sys
import numpy as np
from models.ScopeModel import Scope
from models.tek_fileIO import *
from utilities.utilities import *
import visa, logging, os, struct, sys
from models.PyTektronixScope import TektronixScope
from PyQt5.QtCore import QThread, pyqtSignal
import time
from datetime import datetime

import queue 
from functools import partial
import json
from models.pv_model import pvModel


class ArbModel(Scope, pvModel):
    waveform_updated_signal = pyqtSignal(dict)
    channel_changed_signal = pyqtSignal()
    model_value_changed_signal = pyqtSignal(dict)

    def __init__(self, parent):
        
        pvModel.__init__(self, parent)
        
     
        self.wave_types = ['g_wavelet', 'windowed_sine']
        
        self.vars = ['center_f', 'sigma']

        self.tasks = {  'waveform_type': 
                                {'desc': 'Waveform type', 'val':self.wave_types[0], 'list':self.wave_types, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'waveform_type','type':'l'}},
                        'variable_parameter': 
                                {'desc': 'Variable', 'val':'center_f','list':self.vars,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'variable_parameter','type':'l'}},
                        'edit_state':     
                                {'desc': ';Edit', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'edit_state','type':'b'}}
                                
                      }       

        self.g_wavelet = 'g_wavelet'
        self.variable_parameter = 'center_f'

        self.create_pvs(self.tasks)

        self.start()


    
    #####################################################################
    #  Private set/get functions. Should not be used by external calls  #
    #####################################################################    

    def _exit_task(self):
        pass

    def _get_waveform_type(self):
        print('get ' + str(self.g_wavelet))
        return self.g_wavelet

    def _set_waveform_type(self, param):
        print('set ' + str(param))
        self.g_wavelet = param

    def _get_variable_parameter(self):
        print('get ' + str(self.variable_parameter))
        return self.variable_parameter

    def _set_variable_parameter(self, param):
        print('set ' + str(param))
        self.variable_parameter = param