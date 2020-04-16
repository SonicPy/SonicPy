
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

        self.extensions = 'Text (*.csv);;Binary (*.npz)'.split(';;')

        self.tasks = {  'data_channel':
                                {'desc': '', 'val':'', 
                                'param':{'type':'s'}},
                        'filename':
                                {'desc': 'Filename', 'val':'savedata.csv', 
                                'param':{'type':'s'}},
                        'file_filter':
                                {'desc': 'Filename', 'val':'Text (*.csv);;Binary (*.npz)', 
                                'param':{'type':'s'}},
                        'file_extension':
                                {'desc': 'Extension', 'val':self.extensions[0],'list':self.extensions, 
                                'param':{'type':'l'}},
                        'file_header':
                                {'desc': 'Header', 'val':{}, 
                                'param':{'type':'dict'}}, 
                        'save':     
                                {'desc': 'Save;Save', 'val':False, 
                                'param':{'type':'b'}}, 
                        'autorestart':     
                                {'desc': 'autorestart;ON/OFF', 'val':False, 
                                'param':{'type':'b'}}, 
                        'autosave':     
                                {'desc': 'Sutosave;ON/OFF', 'val':False, 
                                'param':{'type':'b'}}, 
                        'warn_overwrite':     
                                {'desc': 'Warn overwrite;ON/OFF', 'val':False, 
                                'param':{'type':'b'}},
                        'params':
                                {'desc': 'Environment parameters', 'val':{}, 
                                'param':{'type':'dict'}}

                      }       

        self.create_pvs(self.tasks)

        self.pvs['data_channel'].set('DPO5104:waveform')

    
    #####################################################################
    #  Private set/get functions. Should not be used by external calls  #
    #####################################################################    

    def write_file(self, filename, params = {}):
        data = self.pv_server.get_pv(self.pvs['data_channel']._val)._val
        #print(data)
        
        if len(data):
            waveform  = data['waveform']
            
            if filename.endswith('.csv'):
                
                
                write_tek_csv(filename, waveform[0], waveform[1])
            if filename.endswith('.npz'):
                
                np.savez_compressed(filename, waveform)
            
            self.pvs['filename'].set(filename)

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
            file_name = self.pvs['filename']._val
            if len(file_name):
                self.write_file(file_name)
            self.pvs['save'].set(False)

    
    def _set_file_extension(self, extension):
        if 'csv' in extension:
            self.pvs['file_filter'].set('Text (*.csv);;Binary (*.npz)')
            #print(self.file_filter)
        if 'npz' in extension:
            self.pvs['file_filter'].set('Binary (*.npz);;Text (*.csv)')
            #print(self.file_filter)


