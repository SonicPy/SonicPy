
import os.path, sys
import numpy as np
from models.ScopeModel import Scope
from utilities.utilities import *
import visa, logging, os, struct, sys
from models.PyTektronixScope import TektronixScope
from PyQt5.QtCore import QThread, pyqtSignal
import time
from datetime import datetime

import queue 

#Global queue, import this from anywhere, you will get the same object.

class Scope_DPO5104(Scope, QThread):
    waveform_updated_signal = pyqtSignal(dict)
    def __init__(self, parent, visa_hostname='143'):
        
        QThread.__init__(self,parent)
        Scope.__init__(self)
        self.my_queue = queue.Queue()
        self.instrument = ''
        self.visa_hostname = visa_hostname
        self.channel = 1
        self.resolution = 100e-12       # second / sample
        self.accumulations = 1000   
        self.waveform = None
        self.mode = 1                   # 0 = single; 1 = n-accumulate; 2 = inf-accumulate
        self.connected = False
        self.DPO5000 = None
        self.connected = self.connect(self.visa_hostname)
        if self.connected:
            self.start()

    def run(self):
        self.go= True
        
        # do stuff
        i = 0 
        while self.go:
            task = self.my_queue.get()

            

            if 'task_name' in task:
                task_name = task['task_name']

                
                
                if task_name == 'get_waveform':
                    if 'param'in task:
                        param = task['param']
                        ch = param
                        booster = i>0    # booster saves time
                        waveform = self._get_waveform(ch=ch, booster=booster)
                        i=i+1
                        self.waveform_updated_signal.emit(waveform)

                if task_name == 'exit':
                    self.go = False
                    i = 0
                if task_name == 'set_state':
                    if 'param'in task:
                        param = task['param']
                        if param:
                            self._start_acq()
                        else:
                            self._stop_acq()
                    i = 0
                if task_name == 'set_aquisition_type':
                    if 'param'in task:
                        param = task['param']
                        acq_type= param['acq_type'] 
                        num_av=param['num_av'] 
                        self._set_aquisition_type(acq_type, num_av)
                        
                    i = 0
                if task_name == 'set_vertical_scale':
                    if 'param'in task:
                        param = task['param']
                        print ('set_vertical_scale: '+str(param))
                    i = 0
                if task_name == 'select_channel':
                    if 'param'in task:
                        param = task['param']
                        channel = param['channel']
                        state = param['state']
                        print ('select_channel: '+str(channel) +', state: '+str(state))
                        self._select_channel(channel,state)
                    i = 0

        self.go = False

    def get_setup(self):
        setup = self.DPO5000.get_setup_dict(force_load=True)
        return setup

    def set_aquisition_type(self, acq_type='average', num_av=1):
        task = ({'task_name':'set_aquisition_type','param':{'acq_type':acq_type, 'num_av':num_av}})
        self.my_queue.put(task)

    def _set_aquisition_type(self, acq_type='average', num_av=1):
        self.DPO5000.set_aquisition_type(acq_type, num_av)
   
    def get_waveform(self, ch=1):
        self.my_queue.put({'task_name':'get_waveform','param':ch})

    def select_channel(self,channel,state):
        self.my_queue.put({'task_name':'select_channel', 'param':{'channel':channel,'state':state}})

    def _select_channel(self,channel,state):
        if state:
            self.DPO5000.select_channel(channel)
        else:
            self.DPO5000.turn_off_channel(channel)

    def set_state(self, state):
        self.my_queue.put({'task_name':'set_state', 'param':state})

    def _get_state(self):
        state = self.DPO5000.get_state()
        return state

    def stop(self):
        self.go = False

    def set_vertical_scale(self,scale):
        self.my_queue.put({'task_name':'set_vertical_scale', 'param':scale})
        
    def _set_vertical_scale(self,scale):
        self.DPO5000.set_vertical_scale(scale)

    def _start_acq(self):
        """Start acquisition"""
        self.DPO5000.start_acq()
        
    def _stop_acq(self):
        """Stop acquisition"""
        self.DPO5000.stop_acq()

    def set_accumulations(self, accumulations):
        self.DPO5000.set_aquisition_type(acq_type='average',num_av=accumulations)

    def read_file(self, filename='', x_axis_out = True):
        bin_width = 20
        
        x, y = read_tek_csv(filename,return_x=True)
        x = rebin(x,bin_width)
        y = rebin(y,bin_width)

        if x_axis_out:
            return x, y
        else:
            return y
        
    def _get_waveform(self, ch=1, x_axis_out=True, booster=False): 
        start = time.time()
        waveform  = self.DPO5000.read_data_one_channel( ch,
                                                        data_start=1, 
                                                        booster=booster, 
                                                        data_stop=100000,
                                                        x_axis_out=x_axis_out)
        end = time.time()
        elapsed = end - start
        (dt, micro) = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
        dt = "%s.%03d" % (dt, int(micro) / 1000)
        self.waveform = {'waveform':waveform,'ch':ch, 'time':dt, 'transfer_time':elapsed}
        return self.waveform

    def read_waveform(self):
        return self.waveform

    def connect(self, hostname):
        try:
            self.disconnect()
            rm = visa.ResourceManager()
            resources = rm.list_resources()
            print(resources)
            r = None
            for r in resources:
                if hostname in r:
                    break
            if r is not None:
                # pyvisa code:
                instrument = rm.open_resource(r)
                ID = instrument.query('*IDN?')
                print(ID)
                self.instrument = ID
                DPO5000 = TektronixScope(instrument)
                self.DPO5000 = DPO5000
                
                return True
            else:
                return False
        except:
            self.DPO5000 = None
            return False

    def disconnect(self):
        if self.connected:
            try:
                if self.DPO5000 is not None:
                    self.DPO5000.close()
                    self.DPO5000 = None
                    self.connected = False
            except:
                pass