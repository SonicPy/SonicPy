
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
from utilities.utilities import zero_phase_bandpass_filter, read_tek_csv, \
                                read_multiple_spectra, zero_phase_highpass_filter, \
                                zero_phase_bandstop_filter, zero_phase_lowpass_filter

from ua.models.WaterfallModel import WaterfallModel
import json
import glob
import time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject

# Python program to sort a list of
# tuples by the second Item using sort()

# Function to sort hte list by second item of tuple
def Sort_Tuple(tup):

    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of
    # sublist lambda has been used
    tup.sort(key = lambda x: x[1])
    return tup

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
    def __init__(self):
        
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
        self.file_type = '.csv'

        self.settings = {'scale':10,
                         'clip':True}

        self.conditions_folders_sorted = []

    def add_echoes(self, correlation):
        filename_waweform = correlation['filename_waweform']
        bounds = correlation['echo_bounds']
        wave_type = correlation['wave_type']

        freq_cond = self.file_dict[filename_waweform]



        freq = freq_cond[1]
        freq_waterfall = self.waterfalls[freq]
        cond = freq_cond[0]
        cond_waterfall = self.waterfalls[cond]

        freq_waterfall.echoes[wave_type][filename_waweform]=bounds
        cond_waterfall.echoes[wave_type][filename_waweform]=bounds
     

    def clear(self):
        self.__init__()

    def set_scale(self, scale):

        for key in self.waterfalls:
            w = self.waterfalls[key]
            w.settings['scale']=scale

    def set_clip(self, clip):

        for key in self.waterfalls:
            w = self.waterfalls[key]
            w.settings['clip']=clip

    def load_multiple_files_by_frequency(self, freq):
        
        fnames = self.fps_Hz[freq]
        start_time = time.time()
        conditions = list(self.fps_cond.keys())
        
        if not freq in self.spectra:
            loaded_files = {}
          
            #read_files = read_multiple_spectra_dict(fnames) #old
            
            read_files = self.file_server.get_waveforms(fnames) #new, replaced old
            
            for condition in conditions:
                for loaded_fname in read_files:
                    path = loaded_fname['filename']
                    fldr = path.split(os.sep)[-2] # this is the pt condition name
                    if fldr == condition:
                        loaded_files[condition]= loaded_fname
                        break
                if not condition in loaded_files:
                    loaded_files[condition] = {'filename':'','waveform':[np.asarray([0]),np.asarray([0])]}

            self.spectra[freq] = loaded_files

            self.waterfalls[freq] = WaterfallModel(freq)
            self.waterfalls[freq].settings =  self.settings

            self.waterfalls[freq].add_multiple_waveforms(self.spectra[freq])
            #self.waterfalls[freq].get_rescaled_waveforms()

            #print("Loaded " + str(len(fnames)) + " files in %s seconds." % (time.time() - start_time))

    def load_multiple_files_by_condition(self, cond):
        
        fnames = self.fps_cond[cond]
        frequencies = list(self.fps_Hz.keys())
        if len(fnames):
            
            if not cond in self.spectra:
                loaded_files = {}
                
                read_files = self.file_server.get_waveforms(fnames)
                
                res = read_files[0]['filename']
                first_num = res[-1*(len('.csv')+3):-1*len('.csv')]
                for frequency in frequencies:
                    for loaded_fname in read_files:
                        path = loaded_fname['filename']

                        f = int(path[-1*(len('.csv')+3):-1*len('.csv')]) - int(first_num)
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
                

                

            #print("Loaded " + str(len(fnames)) + " files in %s seconds." % (time.time() - start_time))


    def set_folder_path(self, folder):
        # All files ending with .txt
        
        self.fp = folder
        self.understand_folder_structure()
        

    
    def get_conditions_folders(self):

      
        folder = self.fp
        file_type = self.file_type
        subfolders = glob.glob(os.path.join(folder,'*/'), recursive = False)

        #return subfolders.sort()
        conditions_folders_sorted = []

        if len(subfolders):
            sf = {} # dict {folder:[files]}
            tm = [] # list [(folder,timestamp)]

            # determine whether to use getmtime or getctime (some Windows file systems will switch modified time and the created time for a file)
            # sometimes all time stamps get screwed up and files have to be sorted anothe way or manually

            subfolder = subfolders[0]
            file_search_str = os.path.join(subfolder,'*' + file_type)
            files_in_subfolder = glob.glob(file_search_str, recursive = False)
            time_m = os. path. getmtime(files_in_subfolder[0])
            time_c = os. path. getctime(files_in_subfolder[0])

            if time_m < time_c:
                time_func = os. path. getmtime
            else:
                time_func = os. path. getctime



            for subfolder in subfolders:
                path = os.path.normpath(subfolder)
                fldr = path.split(os.sep)[-1]
                file_search_str = os.path.join(subfolder,'*' + file_type)
                files_in_subfolder = glob.glob(file_search_str, recursive = False)
                

                sf[fldr] = files_in_subfolder
                time_modified = time_func(files_in_subfolder[0])
                tm.append ((fldr, time_modified))
            tm = Sort_Tuple(tm)
            
            for t in tm:
                conditions_folders_sorted.append(t[0])

        #print(conditions_folders_sorted)

        return conditions_folders_sorted
            #print("conditions_num : %s seconds." % (time.time() - start_time))

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


        #print("freqs_sorted : %s seconds." % (time.time() - start_time))
        start_time = time.time()
        for p in conditions_folders_sorted:
            
            conditions_search = os.path.join(folder,p,'*'+suffix_freq)
            res = sorted(glob.glob(conditions_search))[:len(freqs_sorted)]
        
            self.fps_cond[p] = res
            first_num = res[0][-1*(len(file_type)+3):-1*len(file_type)]
            for i, r in enumerate(res):
                
                f = int(r[-1*(len(file_type)+3):-1*len(file_type)]) - int(first_num)
                f_num = f'{f:03d}' 
                
                self.file_dict[r]=(p,f_num)

                if f_num in self.fps_Hz:
                    p_list = self.fps_Hz[f_num]
                else:
                    p_list = []
                
                p_list.append(r)
                self.fps_Hz[f_num] = p_list

        print("file_cond_dict : %s seconds." % (time.time() - start_time))

    def get_frequencies_sorted(self):
        conditions_folders_sorted = self.conditions_folders_sorted
        folder = self.fp
        file_type = self.file_type

        condition_0 = conditions_folders_sorted[0]
        freq_search = os.path.join(folder,condition_0,'*'+file_type)
        freqs = glob.glob(freq_search) 

        freqs_base = []
        for p in freqs:
            num = p[-1*(len(file_type)+3):-1*len(file_type)]
            freqs_base.append(num)
        freqs_sorted = sorted(freqs_base)
        return freqs_sorted

    def understand_folder_structure(self):
        

        self.conditions_folders_sorted = self.get_conditions_folders()

        self.frequencies_sorted = self.get_frequencies_sorted()

        rows = len(self.conditions_folders_sorted)
        cols = len (self.frequencies_sorted)
        self.files =  [['' for i in range(cols)] for j in range(rows)]

        if len(self.conditions_folders_sorted) and len(self.frequencies_sorted):
            self.waveforms_3d_array = np.zeros((len(self.conditions_folders_sorted),len(self.frequencies_sorted),2,10000))
    
        if len(self.conditions_folders_sorted):
            self.create_file_dicts()
    
    def condition_index(self,condition):
        return self.conditions_folders_sorted.index(condition)

    def frequency_index(self,frequency):
        return self.frequencies_sorted.index(frequency)

    def add_result_from_file(self, filename):
        data = self.read_result_file(filename)
        self.add_freq(data)


    def clear(self):
        self.__init__()


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

