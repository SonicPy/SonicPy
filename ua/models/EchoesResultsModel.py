
from argparse import FileType
import enum
from importlib.machinery import FileFinder
import os.path, sys
from turtle import update
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

#from ua.models.WaterfallModel import WaterfallModel
import json
import glob
import time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject
from natsort import natsorted 
 
import shutil



class EchoesResultsModel():
    def __init__(self):
        
        self.subfolders = []
        self.folder = ''
        self.echoes_p = {}
        self.echoes_s = {}


        '''self.sorted_correlations_p = {}
        self.sorted_correlations_s = {}'''

    def add_echoe(self, correlation):
        
        wave_type = correlation['wave_type']
        if wave_type == "P":
            if correlation['filename_waveform'] in self.echoes_p:
                correlations = self.echoes_p[correlation['filename_waveform']]
            else:
                correlations = []
            correlations.append(correlation)
            self.echoes_p[correlation['filename_waveform']] = correlations
        elif wave_type == "S":

            if correlation['filename_waveform'] in self.echoes_s:
                correlations = self.echoes_s[correlation['filename_waveform']]
            else:
                correlations = []
            correlations.append(correlation)
            self.echoes_s[correlation['filename_waveform']] = correlations

    def delete_echo(self, filename_waveform, frequency, wave_type):
        deleted = False
        

        #  delete in filesystem
        saved_path = os.path.normpath(filename_waveform)
        file_split = os.path.split(saved_path)[-1]
        base_folder = os.path.split(os.path.split(saved_path)[0])[-1]
            
            
        folder = os.path.join(self.folder, base_folder, wave_type)
        exists = os.path.exists(folder)
        if exists:
            json_search = os.path.join(folder,'*'+str(round(frequency*1e-6,1))+'_MHz.json')
            res_files = glob.glob(json_search)
            if len(res_files):
                file_for_deletion = res_files[0]

                os.remove(file_for_deletion)
                deleted = True

                if wave_type == "P":
                    if filename_waveform in self.echoes_p:
                        del self.echoes_p[filename_waveform]
                        #deleted = True
                elif wave_type == "S":
                    if filename_waveform in self.echoes_s:
                        del self.echoes_s[filename_waveform]
                        #deleted = True
                

        return deleted

    def delete_echoes(self, clear_info):
        cleared = True
        for cl in clear_info:
            wave_type = cl['wave_type']
            frequency = cl['frequency']
            fname = cl['filename_waveform']

            cleared = self.delete_echo(fname, frequency, wave_type)

        return cleared

    def clear(self):
        self.__init__()

    
    def get_echoes(self):
        return self.echoes_p, self.echoes_s

    def get_echoes_by_condition(self, condition, wave_type='P'):
        echoes = {}
        echoes_out = []
        if wave_type == 'P':
            echoes = self.echoes_p
        elif wave_type == 'S':
            echoes = self.echoes_s
        if len(echoes):
            for fname in echoes:
                echo_f = echoes[fname]
                for echo in echo_f:
                    
                
                    freq = echo['frequency']
                    folder = os.path.split(os.path.split(fname)[0])[-1]
                    if folder == condition:
                        echoes_out.append( echo)
        return echoes_out
 
 
    def save_result(self, correlation ):
        wave_type = correlation['wave_type']
        
        if wave_type == 'P' or wave_type == 'S':
            echo = correlation
            fname = echo['filename_waveform']
            freq = echo['frequency']
            folder = os.path.split(fname)[:-1]


            p_folder = os.path.join(*folder, wave_type)
            exists = os.path.exists(p_folder)
            if not exists:
                try:
                    os.mkdir(p_folder)
                except:
                    return

            data = echo
            basename = os.path.basename(fname)+'.'+str(round(freq*1e-6,1))+'_MHz.json'
            filename = os.path.join(p_folder,basename)
            try:
                with open(filename, 'w') as json_file:
                    json.dump(data, json_file, indent = 2) 

                    json_file.close()
            except:
                print('could not save file: '+ filename)

    

    def load_result_from_file(self ):

        for subfolder in self.subfolders:
            wave_types = ['P','S']
            for wave_type in wave_types:
                folder = os.path.join(self.folder, subfolder, wave_type)
                exists = os.path.exists(folder)
                if exists:
                    json_search = os.path.join(folder,'*.json')
                    res_files = glob.glob(json_search)
                    for file in res_files:

                        with open(file) as json_file:
                            data = json.load(json_file)
                            correlation = data
                            if 'wave_type' in correlation:
                                wave_type = correlation['wave_type']
                                if wave_type == wave_type:
                                    if 'filename_waweform' in correlation:
                                        saved_path = correlation['filename_waweform']
                                    elif 'filename_waveform' in correlation:
                                        saved_path = correlation['filename_waveform']
                                    else:
                                        continue
                                    saved_path = os.path.normpath(saved_path)
                                    file_split = os.path.split(saved_path)[-1]

                                    
                                    base_folder = os.path.split(os.path.split(saved_path)[0])[-1]
                                    updated_path = os.path.join(self.folder, base_folder, file_split)
                                    correlation['filename_waveform'] = updated_path
                                    self.add_echoe(correlation)
                            json_file.close()

            