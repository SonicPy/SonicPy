#!/usr/bin/env python



import imp
import os.path, sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
from functools import partial
import json
import copy
from pathlib import Path
from numpy import arange
from numpy.core.einsumfunc import _parse_possible_contraction
from sqlalchemy import false
#from pyrsistent import T
from utilities.utilities import *
from ua.widgets.UltrasoundAnalysisWidget import UltrasoundAnalysisWidget
from ua.widgets.OverviewWidget import OverViewWidget, FolderListWidget
from ua.models.UltrasoundAnalysisModel import  UltrasoundAnalysisModel
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import math

from ua.models.OverViewModel import OverViewModel


import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog, open_files_dialog
import glob
from ua.models.EchoesResultsModel import EchoesResultsModel

############################################################

class OverViewController(QObject):

    file_selected_signal = pyqtSignal(dict)
    folder_selected_signal = pyqtSignal(str)
    cursor_position_signal = pyqtSignal(float)
    freq_settings_changed_signal = pyqtSignal(float)
    folders_sorted_signal = pyqtSignal(list)

    def __init__(self, app = None, results_model=EchoesResultsModel()):
        super().__init__()
        self.model = OverViewModel(results_model)

        if app is not None:
            self.setStyle(app)
        self.widget = OverViewWidget()
        #self.sync_widget_controls_with_model_non_signaling()
        self.folder_widget = FolderListWidget()

        self.make_connections()
        self.line_plots = {}
        self.selected_fname = ''
        self.freq = '000'
        self.cond = '0psi'

       
    def make_connections(self):  

        self.widget.open_btn.clicked.connect(self.open_btn_callback)
        self.widget.sort_btn.clicked.connect(self.folder_widget.raise_widget)
   
        self.widget.scale_ebx.valueChanged.connect(self.scale_changed_callback )
        self.widget.clip_cbx.clicked.connect(self.clip_changed_callback )
        self.widget.single_frequency_waterfall.plot_widget.cursor_y_signal.connect(self.single_frequency_cursor_y_signal_callback )
        self.widget.single_condition_waterfall.plot_widget.cursor_y_signal.connect(self.single_condition_cursor_y_signal_callback )
        self.widget.single_frequency_waterfall.plot_widget. cursor_changed_singal.connect(self.sync_cursors)
        self.widget.single_condition_waterfall.plot_widget. cursor_changed_singal.connect(self.sync_cursors)
        self.widget.single_frequency_waterfall.plot_widget. cursor_changed_singal.connect(self.emit_cursor)
        self.widget.single_condition_waterfall.plot_widget. cursor_changed_singal.connect(self.emit_cursor)

        self.widget.single_condition_waterfall.scrollSignal.connect(self.scrollSignal_callback)
        self.widget.single_frequency_waterfall.scrollSignal.connect(self.scrollSignal_callback)

        self.widget.freq_scroll.valueChanged .connect(self.freq_scroll_callback)
        self.widget.cond_scroll.valueChanged.connect(self.cond_scroll_callback)

        self.widget.cond_minus_btn.clicked.connect(partial(self.cond_btn_callback,-1))
        self.widget.cond_plus_btn.clicked.connect(partial(self.cond_btn_callback,1))
        self.widget.freq_minus_btn.clicked.connect(partial(self.freq_btn_callback,-1))
        self.widget.freq_plus_btn.clicked.connect(partial(self.freq_btn_callback,1))

        self.widget.freq_start.valueChanged.connect(self.freq_start_step_callback)
        self.widget.freq_step.valueChanged.connect(self.freq_start_step_callback)

        self.folder_widget.list_changed_signal.connect(self.list_changed_signal_callback)

    def reset(self):
        self.model.clear()
        self.widget.clear_widget()
    

    def list_changed_signal_callback(self, folders):
        
        self.model.results_model.set_folders_sorted(folders)
        self.folders_sorted_signal.emit(folders)
        self.model.conditions_folders_sorted = folders
        self.model.load_multiple_files_by_frequency(self.freq)
        self.re_plot_single_frequency()

    def scrollSignal_callback(self, delta):
        value = self.widget.scale_ebx.value()
        new_value = value + value * 0.1 * delta
        self.widget.scale_ebx.setValue(new_value)


    def freq_start_step_callback(self, *args, **kwargs):

        
        f_start = self.widget.freq_start.value()
        f_step = self.widget.freq_step.value()

        self.model.set_freq_start_step(f_start, f_step)

        display_freq = f_start + int(self.freq) * f_step
        self.widget.single_frequency_waterfall.set_name ( str(display_freq) + ' MHz')
        #self.freq_settings_changed_signal.emit(display_freq)

    def freq_str_ind_to_val(self, str_ind):
        f_start = self.widget.freq_start.value()
        f_step = self.widget.freq_step.value()


        val_freq = f_start + int(str_ind) * f_step
        return val_freq * 1e6

    def emit_cursor(self, pos):
        self.cursor_position_signal.emit(pos)

    def sync_cursors(self, pos):
        
        self.widget.single_frequency_waterfall.plot_widget.fig.set_cursor(pos)
        self.widget.single_condition_waterfall.plot_widget.fig.set_cursor(pos)

    def correlation_echoes_added(self , correlations):
        
        

        self.re_plot_single_frequency()
        self.re_plot_single_condition()

    def echo_deleted(self, del_info):
        
        fname = del_info['filename_waveform']
        freq = del_info['frequency']
        wave_type = del_info['wave_type']
        self. model.del_echoes(self.cond, wave_type, freq)

        self.re_plot_single_frequency()
        self.re_plot_single_condition()

    def condition_cleared(self, clear_info):
       
        condition = clear_info['condition']
        wave_type = clear_info['wave_type']
        cl = clear_info['clear_info']
        if len(cl):
            self. model.clear_condition(condition, wave_type) 

            self.re_plot_single_frequency() 
            self.re_plot_single_condition()
            

    def save_result(self):
        pass
        #filename = self.fname + '.json'
        #self.model.save_result(filename)


    def single_frequency_cursor_y_signal_callback(self, y_pos):

        if len(self.model.waterfalls):
            # this is the inxed of the plot when user clicks on the waterfall plot
            index = round(y_pos)
            
            fnames = list(self.model.waterfalls[self.freq].waveforms.keys())
            if index >=0 and index < len(fnames):
                
                fname = fnames[index]
                
                self.select_fname(fname)

    def get_data_by_filename(self, fname):
        data = {}
        if fname in self.model.file_dict:
            cond = self.model.file_dict[fname][0]
            freq = self.model.file_dict[fname][1]
            conds = self.get_conditions_list()
            ind  = conds.index(cond)
            self.set_condition(ind)
            
            data['fname'] = fname
            data['cond'] = cond
            data['freq'] = freq
            selected = self.model.spectra[cond][freq]['waveform']
            
            data['t'] = selected[0]
            data['spectrum'] = selected[1]

        return data

    def get_conditions_list(self):
        conds = list(self.model.fps_cond.keys())
        return conds

    def select_fname(self, fname, freq= -1.0):
        temp_fname = copy.copy(self.selected_fname)
        self.selected_fname = fname
        data = self.get_data_by_filename(fname)
        current_frequency = copy.copy(self.freq)
        current_condition = copy.copy(self.cond)
        
        freq = data['freq']
        cond = data['cond']

        freq_val = self.freq_str_ind_to_val(freq)
        
        
        if freq != current_frequency:
            ind = list(self.model.fps_Hz.keys()).index(freq)
            self.set_frequency(ind)
        if cond != current_condition:
            self.set_condition(cond)
        
        if temp_fname != self.selected_fname:
            self.re_plot_single_frequency()
            self.re_plot_single_condition()
        self.file_selected_signal.emit(data)
                

    def single_condition_cursor_y_signal_callback(self, y_pos):
        
        if self.cond in self.model.waterfalls:
            index = round(y_pos)
            
            fnames = list(self.model.waterfalls[self.cond].waveforms.keys())
            if index >=0 and index < len(fnames):
                if fnames[index] in self.model.file_dict:
                    #self.selected_fname = fnames[index]
                    fname = fnames[index]
                    self.select_fname(fname)
                    #self.re_plot_single_condition()

                    '''cond = self.model.file_dict[self.selected_fname][0]
                    self.cond = cond
                    freq = self.model.file_dict[self.selected_fname][1]
                    freqs = list(self.model.fps_Hz.keys())
                    ind  = freqs.index(freq)
                    self.set_frequency(ind)

                    data = {}
                    
                    data['fname'] = self.selected_fname
                    data['cond'] = cond
                    data['freq'] = freq

                    selected = self.model.spectra[self.cond][freq]['waveform']
                
                    data['t'] = selected[0]
                    data['spectrum'] = selected[1]
                    
                    self.file_selected_signal.emit(data)
                    self.re_plot_single_condition()'''

    def preferences_module(self, *args, **kwargs):
        pass

    def scale_changed_callback(self):
        scale = self.widget.scale_ebx.value()
        self.model.set_scale(scale)
        self.re_plot_single_frequency()
        self.re_plot_single_condition()

    def clip_changed_callback(self):
        clip = self.widget.clip_cbx.checkState()
        self.model.set_clip(clip)
        
        self.re_plot_single_frequency()
        self.re_plot_single_condition()

    ### Navigating PT points and frequencies with scorllbar and buttons:
    '''def freq_btns_callback(self, btn):
        index = self.widget.freq_btns_list.index(btn)
        self.set_frequency(index)

    def cond_btns_callback(self, btn):
        index = self.widget.cond_btns_list.index(btn)
        self.set_condition(index)'''

    def freq_scroll_callback(self, val):
        self.set_frequency(val)
        self.re_plot_single_frequency()

    def cond_scroll_callback(self, val):
        self.set_condition(val)
        self.re_plot_single_condition()

    def freq_btn_callback(self, step):
        val = self.widget.freq_scroll.value()
        min = self.widget.freq_scroll.minimum()
        max = self.widget.freq_scroll.maximum()
        new_val = val + step
        if new_val >= min and new_val <= max:
            self.widget.freq_scroll.setValue(new_val)

    def cond_btn_callback(self, step):
        
        val = self.widget.cond_scroll.value()
        min = self.widget.cond_scroll.minimum()
        max = self.widget.cond_scroll.maximum()
        new_val = val + step
        if new_val >= min and new_val <= max:
            self.widget.cond_scroll.setValue(new_val)
        


    ### opening a folder:
    def open_btn_callback(self, mode ):
        self.set_US_folder(mode = mode)

    def sync_widget_controls_with_model_non_signaling(self):

        self.widget.freq_step.blockSignals(True)
        self.widget.freq_start.blockSignals(True)
        self.widget.clip_cbx.blockSignals(True)
        self.widget.scale_ebx.blockSignals(True)
        self.widget.freq_step.setValue(self.model.results_model.project['settings']['f_step'])
        self.widget.freq_start.setValue(self.model.results_model.project['settings']['f_start'])
        self.widget.clip_cbx.setChecked(self.model.results_model.project['settings']['clip'])
        self.widget.scale_ebx.setValue(self.model.results_model.project['settings']['scale'])
        self.widget.freq_step.blockSignals(False)
        self.widget.freq_start.blockSignals(False)
        self.widget.clip_cbx.blockSignals(False)
        self.widget.scale_ebx.blockSignals(False)

    def set_US_folder(self, *args, **kwargs):
        
        if 'mode' in kwargs:
            mode = kwargs['mode']
        else:
            mode = 'discrete_f'

        self.model.settings['mode'] = mode
        self.model.results_model.set_mode(mode)
        default_frequency_index = 0
        default_condition_index = 0
        if 'folder' in kwargs:
            folder = kwargs['folder']
        else:
            folder = QtWidgets.QFileDialog.getExistingDirectory(self.widget, caption='Select US folder',
                                                     directory='')
        done = False
        
        if len(folder):
            folder = os.path.normpath(folder)
        
        if os.path.isdir(folder):
            
            set_okay = self.model.set_folder_path(folder, mode)

            if set_okay : 
                self.sync_widget_controls_with_model_non_signaling()
                folders = self.model.results_model.get_folders_sorted()
                self.folder_widget.set_folders(folders)
                freqs = list(self.model.fps_Hz.keys())
                conds = list(self.model.fps_cond.keys())
                self.set_frequency(default_frequency_index)
                self.widget.freq_scroll.setMaximum(len(freqs)-1)
                self.set_condition(default_condition_index)
                self.widget.cond_scroll.setMaximum(len(conds)-1)
                self.folder_selected_signal.emit(folder)
          

    def set_frequency_by_value(self, freq):
        str_ind = self.model. freq_val_to_ind(freq)
        if str_ind != None:
            self.set_frequency(str_ind)

    def set_frequency(self, index):
        freqs = list(self.model.fps_Hz.keys())
        if len(freqs) >index and len(freqs):
            self.freq = freqs[index]
            self.model.load_multiple_files_by_frequency(self.freq)
            
            self.widget.freq_scroll.blockSignals(True)
            self.widget.freq_scroll.setValue(index)
            self.widget.freq_scroll.blockSignals(False)
            
            
            self.widget.frequency_lbl.setText(str(self.freq))

    def set_condition(self, index):
        
        conds = list(self.model.fps_cond.keys())
        if len(conds) >index and len(conds):
            self.cond = conds[index]
            self.model.load_multiple_files_by_condition(self.cond)

            self.widget.cond_scroll.blockSignals(True)
            self.widget.cond_scroll.setValue(index)
            self.widget.cond_scroll.blockSignals(False)
            
            self.widget.condition_lbl.setText(str(self.cond))

    def re_plot_single_frequency(self ):
        if self.freq in self.model.waterfalls:
            waterfall = self.model.waterfalls[self.freq]
            echoes_p = self.model.results_model.echoes_p
            echoes_s = self.model.results_model.echoes_s

            freq = self.freq_str_ind_to_val(self.freq)

            for echo_p_name in echoes_p:
                echoes = echoes_p[echo_p_name]
                if freq in echoes:
                    bounds = echoes[freq]['echo_bounds']
                    filename_waveform = echo_p_name
                    wave_type = "P"
                    waterfall.set_echoe(filename_waveform ,wave_type, bounds)

            for echo_s_name in echoes_s:
                echoes = echoes_s[echo_s_name]
                if freq in echoes:
                    bounds = echoes[freq]['echo_bounds']
                    filename_waveform = echo_s_name
                    wave_type = "S"
                    waterfall.set_echoe(filename_waveform ,wave_type, bounds)

            waterfall.get_rescaled_waveforms(caller='re_plot_single_frequency')
        
            selected_fname = self.selected_fname
            waterfall_waveform, \
                selected, \
                    selected_name_out, \
                        echoes_p, echoes_s = waterfall.prepare_waveforms_for_plot( selected_fname)

            self.widget.single_frequency_waterfall.clear_plot()
            
            self.update_plot_sigle_frequency(waterfall_waveform,selected, echoes_p, echoes_s)
            f_start = self.widget.freq_start.value()
            f_step = self.widget.freq_step.value()
            display_freq = f_start + int(self.freq) * f_step
            self.widget.single_frequency_waterfall.set_name ( str(display_freq) + ' MHz')
            self.widget.single_frequency_waterfall.set_selected_name (selected_name_out)

    def re_plot_single_condition(self ):
        if self.cond in self.model.waterfalls:
            waterfall = self.model.waterfalls[self.cond]

            echoes_p = self.model.results_model.echoes_p
            echoes_s = self.model.results_model.echoes_s

            for echo_p_name in echoes_p:
                echoes = echoes_p[echo_p_name]
                for freq in echoes:
                    echo = echoes[freq]
                    bounds = echo['echo_bounds']
                    filename_waveform = echo_p_name
                    wave_type = "P"
                    waterfall.set_echoe(filename_waveform ,wave_type, bounds)

            for echo_s_name in echoes_s:
                echoes = echoes_s[echo_s_name]
                for freq in echoes:
                    echo = echoes[freq]
                    bounds = echo['echo_bounds']
                    filename_waveform = echo_s_name
                    wave_type = "S"
                    waterfall.set_echoe(filename_waveform ,wave_type, bounds)

            waterfall.get_rescaled_waveforms(caller='re_plot_single_condition')
        
            selected_fname = self.selected_fname

            waterfall_waveform, \
                selected, \
                    selected_name_out, \
                        echoes_p, echoes_s = waterfall.prepare_waveforms_for_plot( selected_fname)

            self.widget.single_condition_waterfall.clear_plot()
            
            self.update_plot_sigle_condition(waterfall_waveform,selected,echoes_p, echoes_s)
            self.widget.single_condition_waterfall.set_name ( self.cond)
            self.widget.single_condition_waterfall.set_selected_name (selected_name_out)

    

    def update_plot_sigle_frequency(self, waveform,selected=[[],[]], echoes_p=[[],[]], echoes_s=[[],[]]):
        if waveform is not None:
            #print(echoes_p)
            self.widget.single_frequency_waterfall.plot(waveform[0],waveform[1],
                                                        selected[0],selected[1], 
                                                        echoes_p[0], echoes_p[1],
                                                        echoes_s[0], echoes_s[1])

        

    def update_plot_sigle_condition(self, waveform,selected=[[],[]], echoes_p=[[],[]], echoes_s=[[],[]]):
        if waveform is not None:
            self.widget.single_condition_waterfall.plot(waveform[0],waveform[1],
                                                        selected[0],selected[1], 
                                                        echoes_p[0], echoes_p[1],
                                                        echoes_s[0], echoes_s[1])

    


    def show_window(self):
        self.widget.raise_widget()

                
    def setStyle(self, app):
        from .. import theme 
        from .. import style_path
        self.app = app
        if theme==1:
            WStyle = 'plastique'
            file = open(os.path.join(style_path, "stylesheet.qss"))
            stylesheet = file.read()
            self.app.setStyleSheet(stylesheet)
            file.close()
            self.app.setStyle(WStyle)
        else:
            WStyle = "windowsvista"
            self.app.setStyleSheet(" ")
            #self.app.setPalette(self.win_palette)
            self.app.setStyle(WStyle)