import os.path, sys
import numpy as np
from um.models.ScopeModel import Scope
from um.models.tek_fileIO import *
from utilities.utilities import *
import  logging, os, struct, sys
from um.models.PyTektronixScope import TektronixScope
from PyQt5.QtCore import QThread, pyqtSignal
import time
from datetime import datetime

import queue 
from functools import partial
import json
from um.models.pv_model import pvModel


class ArbFilterModel(Scope, pvModel):
    waveform_updated_signal = pyqtSignal(dict)
    channel_changed_signal = pyqtSignal()
    model_value_changed_signal = pyqtSignal(dict)

    def __init__(self, parent):
        
        pvModel.__init__(self, parent)
      
        

        self.tasks = {  
                        
                        'edit_state':     
                                {'desc': ';Edit', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'edit_state','type':'b'}},
                        'filtered_waveform':     
                                {'desc': 'Waveform', 'val':None, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'waveform','type':'dict'}},
                        'filter_params':     
                                {'desc': 'Waveform parameters', 'val':None, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'waveform','type':'dict'}}
                                
                      }       

        
        self.create_pvs(self.tasks)

        self.start()


    
    #####################################################################
    #  Private set/get functions. Should not be used by external calls  #
    #####################################################################    

    def _exit_task(self):
        pass

    '''    def _get_filter_type(self):
        ans = self.pvs['filter_type']._val
        #print('get ' + str(ans))
        return ans

    def _set_filter_type(self, param):
        #print('set ' + str(param))
        self.pvs['filter_type']._val= param'''


    def _get_edit_state(self):
        ans = self.pvs['edit_state']._val
        #print('get ' + str(ans))
        return ans

    def _set_edit_state(self, param):
        #print('set ' + str(param))
        self.pvs['edit_state']._val= param