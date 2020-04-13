
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
import numpy as np

from um.models.pv_model import pvModel


class setpointSweep(pvModel):
    model_value_changed_signal = pyqtSignal(dict)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent= parent
        self.instrument = 'setpointSweep'

        ## device speficic:
        self.tasks = {  
                        'det_trigger_channel':     
                                {'desc': 'Output channel', 'val':None, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'output_channel','type':'pv'}},
                        'setpoint_channel':     
                                {'desc': 'Output channel', 'val':None, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'output_channel','type':'pv'}},
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
        #self.source_waveform_pvs['setpoint'].set(param*1e6)
        #self.scope_pvs['erase'].set(True)
        #self.scope_pvs['run_state'].set(True)
       
        time.sleep(.5)

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
                        'n': 
                                {'desc': '#Pts', 'val':26,'min':1,'max':10000,
                                'methods':{'set':True, 'get':True},  
                                'param':{'tag':'n','type':'i'}},
                        'step': 
                                {'desc': 'Step size', 'val':1.0, 'min':0.001,'max':110,'increment':.1,
                                'methods':{'set':False, 'get':True},  
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
        self.points = {'setpoints':[]}
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

    def _set_n(self, param):
        self.pvs['n']._val = int(param)
        self.get_points()

    def _set_start_freq(self, param):
        self.pvs['start_freq']._val = float(param)
        self.get_points()
        
    def _set_end_freq(self, param):
        self.pvs['end_freq']._val = float(param)
        self.get_points()

    def _set_run_state(self, param):
        if param:
            self.get_points()
        else:
            self.setpointSweepThread.clear_queue()
    
    def get_points(self):
        points, step = get_points(self.pvs['start_freq']._val,  self.pvs['end_freq']._val, self.pvs['n']._val)
        self.points = self.points={'setpoints':points}
        self.pvs['step'].set(step)
        
def get_points(start_freq, end_freq, n):
    rng = end_freq - start_freq
    step = rng / (n -1)
    points = []
    for i in range(n):
        points.append(float(start_freq+i*step))
    return points, float(step)
