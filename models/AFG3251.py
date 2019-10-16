#-------------------------------------------------------------------------------
# Name:        AFG3000C - Passing a Waveform File into Internal Memory
# Purpose: This code is an example of how to send a AFG TFW file to editable memory on a AFG3000 generator
#
# Created using Python version 2.7
# Using Tekvisa v1.8
# Using Windows 7, Tekvisa version v4.1.0 or newer
# Created:     5/10/2016
# Copyright:   (c) Tektronix 2016
#-------------------------------------------------------------------------------


# TODO asymmetric waveform

import visa, time, logging, os, struct, sys, copy, os.path

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from models.AFGModel import Afg
from PyQt5.QtCore import QThread, pyqtSignal

import queue 
from functools import partial
from models.tek_fileIO import read_file_TEKAFG3000
import json
from models.pv_model import pvModel

class AFG_AFG3251(Afg, pvModel):

    model_value_changed_signal = pyqtSignal(dict)

    def __init__(self, parent, visa_hostname='202'):
        pvModel.__init__(self, parent)
        Afg.__init__(self)

        ## device speficic:
        self.instrument = 'AFG3251'
        self.settings_file_tag ='Waveform'

        self.duration = 50

        self.visa_hostname = visa_hostname
        self.connected = False
        #self.connected = self.connect(self.visa_hostname)
        if self.connected:
            #print('connected')
            pass
        
        
        self.function_shapes = ['sinusoid', 'square', 'pulse', 'ramp', 'prnoise', 'dc', 'sinc', 
                                'gaussian', 'lorentz', 'erise', 'edecay', 'haversine', 'user1', 
                                'user2', 'user3', 'user4', 'ememory', 'efile']
        self.operating_modes = ['continuous','burst n-cycles'] 
        
        # Task description markup. Aarbitrary default values ('val') are for type recognition in panel widget constructor
        # supported types are float, int, bool, string, and list of strings
        self.tasks = {  'amplitude': 
                                {'desc': 'Amplitude (Vpp)', 'val':1.0,'min':0.05,'max':9,'increment':0.05, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'amplitude','type':'f'}},
                        'frequency': 
                                {'desc': 'Frequency (Hz)', 'val':30000000.0, 'min':0, 'max':120000000,'increment':500000, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'frequency','type':'f'}},
                        'output_state':     
                                {'desc': 'Output;ON/OFF','val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'output_state','type':'b'}},
                        'n_cycles':  
                                {'desc': 'N-cycles', 'val':3,'min':1 ,'max':100000, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'n_cycles','type':'i'}},
                        'instrument':
                                {'desc': 'Instrument', 'val':self.instrument, 
                                'methods':{'set':False, 'get':True}, 
                                'param':{'tag':'instrument','type':'s'}},
                        'operating_mode':
                                {'desc': 'Operating mode', 'val':self.operating_modes[0],'list':self.operating_modes, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'operating_mode','type':'l'}},
                        'function_shape':
                                {'desc': 'Function shape', 'val':self.function_shapes[0],'list':self.function_shapes, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'function_shape','type':'l'}},
                        'user1_waveform':
                                {'desc': 'User waveform 1', 'val':{}, 
                                'methods':{'set':True, 'get':False}, 
                                'param':{'tag':'user1_waveform','type':'dict'}},
                        'user1_waveform_from_file':
                                {'desc': 'Waveform file', 'val':'', 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'user1_waveform_from_file','type':'s'}},
                      }       

        self.create_pvs(self.tasks)
        self.start()

    ###############################################################################
    #  Private device specific functions. Should not be used by external callers  #
    ###############################################################################    

    def _exit_task(self):
        self.disconnect()

    def ask(self, command):
        #print(command)
        if self.connected:
            ans = self.AFG3000.query(command)
            return ans
        else: return None

    def write(self, command):
        #print(command)
        if self.connected:
            self.AFG3000.write(command)
    
    def write_binary_values(self, command, binary_waveform):
        print (command)
        if self.connected:
            self.AFG3000.write_binary_values(command, binary_waveform, datatype='h', is_big_endian=True)

        
    def _get_instrument(self):
        
        ID = self.ask('*IDN?')
        if ID is not None:
            if len(ID):
                tokens = ID.split(',')
                ID = tokens[1]
        return ID

    def _set_user1_waveform(self, waveform):
        
        if 'binary_waveform' in waveform:
            binary_waveform = waveform['binary_waveform']
            slot='user1'
            #We can write the waveform data to the AFG after making sure its in big endian format
            self.write_binary_values('TRACE:DATA EMEMory,', binary_waveform)
            #'copies' the Editable Memory to User1 memory location. note: there are 4 user memory locations
            self.write('data:copy ' +slot+', ememory')
            self.pvs['function_shape'].set('user1')
            #self.write('source1:function '+slot) #sets the AFG source to user1 memory
    
    def _set_user1_waveform_from_file(self, filename):
        current_file = self.pvs['user1_waveform_from_file']._val
        if current_file != filename:
            if len(filename):
                if os.path.exists(filename):
                    waveform = self.read_file(filename)
                    if 'binary_waveform' in waveform:
                        self._set_user1_waveform(waveform)
                        
    def _get_user1_waveform_from_file(self):
        return self.pvs['user1_waveform_from_file']._val

    def read_file(self, filename='3pulse.tfw'):
        #Filename for TFW to be read in from the PC
        waveform = read_file_TEKAFG3000(filename)
        return waveform

    def _set_frequency(self, freq):
        
        freq_str = str(freq )
        command = 'source1:Frequency '+freq_str
        self.write(command) #set frequency 

    def _get_frequency(self):
        
        command = 'source1:Frequency?'
        ans = self.ask(command) # get frequency 
        ans = float(ans)
        return ans

    def _set_duration(self, duraton):
        
        self.duration = duration

    def _get_duration(self):
        
        ans = self.duration
        return ans
    
    def _set_amplitude(self, amplitude):
        
        a_str='%0.3f'%(amplitude)
        command = 'source1:voltage:amplitude '+a_str
        self.write(command) # sets voltage 

    def _get_amplitude(self):
        
        command = 'source1:voltage:amplitude?'
        ans = self.ask(command) #gets voltage Vpp
        ans = float(ans)
        return ans

    def _set_output_state(self, state):
        
        if state:
            state_str = 'ON'
        else:
            state_str = 'OFF'
        self.write('output1:state ' +state_str) # turns on/off output 1

    def _get_output_state(self):
        
        ans = self.ask('output1:state?') # gets output state
        ans = int(ans)
        return ans

    def _set_n_cycles(self, N):
        
        N_str='%d'%(N)
        command = 'SOURce1:BURSt:NCYCles ' + N_str
        self.write(command) #sets N cycles in burst mode 

    def _get_n_cycles(self):
        
        command = 'SOURce1:BURSt:NCYCles?'
        ans = self.ask(command) #gets N cycles in burst mode 
        ans = int(float(ans))
        return ans

    def _set_function_shape(self, shape):
        
        if type(shape) is str:
            if shape.lower() in self.function_shapes:
                command = 'SOURce1:FUNCtion:SHAPe ' + shape
                self.write(command) #sets shape

    def _get_function_shape(self):
        
        command = 'SOURce1:FUNCtion:SHAPe?'
        ans = self.ask(command) #gets shape
        ans = ans[:-1].lower()
        chars = len(ans)
        shapes = self.function_shapes
        for s in shapes:
            if ans == s[:chars].lower():
                return s
        return 'other'

    def _set_operating_mode(self, mode):
        if 'cont' in mode.lower() or 'cw' in mode.lower():
            command = 'Source1:Freq:Mode CW'
            self.write(command) #sets shape
        if mode.lower() in 'burst n-cycles'.lower():
            command = ':Source1:BURST:STAT ON;:Source1:BURSt:MODE TRIG'
            self.write(command) #sets shape
    
    def _get_operating_mode(self):
        command = 'Source1:Freq:Mode?'
        ans1 = self.ask(command)
        command = 'Source1:BURST:STAT?'
        ans2 = self.ask(command)
        command = 'Source1:BURSt:MODE?'
        ans3 = self.ask(command)
        command = 'SOURce1:BURSt:NCYCles?'
        ans4 = self.ask(command)
        if 'cw' in ans1.lower() and '0' in ans2:
            return 'continuous'
        if '1' in ans2 and 'trig' in ans3.lower():
            return 'burst n-cycles'
        return 'other'
            
    
    def connect(self, hostname):
        try:
            self.disconnect()
            rm = visa.ResourceManager()
            resources = rm.list_resources()
            r = None
            for r in resources:
                if hostname in r:
                    break
            if r is not None:
                # pyvisa code:
                AFG3000 = rm.open_resource(r)
                AFG3000.clear()
                ID = AFG3000.query('*IDN?')
                if ID is not None:
                    if len(ID):
                        tokens = ID.split(',')
                        ID = tokens[1]
                #print(ID)
                self.instrument = ID
                #AFG3000.write('*RST') #reset AFG
                self.AFG3000 = AFG3000
                return True
            else:
                return False
        except:
            self.AFG3000 = None
            return False

    

    def disconnect(self):
        if self.connected:
            try:
                if self.AFG3000 is not None:
                    self.AFG3000.clear()
                    self.AFG3000.close()
                    self.AFG3000 = None
                    self.connected = False
                    #print('disconnected')
            except:
                self.AFG3000 = None
                self.connected = False
            
    