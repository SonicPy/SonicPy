
from enum import auto
import os.path, sys
import wave
import numpy as np
from sqlalchemy import false, true
from um.models.ScopeModel import Scope
from um.models.tek_fileIO import *
from utilities.utilities import *
import logging, os, struct, sys
import pyvisa as visa
from um.models.PyTektronixScope import TektronixScope
from PyQt5.QtCore import QThread, pyqtSignal
import time
from datetime import datetime

import queue 
from functools import partial
import json
from um.models.pv_model import pvModel
import copy

from utilities.HelperModule import get_partial_index, get_partial_value


class Scope_DPO5104(Scope, pvModel):
    waveform_updated_signal = pyqtSignal(dict)
    channel_changed_signal = pyqtSignal()
    model_value_changed_signal = pyqtSignal(dict)

    def __init__(self, parent, visa_hostname='143', offline = False):
        
        
        self.virtual_data = read_tek_csv('anvil.csv')

        pvModel.__init__(self, parent)
        Scope.__init__(self)
        
        ## device speficic:
        
        self.instrument = 'DPO5104'
        self.settings_file_tag ='Scope'

        self.visa_hostname = visa_hostname
        self.connected = False
        
        if not offline:
            self.connected = self.connect(self.visa_hostname)
        
        
        
        self.data_stop = 10000
        self.selected_channel = 'CH1'

        self.acquisition_types = ['sample', 'peak', 'hires', 'envelope', 'average']
        self.channels = ['CH1','CH2','CH3','CH4']
     
        self.tasks = {  'acquisition_type': 
                                {'desc': 'Acqusition type', 'val':self.acquisition_types[0], 'list':self.acquisition_types, 
                                'param':{ 'type':'l'}},
                        'num_av': 
                                {'desc': 'N-average', 'val':1000, 'min':2,'max':10000,
                                'param':{ 'type':'i'}},
                        'stop_after_num_av_preset':     
                                {'desc': 'Auto stop;ON/OFF', 'val':True, 
                                'param':{ 'type':'b'}},
                        'num_acq': 
                                {'desc': 'N-acquired', 'val':0, 'min':0,'max':1e29,
                                'methods':{'set':False, 'get':True},  
                                'param':{ 'type':'i'}},
                        'channel': 
                                {'desc': 'Data source', 'val':self.channels[0],'list':self.channels,
                                'param':{ 'type':'l'}},      
                        'channel_state': 
                                {'desc': 'Channel state;ON/OFF', 'val':False, 
                                'param':{ 'type':'b'}},
                        'run_state':     
                                {'desc': 'Run state;ON/OFF', 'val':False, 
                                'param':{ 'type':'b'}},
                        'erase_start':     
                                {'desc': u';Erase + ON', 'val':False, 
                                'param':{ 'type':'b'}},
                        'erase':     
                                {'desc': 'Erase;Erase', 'val':False, 
                                'param':{ 'type':'b'}},
                        'vertical_scale':  
                                {'desc': 'Vertical scale','unit':u'V', 'val':1.0,'increment':0.05, 'min':1e-9,'max':10,
                                'param':{ 'type':'f'}},
                        'instrument':
                                {'desc': 'Instrument', 'val':'not connected', 
                                'methods':{'set':False, 'get':True}, 
                                'param':{ 'type':'s'}},   
                        'waveform':
                                {'desc': 'Waveform', 'val':{}, 
                                'methods':{'set':False, 'get':True}, 
                                'param':{ 'type':'dict'}},
                        'do_autoscale':
                                {'desc': 'Autoscale (V);Do once', 'unit':u'V', 'val':False, 
                                'param':{ 'type':'b'}},
                        'autoscale_t_min':  
                                {'desc': 'Autscale t<sub>min</sub>','unit':u'us', 'val':3.0,'increment':0.1, 'min':0,'max':20,
                                'param':{ 'type':'f'}},
                        'autoscale_t_max':  
                                {'desc': 'Autscale t<sub>max</sub>','unit':u'us', 'val':9.0,'increment':0.1, 'min':0,'max':20,
                                'param':{ 'type':'f'}},
                        'autoscale_margin':  
                                {'desc': 'Autoscale +/-','unit':u'%', 'val':30,'min':0,'max':100,
                                'param':{ 'type':'i'}},
                        'auto_autoscale':
                                {'desc': 'Autoscale (V); ON/OFF', 'val':False, 
                                'param':{ 'type':'b'}},
                                
                      }       

        self.create_pvs(self.tasks)

    def connect(self, hostname):
        
        self.DPO5000 = TektronixScope(hostname)
        return self.DPO5000.connect()
        
        

    def disconnect(self):
        if self.connected:
            self.DPO5000.disconnect()

    '''def clear_bg(self):
        waveform = None
        self.bg_waveform = {'waveform':waveform}
        self.pvs['bg_waveform'].set(self.bg_waveform)'''

    '''
    def read_file(self, filename):
        waveform = None
        if filename.endswith('.csv'):
            waveform = read_tek_csv(filename)
        if filename.endswith('.npz'):
            waveform = read_npy(filename)

        self.bg_waveform = {'waveform':waveform}
        self.pvs['bg_waveform']._val = self.bg_waveform
        self.pvs['bg_waveform'].value_changed_signal.emit('bg_waveform',[self.bg_waveform])
    '''
    
    
    #####################################################################
    #  Private set/get functions. Should not be used by external calls  #
    #####################################################################    

    def _exit_task(self):
        self.disconnect()



    def _set_erase_start(self, params):
        self.pvs['erase_start']._val = params
        if params:
            autoscale = self.pvs['auto_autoscale']._val
            if autoscale:
                self.pvs['do_autoscale'].set (True)
            self.pvs['erase'].set (True)
            self.pvs['run_state'].set (True)
            self.pvs['erase_start'].set(False)
            
    def _set_auto_autoscale(self, params):
        if params:
            self.pvs['do_autoscale'].set (True)

    def _set_clear_all(self, clear):

        #print('clear all')
        self.DPO5000.clear()

    def _set_erase(self, param):
        if param:
            try:
                #self.clear_queue()
                #print('erasing')
                
                
                self._set_channel_state(False)
                n = self.pvs['num_av']._val
                self.pvs['num_av'].set(1)
                self.pvs['num_av'].set(n)
                self.pvs['num_acq'].set(0)
                self.pvs['waveform']._val={}
                
                self._set_channel_state(True)
                #print('erased')
                
            except:
                pass
            self.pvs['erase'].set(False)

    def _get_instrument(self):
        if self.connected:
            ID = self.DPO5000.get_ID()
            if ID is not None:
                if len(ID):
                    tokens = ID.split(',')
                    ID = tokens[1]
        else:
            ID = 'not connected'
        return ID
        
    def _set_num_av(self, num_av):
        self.pvs['num_av']._val = num_av
        if self.connected:
            self.DPO5000.set_num_av(num_av)

    def _get_num_av(self):

        if self.connected:
            num_av = self.DPO5000.get_num_av()
        else:
            num_av = self.pvs['num_av']._val
        
        return num_av


    def _set_acquisition_type(self, acq_type):
        self.pvs['acquisition_type']._val = acq_type
        if self.connected:
            self.DPO5000.set_aquisition_type(acq_type)    

    def _get_acquisition_type(self):
        if self.connected:
            t = self.DPO5000.get_aquisition_type()  
        else:
            t = self.pvs['acquisition_type']._val
        return t

    def _set_channel(self, channel):
        self.pvs['channel']._val = channel.upper()
        if self.connected:
            channel = self.pvs['channel']._val
            self.DPO5000.set_data_source(channel)
            

    def _get_channel(self):
        if self.connected:
            ch = self.DPO5000.get_data_source()
        else:
            ch = self.pvs['channel']._val
        return ch

    def _get_setup(self):
        if self.connected:
            setup = self.DPO5000.get_setup_dict(force_load=True)
        else:
            setup = self.pvs['setup']._val
        return setup

    def _set_channel_state(self,state):
        if self.connected:
            channel = self._get_channel()
            if state:
                self.DPO5000.select_channel(channel)
            else:
                self.DPO5000.turn_off_channel(channel)

    
    def _get_channel_state(self):
        if self.connected:
            channel = self._get_channel()
            ans = self.DPO5000.is_channel_selected(channel)
        else:
            ans = self.pvs['channel_state']._val    
        return ans

    def _get_run_state(self):
        #print('_get_run_state')
        if self.connected:
            state = self.DPO5000.get_state()
        else:
            state = self.pvs['run_state']._val  
        return state

    def _set_run_state(self, state):
        #print('_set_run_state')
        self.pvs['run_state']._val = state
        if self.connected:
            if state:
                """Start acquisition"""
                self.DPO5000.start_acq()
            else:
                """Stop acquisition"""
                self.DPO5000.stop_acq()

    def _set_vertical_scale(self,scale):
        self.pvs['vertical_scale']._val = scale
        if self.connected:
            channel = self._get_channel()
            #print(scale)
            self.DPO5000.set_vertical_scale(channel, scale)
        
    def _get_vertical_scale(self):
        if self.connected:
            channel = self._get_channel()
            scale = self.DPO5000.get_vertical_scale(channel)
        else:
            scale = self.pvs['vertical_scale']._val      
        return scale

    def _set_do_autoscale(self, param):
        if param:
            #print('autoscale')
            state = self._get_run_state()
            #print(state)
            
            num_av = self.pvs['num_av']._val

            autoscale_margin = self.pvs['autoscale_margin']._val

            #print(num_av)
            self._set_channel_state(False)
            #print('self._set_channel_state(False)')
            self._set_num_av(20)
            #print("_set_num_av(1)")
            self._set_run_state(True)
            #print('_set_run_state(True)')
            self._set_channel_state(True)
            #print('_set_channel_state(True)')
            autostop = copy.copy(self.pvs['stop_after_num_av_preset']._val )
            self.pvs['stop_after_num_av_preset']._val = False
            waveform = self._get_waveform(wait=False)['waveform']
            self.pvs['stop_after_num_av_preset']._val = autostop
            #print(waveform)
            t = waveform[0]
            V = waveform[1]
            
            t_min = self.pvs['autoscale_t_min']._val * 1e-6
            t_max = self.pvs['autoscale_t_max']._val * 1e-6
            #print(t_min)
            #print(t_max)

            t_min_index = int(round(get_partial_index(t, t_min)))
            t_max_index = int(round(get_partial_index(t, t_max)))

            V_subset = V[t_min_index:t_max_index]
            
            V_min = np.amin(V_subset)
            V_max = np.amax( V_subset)

            V_max = max(V_max, abs(V_min))

            #print(V_max)

            V_range = V_max * (1 + autoscale_margin /100)
            V_div = round(V_range / 5,3)
            #print(V_div)


            
            self._set_num_av(num_av)
            
            self._set_run_state(state)
            self.pvs['vertical_scale'].set(float(V_div))
            self.pvs['do_autoscale'].set(False)
            #print('autoscaled')

    def _get_waveform(self, wait=True): 
        #print('get waveform')

        if self.connected:
            #print('connected')
            start = time.time()
            wait_till = start+0.1
            num_av = self.pvs['num_av']._val
            num_acq = self.pvs['num_acq']._val
            stop_after_preset = self.pvs['stop_after_num_av_preset']._val

            if num_acq < num_av or not stop_after_preset:
                
                data_stop = self.data_stop
                ch = self.selected_channel
                #print('about to read')
                waveform  = self.DPO5000.read_data_one_channel( data_start=1, 
                                                                data_stop=data_stop,
                                                                x_axis_out=True)
                
                #end = time.time()
                # make sure set frame rate isn't exceeded
                if wait:
                    while time.time()< wait_till:
                        time.sleep(0.005)
                num_acq = int(self.DPO5000.num_acq)
                #elapsed = end - start
                (dt, micro) = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
                dt = "%s.%03d" % (dt, int(micro) / 1000)

                waveform_out = {'waveform':waveform,'ch':ch, 'time':dt, 'num_acq':num_acq}
                
        else:
            #print('reading csv file')
            num_acq = self.pvs['num_av']._val
            
            ch = 1
            (dt, micro) = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
            dt = "%s.%03d" % (dt, int(micro) / 1000)
            scale = self.pvs['vertical_scale']._val
            v_max = scale * 5 
            waveform = self.virtual_data
            #print(v_max)
            time.sleep(.05)
            noise_scale = 0.002
            waveform_noised = waveform[1]+(np.random.normal(0,1,len(waveform[1]))-0.5)*noise_scale
            
            v = waveform_noised
            v[v>v_max] = v_max
            v[v<(v_max*-1)] = -1*v_max

            #print('read csv file')
            waveform_out = {'waveform':[waveform[0],waveform_noised],'ch':ch, 'time':dt, 'num_acq':num_acq}  

        #print('num_acq: '+str(num_acq))
        self.pvs['num_acq'].set(int(num_acq))

        stop_after_preset = self.pvs['stop_after_num_av_preset']._val

        if stop_after_preset:
            running = self.pvs['run_state']._val
            #print('run_state: ' + str(running))
            if running:
                
                num_av = self.pvs['num_av']._val
                
                #print('num_av: ' + str(num_av))
                #print('num_acq >= num_av: '+ str(num_acq >= num_av))
                if num_acq >= num_av:
                    
                    #print('num_acq >= num_av: ' + str(True))
                    self.pvs['run_state'].set(False)
        #print('returning waveform_out')

        
        return waveform_out


