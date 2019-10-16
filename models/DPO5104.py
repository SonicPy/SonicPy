
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


class Scope_DPO5104(Scope, pvModel):
    waveform_updated_signal = pyqtSignal(dict)
    channel_changed_signal = pyqtSignal()
    model_value_changed_signal = pyqtSignal(dict)

    def __init__(self, parent, visa_hostname='143'):
        
        pvModel.__init__(self, parent)
        Scope.__init__(self)
        
        ## device speficic:
        
        self.instrument = 'DPO5104'
        self.settings_file_tag ='Scope'

        self.visa_hostname = visa_hostname
        self.connected = False
        
        #self.connected = self.connect(self.visa_hostname)
        
        self.file_name = ''
        self.file_settings = None
        self.data_stop = 100000
        self.selected_channel = 'CH1'
        self.waveform = None
        self.bg_waveform = None
        self.file_filter='Text (*.csv);;Binary (*.npz)'

        self.acquisition_types = ['sample', 'peak', 'hires', 'envelope', 'average']
        self.channels = ['CH1','CH2','CH3','CH4']
     

        self.tasks = {  'acquisition_type': 
                                {'desc': 'Acqusition type', 'val':self.acquisition_types[0], 'list':self.acquisition_types, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'aquisition_type','type':'l'}},
                        'num_av': 
                                {'desc': 'N-average', 'val':1000, 'min':2,'max':10000,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'num_av','type':'i'}},
                        'num_acq': 
                                {'desc': 'N-acquired', 'val':1, 'min':1,'max':1e30-1,
                                'methods':{'set':False, 'get':True},  
                                'param':{'tag':'num_acq','type':'i'}},
                        'channel': 
                                {'desc': 'Data source', 'val':self.channels[0],'list':self.channels,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'channel','type':'l'}},      
                        'channel_state': 
                                {'desc': 'Channel state;ON/OFF', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'channel_state','type':'b'}},
                        'run_state':     
                                {'desc': 'Run state;ON/OFF', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'output_state','type':'b'}},
                        'erase':     
                                {'desc': 'Erase;Erase', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'output_state','type':'b'}},
                        'vertical_scale':  
                                {'desc': 'Vertical scale', 'val':1.0,'increment':0.05, 'min':1e-9,'max':10,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'vertical_scale','type':'f'}},
                        'instrument':
                                {'desc': 'Instrument', 'val':self.instrument, 
                                'methods':{'set':False, 'get':True}, 
                                'param':{'tag':'instrument','type':'s'}},
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
                                'param':{'tag':'save','type':'b'}},       
                        'waveform':
                                {'desc': 'Waveform', 'val':{}, 
                                'methods':{'set':False, 'get':True}, 
                                'param':{'tag':'waveform','type':'dict'}},
                        'bg_waveform':
                                {'desc': 'Waveform', 'val':{}, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'waveform','type':'dict'}},
                        'params':
                                {'desc': 'Environment parameters', 'val':{}, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'waveform','type':'dict'}}
                                
                      }       

        self.create_pvs(self.tasks)

        self.start()

    def connect(self, hostname):
        
        self.DPO5000 = TektronixScope('143')
        return self.DPO5000.connect()
        return False
        

    def disconnect(self):
        if self.connected:
            self.DPO5000.disconnect()

    def clear_bg(self):
        waveform = None
        self.bg_waveform = {'waveform':waveform}
        self.pvs['bg_waveform'].set(self.bg_waveform)


    def read_file(self, filename):
        waveform = None
        if filename.endswith('.csv'):
            waveform = read_tek_csv(filename)
        if filename.endswith('.npz'):
            waveform = read_npy(filename)

        self.bg_waveform = {'waveform':waveform}
        self.pvs['bg_waveform']._val = self.bg_waveform
        self.pvs['bg_waveform'].value_changed_signal.emit('bg_waveform',[self.bg_waveform])
        

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
        self.disconnect()


    def get_waveform(self):
        self.my_queue.put({'task_name':'get_waveform'})

    def get_num_acq(self):
        if self.waveform is not None:
            return self.waveform['num_av']
        else: return 0

    def _set_filename(self, filename):

        self.file_name = filename
        if filename.endswith('.csv'):
            self.pvs['file_extension'].set('Text (*.csv)')
            
        if filename.endswith('.npz'):
            self.pvs['file_extension'].set('Binary (*.npz)')
            
    def _set_params(self, params):
        self.params = params
    
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

    def _set_clear_all(self, clear):

        #print('clear all')
        self.DPO5000.clear()

    def _set_erase(self, param):
        if param:
            #self.clear_queue()
            #print('erasing')
            self._set_channel_state(False)
            self._set_channel_state(True)
            time.sleep(.05)
            self.pvs['erase'].set(False)

    def _get_instrument(self):
        ID = self.DPO5000.get_ID()
        if ID is not None:
            if len(ID):
                tokens = ID.split(',')
                ID = tokens[1]
        return ID
        
    def _set_num_av(self, num_av):
        self.DPO5000.set_num_av(num_av)

    def _get_num_av(self):

        
        num_av = self.DPO5000.get_num_av()
        
        return num_av

    def _get_num_acq(self):
        if self.waveform is not None:
            return self.waveform['num_acq']
        else: return 0
        #self.DPO5000.number_acquired()

    def _set_acquisition_type(self, acq_type):
        self.DPO5000.set_aquisition_type(acq_type)    

    def _get_acquisition_type(self):
        t = self.DPO5000.get_aquisition_type()  
        return t

    def _set_channel(self, channel):
        self.channel = channel.upper()
        self.DPO5000.set_data_source(self.channel)
        self.channel_changed_signal.emit()

    def _get_channel(self):
        ch = self.DPO5000.get_data_source()
        return ch

    def _get_setup(self):
        setup = self.DPO5000.get_setup_dict(force_load=True)
        return setup

    def _set_channel_state(self,state):
        channel = self._get_channel()
        if state:
            self.DPO5000.select_channel(channel)
        else:
            self.DPO5000.turn_off_channel(channel)
    
    def _get_channel_state(self):
        channel = self._get_channel()
        ans = self.DPO5000.is_channel_selected(channel)
        return ans

    def _get_run_state(self):
        state = self.DPO5000.get_state()
        return state

    def _set_run_state(self, state):
        if state:
            """Start acquisition"""
            self.DPO5000.start_acq()
        else:
            """Stop acquisition"""
            self.DPO5000.stop_acq()

    def _set_vertical_scale(self,scale):
        channel = self._get_channel()
        self.DPO5000.set_vertical_scale(channel, scale)
        
    def _get_vertical_scale(self):
        channel = self._get_channel()
        scale = self.DPO5000.get_vertical_scale(channel)
        return scale

    def _get_waveform(self): 
        #start = time.time()
        #wait_till = start+0.05
        
        data_stop = self.data_stop
        ch = self.selected_channel
        waveform  = self.DPO5000.read_data_one_channel( data_start=1, 
                                                        data_stop=data_stop,
                                                        x_axis_out=True)
        
        #end = time.time()
        
        # make sure set frame rate isn't exceeded
        #while time.time()< wait_till:
        #        time.sleep(0.005)
        num_acq =self.DPO5000.num_acq
        #elapsed = end - start
        (dt, micro) = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
        dt = "%s.%03d" % (dt, int(micro) / 1000)

        self.waveform = {'waveform':waveform,'ch':ch, 'time':dt, 'num_acq':num_acq}
        self.pvs['num_acq']._val = num_acq
        return self.waveform
