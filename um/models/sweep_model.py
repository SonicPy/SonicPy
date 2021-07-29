
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
                                'param':{'type':'i'}},
                        'current_setpoint': 
                                {'desc': 'Current set-point', 'val':0., 'increment':0.1, 'min':-10e11,'max':10e11,
                                'param':{'type':'f'}},
                        'setpoints':     
                                {'desc': 'Setpoints', 'val':None, 
                                'param':{'type':'dict'}},
                        'run_state':     
                                {'desc': 'Run;ON/OFF', 'val':False, 
                                'param':{'type':'b'}},
                        'start_scan':     
                                {'desc': '', 'val':False, 
                                'param':{'type':'b'}},
                        'advance_to_next':     
                                {'desc': '', 'val':False, 
                                'param':{'type':'b'}},
                        'acquire':     
                                {'desc': '', 'val':False, 
                                'param':{'type':'b'}},
                        'do_point':     
                                {'desc': '', 'val':False, 
                                'param':{'type':'b'}},
                        'detector_done':     
                                {'desc': '', 'val':False, 
                                'param':{'type':'b'}},
                        'detector_trigger':     
                                {'desc': '', 'val':False, 
                                'param':{'type':'b'}},
                        'positioner_done':     
                                {'desc': '', 'val':False, 
                                'param':{'type':'b'}},
                        'move_positioner':     
                                {'desc': '', 'val':False, 
                                'param':{'type':'b'}},
                        
                        'save_data_set_trigger':     
                                {'desc': '', 'val':False, 
                                'param':{'type':'b'}},
                        'save_data':     
                                {'desc': '', 'val':False, 
                                'param':{'type':'b'}},
                        'save_data_done':     
                                {'desc': '', 'val':False, 
                                'param':{'type':'b'}},
                        'positioner_settling_time': 
                                {'desc': 'Positioner settling time', 'val':0.1, 'increment':0.1, 'min':0,'max':1000,
                                'param':{'type':'f'}},
                        'detector_settling_time': 
                                {'desc': 'Detector settling time', 'val':0., 'increment':0.1, 'min':0,'max':1000,
                                'param':{'type':'f'}},
                        'save_data_settling_time': 
                                {'desc': 'Save data settling time', 'val':0., 'increment':0.1, 'min':0,'max':1000,
                                'param':{'type':'f'}},

                                }
        self.create_pvs(self.tasks)

    ### initialize scan
        
    def _set_setpoints(self, param):
        #print('_set_setpoints '+str(param))
        self.pvs['setpoints']._val = param

    ### scan starts here
    ### parent thread starts the scan be setting 'run_state' to True
    ### scan can be interrupted/stopped by setting 'run_state to False at any time
    ### after all points in scan are done the 'run_state' resets to False by itself

    def _set_run_state(self, param):
        currently_running = self.pvs['run_state']._val
        self.pvs['run_state']._val = param
        if param:
            if not currently_running:  
                self.pvs['start_scan'].set(True)
                #print('point sweep starting')
        else:
            self.parent.pvs['scan_go'].set(False)
            #print('point sweep done')

    def _set_start_scan(self, param):
        self.pvs['current_setpoint_index'].set(0)
        self.pvs['start_scan']._val = param
        if param:
            self.pvs['do_point'].set(True)

    def _set_current_setpoint_index(self, param):
        self.pvs['current_setpoint_index']._val = param
        #print('setpoint index: '+str(param))

    #############################
    # start doing a setpoint
    #############################

    def _set_do_point(self, param):
        pts = self.pvs['setpoints']._val['setpoints']
        index = self.pvs['current_setpoint_index']._val
        
        if len (pts):
            p = pts[index]
            self.pvs['current_setpoint'].set(p)
            
        else:
            self.pvs['run_state'].set(False)


    #############################
    # positioner
    #############################

    def _set_current_setpoint(self, param):
        self.pvs['current_setpoint']._val = param
        positioner_pvname = self.parent.pvs['positioner_read_channel']._val
        positioner_pv = self.pv_server.get_pv(positioner_pvname)
        positioner_pv.value_changed_signal.connect(self.wait_for_positioner_done)
        self.pvs['move_positioner'].set(True)

    def _set_move_positioner(self, param):
        if param:
            p = self.pvs['current_setpoint']._val
            positioner_pvname = self.parent.pvs['positioner_set_channel']._val
            positioner_pv = self.pv_server.get_pv(positioner_pvname)
            positioner_pv.set(p*1e6)

    def wait_for_positioner_done(self, pv, param):
        positioner_pvname = self.parent.pvs['positioner_read_channel']._val
        positioner_pv = self.pv_server.get_pv(positioner_pvname)
        positioner_pv.value_changed_signal.disconnect(self.wait_for_positioner_done)
        
        settling_time = self.pvs['positioner_settling_time']._val
        time.sleep(settling_time)
        self.pvs['positioner_done'].set(True)

    def _set_positioner_done(self, param):
        run_state = self.pvs['run_state']._val
        if run_state:
            self.pvs['detector_trigger'].set(True)

    

    #############################
    # detector
    #############################

    def _set_detector_trigger(self, param):
        detector_pvname = self.parent.pvs['det_run_state_channel']._val
        detector_pv = self.pv_server.get_pv(detector_pvname)
        detector_pv.value_changed_signal.connect(self.wait_for_detector_done)
        self.pvs['acquire'].set(True)


    def _set_acquire(self, param):
        if param:
            detector_pvname = self.parent.pvs['det_trigger_channel']._val
            detector_pv = self.pv_server.get_pv(detector_pvname)
            detector_pv.set(True)

    def wait_for_detector_done(self, pv, param):
        param = param[0]
        if not param:
            detector_pvname = self.parent.pvs['det_run_state_channel']._val
            detector_pv = self.pv_server.get_pv(detector_pvname)
            detector_pv.value_changed_signal.disconnect(self.wait_for_detector_done)
            #print('detector done')
            settling_time = self.pvs['detector_settling_time']._val
            time.sleep(settling_time)
            self.pvs['detector_done'].set(True)

    def _set_detector_done(self, param):
        
        # do something with the acquire point, here we just trigger save_data
        run_state = self.pvs['run_state']._val
        if run_state:
            self.pvs['save_data_set_trigger'].set(True)

    #############################
    # save data
    #############################

    def _set_save_data_set_trigger(self, param):
        save_data_pvname = self.parent.pvs['save_data_read_channel']._val
        save_data_pv = self.pv_server.get_pv(save_data_pvname)
        save_data_pv.value_changed_signal.connect(self.wait_for_save_data_done)
        self.pvs['save_data'].set(True)

    def _set_save_data(self, param):
        if param:
            save_data_pvname = self.parent.pvs['save_data_set_channel']._val
            save_data_pv = self.pv_server.get_pv(save_data_pvname)
            save_data_pv.set(True)

    def wait_for_save_data_done(self, pv, param):
        param = param[0]
        print(param)
        if not param:
            save_data_pvname = self.parent.pvs['save_data_read_channel']._val
            save_data_pv = self.pv_server.get_pv(save_data_pvname)
            save_data_pv.value_changed_signal.disconnect(self.wait_for_save_data_done)
            #print('save data done')
            settling_time = self.pvs['save_data_settling_time']._val
            time.sleep(settling_time)
            
            self.pvs['save_data_done'].set(True)

    def _set_save_data_done(self, param):
       
        # go to next point if run_state is still True
        run_state = self.pvs['run_state']._val
        if run_state:
            self.pvs['advance_to_next'].set(True)

    #############################
    # advance to nect or end
    #############################

    def _set_advance_to_next(self, param):
        pts = self.pvs['setpoints']._val['setpoints']
        index = self.pvs['current_setpoint_index']._val
        
        if len(pts)>index+1:
            #print('advancing to next index: ' + str(index+1))
            self.pvs['current_setpoint_index'].set(index+1)
            self.pvs['do_point'].set(True)
        else:
            self.pvs['run_state'].set(False)
        


        
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
                                {'desc': 'Detector set', 'val':'DPO5104:erase_start', 
                                'param':{ 'type':'s'}},
                        'det_run_state_channel':
                                {'desc': 'Detector read', 'val':'DPO5104:run_state', 
                                'param':{ 'type':'s'}},
                        'positioner_set_channel':     
                                {'desc': 'Position set', 'val':'burst_fixed_time:freq', 
                                'param':{ 'type':'s'}},
                        'positioner_read_channel':     
                                {'desc': 'Position read', 'val':'AFG3251:frequency', 
                                'param':{ 'type':'s'}},
                        'save_data_set_channel':     
                                {'desc': 'Save data set', 'val':'SaveData:save', 
                                'param':{ 'type':'s'}},
                        'save_data_read_channel':     
                                {'desc': 'Save data read', 'val':'SaveData:save', 
                                'param':{ 'type':'s'}},
                        'start_point': 
                                {'desc': 'Start', 'val':10.0, 'increment':0.5,'min':.001,'max':110 ,
                                'param':{ 'type':'f'}},
                        'end_point': 
                                {'desc': 'End', 'val':40.0, 'increment':0.5, 'min':.002,'max':120,
                                'param':{ 'type':'f'}},
                        'n': 
                                {'desc': '#Pts', 'val':6,'min':2,'max':10000,
                                'param':{ 'type':'i'}},
                        'current_point': 
                                {'desc': 'Set-point index', 'val':0,'min':0,'max':10000,
                                'methods':{'set':False, 'get':True},  
                                'param':{ 'type':'i'}},
                        'step': 
                                {'desc': 'Step size', 'val':1.0, 'min':0.001,'max':110,'increment':.1,
                                'methods':{'set':False, 'get':True},  
                                'param':{ 'type':'f'}},
                        'scan_go':     
                                {'desc': 'Scan;Go', 'val':False, 
                                'param':{ 'type':'b'}},
                        'scan_stop':     
                                {'desc': 'Scan;Stop', 'val':False, 
                                'param':{ 'type':'b'}},
                        'scan_pause':     
                                {'desc': 'Scan;Stop', 'val':False, 
                                'param':{ 'type':'b'}},
                        'setpoint': 
                                {'desc': 'Set-point', 'val':30., 'increment':0.1, 'min':0.1,'max':100,
                                'param':{ 'type':'f'}}
                                }

        self.create_pvs(self.tasks)
        self.offline = True
        self.points = {'setpoints':[]}

        self.setpointSweepThread.pvs['run_state'].value_changed_signal.connect(self.scan_done_callback)
        self.setpointSweepThread.pvs['current_setpoint_index'].value_changed_signal.connect(self.current_setpoint_index_callback)
   
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
            #print('scan_go: False')
            self.pvs['scan_go'].set(False)

    def current_setpoint_index_callback(self, pv, data):
        ind = data[0]
        self.pvs['current_point'].set(ind+1)
        current_setpoint = self.setpointSweepThread.pvs['current_setpoint']._val
        self.pvs['setpoint'].set(current_setpoint)

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
