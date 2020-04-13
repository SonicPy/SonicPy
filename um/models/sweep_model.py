
# TODO asymmetric waveform

import time, logging, os, struct, sys, copy

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from um.models.AFGModel import Afg
from PyQt5.QtCore import QThread, pyqtSignal

import queue 
from functools import partial
from um.models.tek_fileIO import read_file_TEKAFG3000
import json

from um.models.pv_model import pvModel


class setpointSweep(pvModel):
    model_value_changed_signal = pyqtSignal(dict)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent= parent
        self.instrument = 'setpointSweep'

        ## device speficic:
        self.tasks = {  
                        'setpoint': 
                                {'desc': 'Set-point', 'val':30., 'increment':0.1, 'min':0.001,'max':120,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'setpoint','type':'f'}},
                        'run_state':     
                                {'desc': 'Run;ON/OFF', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'run_state','type':'b'}}
                                
                                }
        self.create_pvs(self.tasks)
        #self.offline = True
        
        self.start()           

    def _set_setpoint(self, param):
        print('_set_setpoint '+str(param))
        self.source_waveform_pvs['setpoint'].set(param*1e6)
        self.scope_pvs['erase'].set(True)
        self.scope_pvs['run_state'].set(True)
       
        time.sleep(5)

    def _set_run_state(self, param):
        self.parent.pvs['run_state'].set(False)
        print('freq sweep done')
        

class SweepModel(pvModel):

    model_value_changed_signal = pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        ## device speficic:
        self.setpointSweepThread = setpointSweep(self)
        self.instrument = 'SweepModel'
        
        
        # Task description markup. Aarbitrary default values ('val') are for type recognition in panel widget constructor
        # supported types are float, int, bool, string, and list of strings
        self.tasks = {  'start_freq': 
                                {'desc': 'Start', 'val':10.0, 'increment':0.5,'min':.001,'max':110 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'start_freq','type':'f'}},
                        'end_freq': 
                                {'desc': 'End', 'val':40.0, 'increment':0.5, 'min':.002,'max':120,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'end_freq','type':'f'}},
                        'samples': 
                                {'desc': 'Samples', 'val':26,'min':1,'max':10000,
                                'methods':{'set':False, 'get':True},  
                                'param':{'tag':'samples','type':'i'}},
                        'step': 
                                {'desc': 'Step', 'val':1.0, 'min':0.01,'max':110,'increment':.1,
                                'methods':{'set':True, 'get':True},  
                                'param':{'tag':'step','type':'f'}},
                        'run_state':     
                                {'desc': 'Run;ON/OFF', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'output_state','type':'b'}},
                        'setpoint': 
                                {'desc': 'Set-point', 'val':30., 'increment':0.1, 'min':0.1,'max':100,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'end_freq','type':'f'}}
                                
                                }

        self.create_pvs(self.tasks)
        self.offline = True
        self.samples = []
        self.start()


    #####################################################################
    #  Private set/get functions. Should not be used by external calls  #
    #####################################################################    

    def exit(self):
        super().exit()
        self.setpointSweepThread.exit()

    def clear_waveforms(self):
        self.sweep = {}

    def get_waveform(self, ind):
        freqs = sorted(list(self.sweep.keys()))
        if ind >= 0 and ind < len(freqs):
            freq = freqs[ind]
            waveform = self.sweep[freq]
            return (waveform.get_x(), waveform.get_y()), freq
        else:
            return None


    def samples_updated(self, samples):
        self.samples={'setpoints':samples}
        n = len(samples)
        self.pvs['samples']._val = str(n)
        self.pvs['samples'].value_changed_signal.emit('samples',[n])

    def _set_start_freq(self, param):

        samples = get_samples(param, self.pvs['end_freq']._val, self.pvs['step']._val)
        self.samples_updated(samples)
        
    def _set_end_freq(self, param):
        samples = get_samples(self.pvs['start_freq']._val, param,  self.pvs['step']._val)
        self.samples_updated(samples)

    '''
    def _set_samples(self, param):
        print(param)
    '''

    def _set_step(self, param):

        samples = get_samples(self.pvs['start_freq']._val,  self.pvs['end_freq']._val, param)
        self.samples_updated(samples)

    def _set_run_state(self, param):
        if param:
            samples = get_samples(self.pvs['start_freq']._val,  self.pvs['end_freq']._val, self.pvs['step']._val)
            self.samples_updated(samples)
        else:
            self.setpointSweepThread.clear_queue()

    '''
    def _get_start_freq(self):
        return self.pvs['start_freq']._val
    def _get_end_freq(self):
        return self.pvs['end_freq']._val
    def _get_samples(self):
        return self.pvs['samples']._val
    def _get_step(self):
        return self.pvs['step']._val
    def _get_run_state(self):
        return self.pvs['run_state']._val
    '''

def get_samples(start_freq, end_freq, step):
    samples = [start_freq]
    sample = round(start_freq,5)
    #print(start_freq)
    #print(end_freq)
    #print(step)
    
    while sample < end_freq:
        
        sample = round(sample + step,5)
        samples.append(sample)
    #print(samples)
    return samples