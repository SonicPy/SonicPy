
from argparse import FileType
import enum
import os.path, sys
from utilities.utilities import *
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import numpy as np
from numpy import argmax, c_, nan, greater,less, append, sort, array, argmin

from scipy import optimize
from scipy.signal import argrelextrema, tukey
from functools import partial
from um.models.tek_fileIO import *
from scipy import signal
import pyqtgraph as pg
from utilities.utilities import zero_phase_bandpass_filter,  \
                                 zero_phase_highpass_filter, \
                                zero_phase_bandstop_filter, zero_phase_lowpass_filter

from ua.models.WaterfallModel import WaterfallModel
import json
import glob
import time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject
from natsort import natsorted 

from ua.models.EchoesResultsModel import EchoesResultsModel
 
# Python program to sort a list of
# tuples by the second Item using sort()

# Function to sort hte list by second item of tuple
def Sort_Tuple(list, element = 1):

    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of
    # sublist lambda has been used
    list.sort(key = lambda x: x[element])
    return list

class FileServer():
    def __init__(self):
        
        self.files = {}
    
    def get_waveforms(self, files):
        output = []
        read_files = []
        for f in files:
            if f in self.files:
                pass
                #waveforms.append(self.files[f])
            else:
                read_files.append(f)
    
        if len(read_files):
            read_files = read_2D_spectra_dict(read_files)
            for rf in read_files:
                fname = rf['filename']
                waveform = rf['waveform']
                self.files[fname]=waveform
        
        for f in files:
            output.append({'filename':f,'waveform':self.files[f]})
        return output

