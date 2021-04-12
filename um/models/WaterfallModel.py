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


class WaterfallModel(Scope, pvModel):

    def __init__(self, parent):
        
        pvModel.__init__(self, parent)
      
        self.instrument = 'Waterfall'
        self.scans = []
        self.scans.append({})
        self.tasks = {  
                        'waveform_in':     
                                {'desc': 'Waveform in', 'val':None, 
                                'param':{ 'type':'dict'}},
                        'waterfall_out':     
                                {'desc': 'Waveform out', 'val':None, 
                                'param':{ 'type':'dict'}},
                        'scale': {'desc': 'Scale', 'unit':'', 'val':1.0,'min':0.000001,'max':100000,'increment':0.1, 
                                'param':{'type':'f'}},
                        'clear':     
                                {'desc': ';Clear', 'val':False, 
                                'param':{ 'type':'b'}},
                        'clip':     
                                {'desc': ';Clip', 'val':True, 
                                'param':{ 'type':'b'}}
                      }       
        
        self.create_pvs(self.tasks)

    #####################################################################
    #  Private set/get functions. Should not be used by external calls  #
    #####################################################################    

    def _exit_task(self):
        pass

    def _get_waterfall_out(self):
        ans = self.pvs['waterfall_out']._val
        #print('get ' + str(ans))
        return ans

    def _set_waveform_in(self, param):
        #print('set ' + str(param))
        fname = param['filename']
        wform = param['waveform']
        x = wform[0][::2]
        y = wform[1][::2]
        wform = [x,y]
        self.scans[0][fname]=wform

        self.pvs['waveform_in']._val= param

        self.rescale_waveforms()

    def _set_scale(self, param):
        self.pvs['scale']._val= param
        self.rescale_waveforms()



    def _set_clip(self, param):
        self.pvs['clip']._val= param
        self.rescale_waveforms()

    def rescale_waveforms(self):
        out = {}
        scale = self.pvs['scale' ]._val
        offset = 1
        clip = self.pvs['clip' ]._val

        fnames = sorted( list(self.scans[0].keys()))
        #print(fnames)
        if len(fnames):
            x = np.empty([0])
            y = np.empty([0])
            
            for i, f in enumerate(fnames):
                
                key = f
                waveform = self.scans[0][key]
                
                x_next = waveform[0]
                y_next = waveform[1]*float(scale)
                if clip:
                    y_next[y_next>(offset/2)] = offset/2 * 0.9
                    y_next[y_next<(-1*offset/2)] = -1*offset/2 * 0.9
                y_next = y_next + i * float(offset)
                
                
                if len(x):
                    x = np.append(x,np.nan)
                    y = np.append(y,np.nan)
                
                x = np.append(x,x_next)
                y = np.append(y,y_next)
            waveform = [x,y]
            out = {key:waveform}
            
        self.pvs['waterfall_out'].set(out)


    def _set_clear(self, param):
        if param:
            self.scans[0]={}
            self.pvs['waterfall_out'].set(self.scans[0])
            self.pvs['clear'].set( False)
        else:
            self.pvs['clear']._val = False    