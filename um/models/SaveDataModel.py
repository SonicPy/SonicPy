
import os.path, sys, math
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

from scipy import nanmean

import string

from os.path import expanduser

from epics import caput, caget, PV

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
                        'history_channel':
                                {'desc': '', 'val':'', 
                                'param':{'type':'s'}},
                        'filename':
                                {'desc': 'Filename', 'val':'', 
                                'param':{'type':'s'}},
                        'full_file_name':
                                {'desc': 'FullFileName', 'val':'', 
                                'param':{'type':'s'}, 'epics_PV_out':'16bmb:scope_file:FullFileName_RBV'},
                        'file_filter':
                                {'desc': 'Filename', 'val':'Text (*.csv);;Binary (*.npz)', 
                                'param':{'type':'s'}},
                        'file_extension':
                                {'desc': 'File type', 'val':self.extensions[0],'list':self.extensions, 
                                'param':{'type':'l'}},
                        'file_header':
                                {'desc': 'Header', 'val':{}, 
                                'param':{'type':'dict'}}, 
                        'save':     
                                {'desc': ';Save', 'val':False, 
                                'epics_PV_in':'16bmb:scope_file:WriteFile',
                                'epics_PV_out':'16bmb:scope_file:WriteFile',
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
                                'param':{'type':'dict'}},
                        'file_system_path':
                                {'desc': 'File system', 'val':'~', 
                                'param':{'type':'s'}},
                        'subdirectory':
                                {'desc': 'Subdirectory', 'val':'ultrasonic', 
                                'param':{'type':'s'}},
                        'base_name':
                                {'desc': 'Base name', 'val':'us_', 
                                'param':{'type':'s'}},
                        'path':
                                {'desc': 'Path', 'val':'', 
                                
                                'param':{'type':'s'}},
                        'path_exists':     
                                {'desc': 'Path exists;Yes/No', 'val':False, 
                                'param':{'type':'b'}}, 
                        'name':
                                {'desc': 'Last file', 'val':'', 
                                
                                'param':{'type':'s'}},
                        'format':
                                {'desc': '# format', 'val':'%3d', 
                                'param':{'type':'s'}},
                        'next_file_number': 
                                {'desc': 'Next file #', 'val':0,'min':0,'max':1e16,
                                'param':{ 'type':'i'}},
                        'latest_event':
                                {'desc': 'Status', 'val':'', 'epics_PV_out':'16bmb:scope_file:WriteMessage',
                                
                                'param':{'type':'s'}},

                      }       

        self.create_pvs(self.tasks)

        self.pvs['data_channel'].set('DPO5104:waveform')
        self.pvs['history_channel'].set('Waterfall:waveform_in')


        # these may get implemented in the future to be in line with area detector file saving workflow
        '''self.pvs_file ={'FilePath': None,
                        'FilePath_RBV': None,
                        'FileName': None,
                        'FileName_RBV': None,
                        'FullFileName_RBV': None,
                        'FileTemplate': None,
                        'FileTemplate_RBV': None,
                        'WriteMessage': None,
                        'FileNumber': None,
                        'FileNumber_RBV': None,
                        'AutoIncrement': None,
                        'AutoIncrement_RBV': None,
                        'WriteStatus': None,
                        'FilePathExists_RBV': None,
                        'AutoSave': None,
                        'AutoSave_RBV': None,
                        'WriteFile': None,
                        'WriteFile_RBV': None}'''


    
    #####################################################################
    #  Private set/get functions. Should not be used by external calls  #
    #####################################################################    

    def write_file(self, filename, params = {}):
        data = self.pv_server.get_pv(self.pvs['data_channel']._val)._val
        #print(data)
        
        
        if len(data):
            waveform  = data['waveform']
            x = waveform[0]
            y = waveform[1]
        
            '''R = 10

            pad_size = math.ceil(float(x.size)/R)*R - x.size

            x_padded = np.append(x, np.zeros(pad_size)*np.NaN)
            x = x_padded
            y_padded = np.append(y, np.zeros(pad_size)*np.NaN)
            y = y_padded

            x = x.reshape(-1, R)
            x = nanmean(x.reshape(-1,R), axis=1)
            y = y.reshape(-1, R)
            y = nanmean(y.reshape(-1,R), axis=1)
            '''
            path, fname = os.path.split(filename)

            '''subsample = np.arange(0,len(x),10)
            x = np.take(x, subsample)
            y = np.take(y, subsample)'''
            waveform = [x,y]

            success = False
            if filename.endswith('.csv'):
                fullname = os.path.expanduser(filename)
                try:
                    
                    write_tek_csv(fullname, waveform[0], waveform[1], params)
                    success = True
                except :
                    pass
                
            if filename.endswith('.npz'):
                try:
                    np.savez_compressed(fullname, waveform)
                    success = True
                except :
                    pass
            

            if success:
                filenumber = self.pvs['next_file_number']._val
                self.pvs['next_file_number'].set(filenumber+1)
                self.pvs['path'].set(str(path))
                self.pvs['name'].set(str(fname))
                self.pvs['full_file_name'].set(str(fullname))
                self.pvs['latest_event'].set('Wrote data to ' + str(fname))
                 
            else:
                self.pvs['latest_event'].set('Failed writing ' + str(fname))
            
            self.pvs['filename'].set(filename)
            history_pvname = self.pvs['history_channel']._val
            history_pv = self.pv_server.get_pv(history_pvname)
            waveform_out = {}
            waveform_out['filename']= filename
            waveform_out['waveform']= waveform
            history_pv.set(waveform_out)
            #print('set wafeform_in')
        else:
            self.pvs['latest_event'].set('No data to write')
        

    def _exit_task(self):
        pass

    def _set_path_exists(self, exists):
        self.pvs['path_exists']._val = exists
        

    def _get_path_exists(self):
        file_system_path = self.pvs['file_system_path']._val
        subdirectory = self.pvs['subdirectory']._val
        exists = self.check_if_folder_exists(file_system_path, subdirectory)
        return exists

    def _set_file_system_path(self, file_system_path):
        self.pvs['file_system_path']._val = file_system_path
        subdirectory = self.pvs['subdirectory']._val
        exists = self.check_if_folder_exists(file_system_path, subdirectory)
        self.pvs['path_exists'].set(exists)

    def _set_subdirectory(self, subdirectory):
        file_system_path = self.pvs['file_system_path']._val
        exists = self.check_if_folder_exists(file_system_path, subdirectory)
        self.pvs['path_exists'].set(exists)

    def check_if_folder_exists(self, file_system_path, subdirectory):
        if '~'in file_system_path:
            file_system_path = expanduser(file_system_path)
        fpath = os.path.join(file_system_path,subdirectory)
        exists = os.path.exists(fpath)
        #print('path_exists: '+ str(exists))
        return exists


    def _set_filename(self, filename):

        self.pvs['filename']._val =  filename
        if filename.endswith('.csv'):
            self.pvs['file_extension'].set('Text (*.csv)')
            
        if filename.endswith('.npz'):
            self.pvs['file_extension'].set('Binary (*.npz)')


    '''def saveFile(self, filename, params = {}):
        afg_pvs = self.afg_controller.model.pvs
        saved_filename = self.save_data_controller.save_data_callback(filename=filename, params=params)
        new_folder = os.path.dirname(str(saved_filename))
        old_folder = self.working_directories.savedata
        if new_folder != old_folder:
            self.working_directories.savedata = new_folder
            mcaUtil.save_folder_settings(self.working_directories, self.scope_working_directories_file)'''
    
    def _set_save(self, state):
        self.pvs['save']._val = state
        print('received save state: ' + str(state))
        if state:

            file_system_path = self.pvs['file_system_path']._val
            subdirectory = self.pvs['subdirectory']._val
            
            path = os.path.join(file_system_path,subdirectory)
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                try:
                    os.mkdir(path)
                except OSError:
                    self.pvs['latest_event'].set("Creation of the directory %s failed" % path)
                    
                    self.pvs['save'].set(False)
                    return
                else:
                    self.pvs['latest_event'].set("Successfully created the directory %s " % path)
                  

            base_name = self.pvs['base_name']._val
            next_file_number = self.pvs['next_file_number']._val
            extension = self.pvs['file_extension']._val
            #print(extension)

            if extension.endswith('.csv)'):
                ext = '.csv'
            if extension.endswith('.npz)'):
                ext = '.npz'

            form = self.pvs['format']._val 
            num_suffix = form%(next_file_number)
            num_suffix = num_suffix.replace(' ','0')

            filename = base_name+num_suffix+ext

            file_name = os.path.join(file_system_path,subdirectory, filename )

            if len(file_name):
                freq = None
                params = {}
                try:
                    freq = self.pv_server.get_pv('AFG3251:frequency')._val
                    params['AFG3251:frequency'] = {'val':freq, 'unit': 'Hz'}
                except:
                    pass

                self.write_file(file_name, params=params)
            print(self.pvs['save']._pv_name + ' save done')
            #self.pvs['save']._pv_name
            self.pvs['save'].set(False)
            

    
    def _set_file_extension(self, extension):
        if 'csv' in extension:
            self.pvs['file_filter'].set('Text (*.csv);;Binary (*.npz)')
            #print(self.file_filter)
        if 'npz' in extension:
            self.pvs['file_filter'].set('Binary (*.npz);;Text (*.csv)')
            #print(self.file_filter)