class OverViewModel():
    def __init__(self, results_model: EchoesResultsModel):
        
        self.results_model = results_model

        self.f_start = 15
        self.f_step = 2

        self.spectra = {}

        self.file_server = FileServer()

        self.waveforms = None
        self.files = [[]]
        
        self.fp = ''
        self.fps_cond = {}
        self.fps_Hz = {}

        self.file_dict = {}

        self.waterfalls = {} 
        self.folder_suffix = 'psi'
        self.file_type = ''

        self.settings = {'scale':10,
                         'clip':True}

        self.conditions_folders_sorted = []

        self.echoes_p = {}
        self.echoes_s = {}

    def add_echoes(self, correlation):
        filename_waveform = correlation['filename_waveform']
        bounds = correlation['echo_bounds']
        wave_type = correlation['wave_type']

   

        # i was here
        '''freq_waterfall.set_echoe(filename_waveform ,wave_type, bounds)
        
        cond_waterfall.set_echoe(filename_waveform ,wave_type, bounds)'''

        self.set_echoes(filename_waveform ,wave_type, bounds)

    def del_echoes(self, condition, wave_type, freq):
        str_ind_freq = f'{self.freq_val_to_ind(freq):03d}' 
        fname = self.spectra[condition][str_ind_freq]['filename']
        if wave_type == 'P':
            del self.echoes_p[fname] 
            

        elif wave_type == 'S':
            del self.echoes_s[fname] 

        waterfall = self.waterfalls[str_ind_freq]
        waterfall.del_echoe(fname, wave_type)
        waterfall = self.waterfalls[condition]
        waterfall.del_echoe(fname, wave_type)

    def freq_val_to_ind(self, freq):
        ind = None
        freqs = list(self.fps_Hz.keys())
        f_start = self.f_start
        f_step = self.f_step
        freqs_vals = []
        for freq_ind in range(len(freqs)):
            freq_val = (f_start + freq_ind * f_step) * 1e6
            freqs_vals.append(freq_val)
        if freq in freqs_vals:
            ind = freqs_vals.index(freq)
        return ind

        
    def set_echoes(self, fname, wave_type, echoes_bounds):
        # echoes_bounds = list, [[0.0,0.0],[0.0,0.0]] (values are in seconds)
        # echoes_bounds[0]: P bounds
        # echoes_bounds[0]: S bounds
        if wave_type == 'P':
            self.echoes_p[fname] = echoes_bounds

        elif wave_type == 'S':
            self.echoes_s[fname] = echoes_bounds

    def clear(self):
        self.__init__(self.results_model)

    def set_scale(self, scale):

        for key in self.waterfalls:
            w = self.waterfalls[key]
            w.settings['scale']=scale

    def set_clip(self, clip):

        for key in self.waterfalls:
            w = self.waterfalls[key]
            w.settings['clip']=clip

    def load_multiple_files_by_frequency(self, freq):
        conditions = self.conditions_folders_sorted # list(self.fps_cond.keys())
        fnames = []
        for c in conditions:
            fname_list = self.fps_cond[c]
            if freq in fname_list:
                fname = fname_list[freq]
            else:
                fname = ''
            fnames.append(fname)
        start_time = time.time()
        
        
        if 1: #not freq in self.spectra:
            loaded_files = {}
          
            #read_files = read_multiple_spectra_dict(fnames) #old
            
            read_files = self.file_server.get_waveforms(fnames) #new, replaced old
            
            for condition in conditions:
                for loaded_fname in read_files:
                    path = loaded_fname['filename']
                    if path == '':
                        continue
                    fldr = path.split(os.sep)[-2] # this is the pt condition name
                    if fldr == condition:
                        loaded_files[condition]= loaded_fname
                        break
                if not condition in loaded_files:
                    loaded_files[condition] = {'filename':'','waveform':[np.asarray([0]),np.asarray([0])]}

            self.spectra[freq] = loaded_files
        if not freq in self.waterfalls:

            self.waterfalls[freq] = WaterfallModel(freq)
            self.waterfalls[freq].settings =  self.settings

            self.waterfalls[freq].add_multiple_waveforms(self.spectra[freq])
        else:
            fnames = []
            for cond in self.spectra[freq]:
                fnames.append(self.spectra[freq][cond]['filename'])
            waterfall = self.waterfalls[freq]
            waterfall.re_order_files(fnames)
        

          
    def load_multiple_files_by_condition(self, cond):
        
        fname_dict = self.fps_cond[cond]
        fnames = []
        for f in fname_dict:
            fnames.append(fname_dict[f])
        frequencies = list(self.fps_Hz.keys())
        if len(fnames):
            
            if not cond in self.spectra:
                loaded_files = {}
                read_files = self.file_server.get_waveforms(fnames)
                
                for frequency in frequencies:
                    for i, loaded_fname in enumerate(read_files):
                     
                        f = i
                        f_num = f'{f:03d}' 

                        if f_num == frequency:
                            loaded_files[frequency]= loaded_fname
                            break
                    if not frequency in loaded_files:
                        loaded_files[frequency] = {'filename':'','waveform':[np.asarray([0]),np.asarray([0])]}

                self.spectra[cond] = loaded_files
                self.waterfalls[cond] = WaterfallModel(cond)
                self.waterfalls[cond].settings =  self.settings
                self.waterfalls[cond].add_multiple_waveforms(self.spectra[cond])
                


    def set_folder_path(self, folder):
        
        exists = os.path.isdir(folder)
        
        if exists:
            self.fp = folder
            settings_file =  os.path.join(folder, 'settings.json')

            settings_exist = os.path.isfile(settings_file)
            if settings_exist:
                settings = self.read_result_file(settings_file)
                print(settings)

            self.understand_folder_structure()
        

    
    def get_conditions_folders(self, folder):
        '''
        returns list of naturally sorted conditions folders in folder
        '''
        
        subfolders = glob.glob(os.path.join(folder,'*/'), recursive = False)
        conditions_folders_sorted = []

        if len(subfolders):
            folder_norm = []

            for subfolder in subfolders:
                path = os.path.normpath(subfolder)
                fldr = path.split(os.sep)[-1]
                folder_norm.append(fldr)
            conditions_folders_sorted = natsorted(folder_norm)
            
        return conditions_folders_sorted


    def create_file_dicts(self):

        conditions_folders_sorted = self.conditions_folders_sorted
        self.fps_cond = {}
        self.file_dict = {}
        self.fps_Hz = {}

        start_time = time.time()
     
        folder = self.fp
        file_type = self.file_type

        condition_0 = conditions_folders_sorted[0]
        freq_search = os.path.join(folder,condition_0,'*'+file_type)
        freqs = glob.glob(freq_search) 

     
        suffix_freq = freqs[0].split('_')[-1][-4:]
        
        freqs_sorted = self.frequencies_sorted


        start_time = time.time()
        for p in conditions_folders_sorted:
            
            conditions_search = os.path.join(folder,p,'*'+suffix_freq)
            res = natsorted(glob.glob(conditions_search)) [:len(freqs_sorted)]

            r_list = {}
            for i, r in enumerate(res):
                f_num = f'{i:03d}' 
                r_list[f_num]= r
        
            self.fps_cond[p] = r_list
            
            for i, r in enumerate(res):
                
                
                f_num = f'{i:03d}' 
                
                self.file_dict[r]=(p,f_num)

                if f_num in self.fps_Hz:
                    p_list = self.fps_Hz[f_num]
                else:
                    p_list = []
                
                p_list.append(r)
                self.fps_Hz[f_num] = p_list


    def get_frequencies_sorted(self):
        conditions_folders_sorted = self.conditions_folders_sorted
        folder = self.fp
        file_type = self.file_type

        condition_0 = conditions_folders_sorted[0]
        freq_search = os.path.join(folder,condition_0,'*'+file_type)
        freqs = glob.glob(freq_search) 
        files = []
        for freq in freqs:
            file = os.path.split(freq)[-1]
            files.append(file)

        files = natsorted(files)

        freqs_base = []
        for i, p in enumerate(files):
            num = f'{i:03d}'
            freqs_base.append(num)
        freqs_sorted = natsorted(freqs_base)
        return freqs_sorted

    def get_file_types_in_folder(self, folder):
        '''
        gets number of file types in folder
        returns a dict {'type':###}
        '''
        conditions_search = os.path.join(folder,'*')
        res = glob.glob(conditions_search)
        types = {}
        for r in res:
            if '.' in r:
                ext = '.' + r.split('.')[-1]

            else:
                ext = ''

            if not ext in types:
                types[ext]= 1
            else:
                i = types[ext]
                types[ext] = i+1
         
        return types

    def get_extension(self ):
        '''
        get extension by searching the first folder and determining the most common file type: '.csv', '', etc..
        '''
        folder = self.fp
        condition_0 = self.conditions_folders_sorted[0]
        first_folder = os.path.join(folder,condition_0)
        types = self.get_file_types_in_folder(first_folder)
        extensions = []
        for t in types:
            extensions.append((t,types[t]))
        extensions = Sort_Tuple(extensions)
        ext = extensions[0][0]
        return ext


    def understand_folder_structure(self):
        
        folder = self.fp
        self.conditions_folders_sorted = self.get_conditions_folders(folder)

        self.file_type =  self.get_extension()

        self.frequencies_sorted = self.get_frequencies_sorted()

        if len(self.conditions_folders_sorted):
            self.create_file_dicts()
    
    def condition_index(self,condition):
        return self.conditions_folders_sorted.index(condition)

    def frequency_index(self,frequency):
        return self.frequencies_sorted.index(frequency)

    def add_result_from_file(self, filename):
        data = self.read_result_file(filename)
        self.add_freq(data)





    def read_result_file(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)

        return data


 
 
    def save_result(self, filename):
        
        data = {'frequency':self.freq,'minima_t':list(self.minima[0]),'minima':list(self.minima[1]), 
                            'maxima_t':list(self.maxima[0]),'maxima':list(self.maxima[1])}
        
        if filename.endswith('.json'):
            with open(filename, 'w') as json_file:
                json.dump(data, json_file,indent = 2)    

