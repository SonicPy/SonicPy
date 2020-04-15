
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
from um.models.pvServer import pvServer


class setpointSweep(pvModel):
    model_value_changed_signal = pyqtSignal(dict)
    detector_busy_signal = pyqtSignal(bool)
    positioner_busy_signal = pyqtSignal(bool)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent= parent
        self.instrument = 'setpointScan'
        self.pv_server = pvServer()
        
        ## device speficic:
        self.tasks = {  
                        
                        'current_setpoint_index': 
                                {'desc': 'Current set-point index', 'val':0,'min':0,'max':10000,
                                'methods':{'set':True, 'get':True},  
                                'param':{'tag':'current_setpoint_index','type':'i'}},
                        'current_setpoint': 
                                {'desc': 'Current set-point', 'val':0., 'increment':0.1, 'min':-10e11,'max':10e11,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'current_setpoint','type':'f'}},
                        'setpoints':     
                                {'desc': 'Setpoints', 'val':None, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'setpoints','type':'dict'}},
                        'run_state':     
                                {'desc': 'Run;ON/OFF', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'run_state','type':'b'}},
                        'start_scan':     
                                {'desc': '', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'start_scan','type':'b'}},
                        'advance_to_next':     
                                {'desc': '', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'advance_to_next','type':'b'}},
                        'acquire':     
                                {'desc': '', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'acquire','type':'b'}},
                        'do_point':     
                                {'desc': '', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'do_point','type':'b'}},
                        'detector_done':     
                                {'desc': '', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'detector_done','type':'b'}},
                                
                        'detector_trigger':     
                                {'desc': '', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'detector_trigger','type':'b'}},
                                
                        'positioner_done':     
                                {'desc': '', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'positioner_done','type':'b'}},
                                
                        'move_positioner':     
                                {'desc': '', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'positioner_done','type':'b'}}
                                }
        self.create_pvs(self.tasks)
        self.start()           
    
    def _set_acquire(self, param):
        if param:
            p = self.pvs['current_setpoint']._val
            print('aquiring @ ' +str(p))
            detector_pvname = self.parent.pvs['det_trigger_channel']._val
            detector_pv = self.pv_server.get_pv(detector_pvname)
            detector_pv.set(True)
            

    def wait_for_detector_done(self, pv, param):
        param = param[0]
        if not param:
            detector_pvname = self.parent.pvs['det_run_state_channel']._val
            detector_pv = self.pv_server.get_pv(detector_pvname)
            detector_pv.value_changed_signal.disconnect(self.wait_for_detector_done)
            print('detector done')
            
            self.pvs['detector_done'].set(True)

    def wait_for_positioner_done(self, param):
        
        if not param:
            self.positioner_busy_signal.disconnect(self.wait_for_positioner_done)
            print('positioner done')
            
            self.pvs['positioner_done'].set(True)

    def _set_move_positioner(self, param):
        if param:
            p = self.pvs['current_setpoint']._val
            #print('moving positioner to: ' +str(p))
            positioner_pvname = self.parent.pvs['positioner_channel']._val
            print (str(positioner_pvname)+ ' = '+str(p))
            positioner_pv = self.pv_server.get_pv(positioner_pvname)
            print (str(positioner_pv)+ ' = '+str(p))
            positioner_pv.set(p*1e6)

            # replace timer with event from positioner (AFG, etc)
            time.sleep(.5)   
            self.positioner_busy_signal.emit(False)

    def _set_detector_done(self, param):
        
        # do something with the acquire point

        # go to next point if run_state is True
        run_state = self.pvs['run_state']._val
        if run_state:
            self.pvs['advance_to_next'].set(True)

    def _set_positioner_done(self, param):
        
        # do something with the acquire point

        # go to next point if run_state is True
        run_state = self.pvs['run_state']._val
        if run_state:
            self.pvs['detector_trigger'].set(True)

    def _set_detector_trigger(self, param):
        detector_pvname = self.parent.pvs['det_run_state_channel']._val
        print(detector_pvname)
        detector_pv = self.pv_server.get_pv(detector_pvname)
        print('pv: ' + str(detector_pv))
        detector_pv.value_changed_signal.connect(self.wait_for_detector_done)
        self.pvs['acquire'].set(True)
            

    def _set_do_point(self, param):
        pts = self.pvs['setpoints']._val['setpoints']
        index = self.pvs['current_setpoint_index']._val
        
        if len (pts):
            p = pts[index]
            self.pvs['current_setpoint'].set(p)
            
        else:
            self.pvs['run_state'].set(False)

    def _set_run_state(self, param):
        currently_running = self.pvs['run_state']._val
        self.pvs['run_state']._val = param
        if param:
            if not currently_running:  
                self.pvs['start_scan'].set(True)
                print('point sweep starting')
        else:
            self.parent.pvs['scan_go'].set(False)
            print('point sweep done')

    def _set_start_scan(self, param):
        self.pvs['current_setpoint_index'].set(0)
        self.pvs['start_scan']._val = param
        if param:
            self.pvs['do_point'].set(True)

    def _set_advance_to_next(self, param):
        pts = self.pvs['setpoints']._val['setpoints']
        index = self.pvs['current_setpoint_index']._val
        
        if len(pts)>index+1:
            print('advancing to index: ' + str(index+1))
            self.pvs['current_setpoint_index'].set(index+1)
            self.pvs['do_point'].set(True)
        else:
            self.pvs['run_state'].set(False)
        
    
    def _set_setpoints(self, param):
        print('_set_setpoints '+str(param))
        self.pvs['setpoints']._val = param

    def _set_current_setpoint(self, param):
        self.positioner_busy_signal.connect(self.wait_for_positioner_done)
        print('septoint updated: '+ str(param))
        self.pvs['move_positioner'].set(True)
        

    def _set_current_setpoint_index(self, param):
        self.pvs['current_setpoint_index']._val = param
        print('setpoint index: '+str(param))

    
        
