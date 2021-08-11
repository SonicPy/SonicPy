
import os.path, sys
from utilities.utilities import *
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import numpy as np
from numpy import argmax, nan, greater,less, append, sort, array, argmin

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

class OverViewModel():
    def __init__(self):
        
        self.spectra = {}
        
        self.fp = ''
        self.fps_cond = {}
        self.fps_Hz = {}

        self.file_freq_dict = {}
        self.file_cond_dict = {}

        self.waterfalls = {} 
        self.folder_suffix = 'psi'
        self.file_type = '.csv'

        self.settings = {'scale':10,
                         'clip':True}

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
        if not freq in self.spectra:
            self.spectra[freq] = read_multiple_spectra_dict(fnames)

            self.waterfalls[freq] = WaterfallModel(freq)
            self.waterfalls[freq].settings =  self.settings
            self.waterfalls[freq].add_multiple_waveforms(self.spectra[freq])
            #self.waterfalls[freq].get_rescaled_waveforms()

        #print("Loaded " + str(len(fnames)) + " files in %s seconds." % (time.time() - start_time))

    def load_multiple_files_by_condition(self, cond):
        
        fnames = self.fps_cond[cond]
        start_time = time.time()
        if not cond in self.spectra:
            self.spectra[cond] = read_multiple_spectra_dict(fnames)

            self.waterfalls[cond] = WaterfallModel(cond)
            self.waterfalls[cond].settings =  self.settings
            self.waterfalls[cond].add_multiple_waveforms(self.spectra[cond])
            #self.waterfalls[cond].get_rescaled_waveforms()

        #print("Loaded " + str(len(fnames)) + " files in %s seconds." % (time.time() - start_time))


    def set_folder_path(self, folder):
        # All files ending with .txt
        self.fp = folder
        self.understand_folder_structure()
        

    def understand_folder_structure(self):
        folder_suffix = self.folder_suffix
        folder = self.fp
        file_type = self.file_type
        conditions_search = os.path.join(folder,'*'+folder_suffix)
        conditions = glob.glob(conditions_search)
        
        conditions_base = []
        suffix = os.path.basename(conditions[0])[-3:]
        for p in conditions:
            try:
                num = int(os.path.basename(p)[:-3])
                conditions_base.append(num)
            except:
                pass
        conditions_num = sorted(conditions_base)
        conditions_folders_sorted = []
        for p in conditions_num:
            conditions_folders_sorted.append(str(p)+suffix)

        condition_0 = conditions_folders_sorted[0]
        freq_search = os.path.join(folder,condition_0,'*'+file_type)
        freqs = glob.glob(freq_search) 

        freqs_base = []
        
        suffix_freq = freqs[0].split('_')[-1][-4:]
        for p in freqs:
            num = p.split('_')[-1][:-4]
            freqs_base.append(num)
        freqs_sorted = sorted(freqs_base)
 
        for p in conditions_folders_sorted:
            conditions_search = os.path.join(folder,p,'*'+suffix_freq)
            res = sorted(glob.glob(conditions_search))
            self.fps_cond[p] = res
            for r in res:
                self.file_cond_dict[r]=p
      
        for f in freqs_sorted:
            p_list = []
            for p in conditions_folders_sorted:

                freq_search = os.path.join(folder,p,'*'+f+suffix_freq)
                res = glob.glob(freq_search)
                if len(res):
                    p_list.append(res[0])
                else:
                    p_list.append(None)
            self.fps_Hz[f] = p_list
            for p in p_list:
                self.file_freq_dict[p]=f

        print('found conditions: '+str(conditions_folders_sorted))
        print('found frequencies: '+str(freqs_sorted))



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

