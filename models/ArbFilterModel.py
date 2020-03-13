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


class ArbFilterModel(Scope, pvModel):
    waveform_updated_signal = pyqtSignal(dict)
    channel_changed_signal = pyqtSignal()
    model_value_changed_signal = pyqtSignal(dict)

    def __init__(self, parent, definitions):
        
        pvModel.__init__(self, parent)
        
        self.filter_types = [ definitions[x].param['name'] for x in definitions]
        

        self.tasks = {  'filter_type': 
                                {'desc': 'Filter type', 'val':self.filter_types[0], 'list':self.filter_types, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'filter_type','type':'l'}},
                        
                        'edit_state':     
                                {'desc': ';Edit', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'edit_state','type':'b'}}
                                
                      }       

        
        self.create_pvs(self.tasks)

        self.start()


    
    #####################################################################
    #  Private set/get functions. Should not be used by external calls  #
    #####################################################################    

    def _exit_task(self):
        pass

    def _get_filter_type(self):
        ans = self.pvs['filter_type']._val
        #print('get ' + str(ans))
        return ans

    def _set_filter_type(self, param):
        #print('set ' + str(param))
        self.pvs['filter_type']._val= param

    def _get_variable_parameter(self):
        ans = self.pvs['variable_parameter']._val
        #print('get ' + str(ans))
        return ans

    def _set_variable_parameter(self, param):
        #print('set ' + str(param))
        self.pvs['variable_parameter']._val= param

    def _get_edit_state(self):
        ans = self.pvs['edit_state']._val
        #print('get ' + str(ans))
        return ans

    def _set_edit_state(self, param):
        #print('set ' + str(param))
        self.pvs['edit_state']._val= param