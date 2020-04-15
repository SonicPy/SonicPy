
import os.path, sys
import numpy as np
from um.models.ScopeModel import Scope
from um.models.tek_fileIO import *
from utilities.utilities import *
import visa, logging, os, struct, sys
from um.models.PyTektronixScope import TektronixScope
from PyQt5.QtCore import QThread, pyqtSignal
import time
from datetime import datetime

import queue 
from functools import partial
import json
from um.models.pv_model import pvModel
from um.models.pvServer import pvServer


class SaveDataModel(pvModel):
    

    def __init__(self, parent, offline = False):
        super().__init__(parent)
        self.parent= parent
        
        self.pv_server = pvServer()
        
        self.instrument = 'SaveData'
    
        self.file_name = ''
        self.file_settings = None
  
        self.file_filter='Text (*.csv);;Binary (*.npz)'


        self.tasks = {  
                        'filename':
                                {'desc': 'Filename', 'val':'', 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'filename','type':'s'}},
                        'file_extension':
                                {'desc': 'Extension', 'val':self.file_filter.split(';;')[0],'list':self.file_filter.split(';;'), 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'file_extension','type':'l'}},
                        'file_header':
                                {'desc': 'Header', 'val':{}, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'file_header','type':'dict'}}, 
                        'save':     
                                {'desc': 'Save;Save', 'val':False, 
                                'methods':{'set':True, 'get':False}, 
                                'param':{'tag':'save','type':'b'}}
                                
                      }       

        self.create_pvs(self.tasks)

        self.start()


    def write_file(self, filename, params = {}):
        data = self.waveform
        if data is not None:
            waveform  = data['waveform']
            
            if filename.endswith('.csv'):
                self.file_filter='Text (*.csv);;Binary (*.npz)'
                write_tek_csv(filename, waveform[0], waveform[1])
            if filename.endswith('.npz'):
                self.file_filter='Binary (*.npz);;Text (*.csv)'
                np.savez_compressed(filename, waveform)
            
            self.file_name = filename
        
    
    #####################################################################
    #  Private set/get functions. Should not be used by external calls  #
    #####################################################################    

    def _exit_task(self):
        pass

    def _set_filename(self, filename):

        self.file_name = filename
        if filename.endswith('.csv'):
            self.pvs['file_extension'].set('Text (*.csv)')
            
        if filename.endswith('.npz'):
            self.pvs['file_extension'].set('Binary (*.npz)')

    
    def _set_save(self, state):
        if state:
            self.write_file(self.file_name, self.params)

    def _get_filename(self):
        return self.file_name

    def _get_file_extension(self):
        return self.file_filter
    
    def _set_file_extension(self, extension):
        if 'csv' in extension:
            self.file_filter = 'Text (*.csv);;Binary (*.npz)'
            #print(self.file_filter)
        if 'npz' in extension:
            self.file_filter = 'Binary (*.npz);;Text (*.csv)'
            #print(self.file_filter)