class SweepModel(pvModel):

    model_value_changed_signal = pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        ## device speficic:
        self.setpointSweepThread = setpointSweep(self)
        self.instrument = 'ScanModel'
        
        
        # Task description markup. Aarbitrary default values ('val') are for type recognition in panel widget constructor
        # supported types are float, int, bool, string, and list of strings
        self.tasks = {  'det_trigger_channel':
                                {'desc': 'Detector', 'val':'DPO5104:erase_start', 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'det_trigger_channel','type':'s'}},
                        'det_run_state_channel':
                                {'desc': 'Detector', 'val':'DPO5104:run_state', 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'det_run_state_channel','type':'s'}},
                        
                        'positioner_channel':     
                                {'desc': 'Positioner', 'val':'AFG3251:frequency', 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'positioner_channel','type':'s'}},
                        'start_point': 
                                {'desc': 'Start', 'val':10.0, 'increment':0.5,'min':.001,'max':110 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'start_point','type':'f'}},
                        'end_point': 
                                {'desc': 'End', 'val':40.0, 'increment':0.5, 'min':.002,'max':120,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'end_point','type':'f'}},
                        'n': 
                                {'desc': '#Pts', 'val':6,'min':2,'max':10000,
                                'methods':{'set':True, 'get':True},  
                                'param':{'tag':'n','type':'i'}},
                        'current_index': 
                                {'desc': 'Point', 'val':0,'min':0,'max':10000,
                                'methods':{'set':False, 'get':True},  
                                'param':{'tag':'current_index','type':'i'}},
                        
                        'step': 
                                {'desc': 'Step size', 'val':1.0, 'min':0.001,'max':110,'increment':.1,
                                'methods':{'set':False, 'get':True},  
                                'param':{'tag':'step','type':'f'}},
                        'scan_go':     
                                {'desc': 'Scan;Go', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'output_state','type':'b'}},
                        'scan_stop':     
                                {'desc': 'Scan;Stop', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'output_state','type':'b'}},
                        'scan_pause':     
                                {'desc': 'Scan;Stop', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'output_state','type':'b'}},
                        'setpoint': 
                                {'desc': 'Set-point', 'val':30., 'increment':0.1, 'min':0.1,'max':100,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'set_point','type':'f'}}
                                }

        self.create_pvs(self.tasks)
        self.offline = True
        self.points = {'setpoints':[]}

        self.setpointSweepThread.pvs['run_state'].value_changed_signal.connect(self.scan_done_callback)
        self.setpointSweepThread.pvs['current_setpoint_index'].value_changed_signal.connect(self.current_setpoint_index_callback)
        
        self.start()

 

    #####################################################################
    #  Private set/get functions. Should not be used by external calls  #
    #####################################################################    


    def exit(self):
        super().exit()
        self.setpointSweepThread.exit()

    def clear_waveforms(self):
        self.sweep = {}

    def scan_done_callback(self, pv, data):
        running = data[0]
        if not running:
            print('scan_go: False')
            self.pvs['scan_go'].set(False)

    def current_setpoint_index_callback(self, pv, data):
        ind = data[0]
        self.pvs['current_index'].set(ind+1)

    def stop_scan(self):
        self.setpointSweepThread.pvs['run_state']._val = False

    def start_sweep(self):
        # here we do the setpoint sweep
        setpoints = copy.deepcopy(self.points)
        self.setpointSweepThread.pvs['setpoints'].set(setpoints)
        
        self.setpointSweepThread.pvs['run_state'].set(True)

    def get_waveform(self, ind):
        points = sorted(list(self.sweep.keys()))
        if ind >= 0 and ind < len(points):
            point = points[ind]
            waveform = self.sweep[point]
            return (waveform.get_x(), waveform.get_y()), point
        else:
            return None

    def _set_n(self, param):
        self.pvs['n']._val = int(param)
        self.get_points()

    def _set_start_point(self, param):
        self.pvs['start_point']._val = float(param)
        self.get_points()
        
    def _set_end_point(self, param):
        self.pvs['end_point']._val = float(param)
        self.get_points()

    def _set_scan_go(self, param):
        if param:
            self.get_points()
        else:
            self.setpointSweepThread.clear_queue()
    
    def get_points(self):
        points, step = get_points(self.pvs['start_point']._val,  self.pvs['end_point']._val, self.pvs['n']._val)
        self.points = self.points={'setpoints':points}
        self.pvs['step'].set(step)
        
def get_points(start_point, end_point, n):
    rng = end_point - start_point
    step = rng / (n -1)
    points = []
    for i in range(n):
        points.append(float(round(start_point+i*step,10)))
    return points, float(step)
