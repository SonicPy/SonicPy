
from argparse import FileType
import enum
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

        

    def add_echoes(self, correlation):
        filename_waweform = correlation['filename_waweform']
        bounds = correlation['echo_bounds']
        wave_type = correlation['wave_type']

        freq = self.file_freq_dict[filename_waweform]
        freq_waterfall = self.waterfalls[freq]
        cond = self.file_cond_dict[filename_waweform]
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
        if not freq in self.spectra:
            self.spectra[freq] = read_multiple_spectra_dict(fnames)

            self.waterfalls[freq] = WaterfallModel(freq)
            self.waterfalls[freq].settings =  self.settings
            self.waterfalls[freq].add_multiple_waveforms(self.spectra[freq])
            #self.waterfalls[freq].get_rescaled_waveforms()

        #print("Loaded " + str(len(fnames)) + " files in %s seconds." % (time.time() - start_time))

    def load_multiple_files_by_condition(self, cond):
        
        fnames = self.fps_cond[cond]
        if len(fnames):
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
        

        start_time = time.time()
     

        folder_suffix = self.folder_suffix
        folder = self.fp
        file_type = self.file_type
        subfolders = glob.glob(os.path.join(folder,'*/'), recursive = False)
        sf = {} # dict {folder:[files]}
        tm = [] # list [(folder,timestamp)]
        for subfolder in subfolders:
            path = os.path.normpath(subfolder)
            fldr = path.split(os.sep)[-1]
            file_search_str = os.path.join(subfolder,'*' + file_type)
            files_in_subfolder = glob.glob(file_search_str, recursive = False)
            

            sf[fldr] = files_in_subfolder
            time_modified = os. path. getmtime(files_in_subfolder[0])
            tm.append ((fldr, time_modified))
        tm = Sort_Tuple(tm)
        conditions_folders_sorted = []
        for t in tm:
            conditions_folders_sorted.append(t[0])

        '''conditions_search = os.path.join(folder,'*'+folder_suffix)
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
        #print("conditions_num : %s seconds." % (time.time() - start_time))
        start_time = time.time()
        for p in conditions_num:
            conditions_folders_sorted.append(str(p)+suffix)'''


        condition_0 = conditions_folders_sorted[0]
        freq_search = os.path.join(folder,condition_0,'*'+file_type)
        freqs = glob.glob(freq_search) 

        freqs_base = []
        
        suffix_freq = freqs[0].split('_')[-1][-4:]
        for p in freqs:
            num = p[-1*(len(file_type)+3):-1*len(file_type)]
            freqs_base.append(num)
        freqs_sorted = sorted(freqs_base)
        #print("freqs_sorted : %s seconds." % (time.time() - start_time))
        start_time = time.time()
        for p in conditions_folders_sorted:
            conditions_search = os.path.join(folder,p,'*'+suffix_freq)
            res = sorted(glob.glob(conditions_search))
            self.fps_cond[p] = res
            for r in res:
                self.file_cond_dict[r]=p
        #print("file_cond_dict : %s seconds." % (time.time() - start_time))
        start_time = time.time()

        nfiles = len(freqs_sorted)*len(conditions_folders_sorted)
        progress_dialog = QtWidgets.QProgressDialog("Loading multiple waveforms.", "Abort Loading", 0, nfiles, None)
        progress_dialog.setMinimumWidth(300)
        progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        progress_dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        progress_dialog.show()
        QtWidgets.QApplication.processEvents()

        for m, f in enumerate(freqs_sorted):
            p_list = []
            for n, p in enumerate(conditions_folders_sorted):
                d = n + m * len (conditions_folders_sorted)
                if d % 2 == 0:
                    #update progress bar only every 2 files to save time
                    progress_dialog.setValue(d)
                    QtWidgets.QApplication.processEvents()
                freq_search = os.path.join(folder,p,'*'+f+suffix_freq)
                res = glob.glob(freq_search)
                if len(res):
                    p_list.append(res[0])
                else:
                    p_list.append(None)
                if progress_dialog.wasCanceled():
                    break
            self.fps_Hz[f] = p_list
            
            for p in p_list:
                self.file_freq_dict[p]=f
            if progress_dialog.wasCanceled():
                    break
        #print("file_freq_dict : %s seconds." % (time.time() - start_time))
        
        #print('found conditions: '+str(conditions_folders_sorted))
        #print('found frequencies: '+str(freqs_sorted))

        progress_dialog.close()
        QtWidgets.QApplication.processEvents()

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

