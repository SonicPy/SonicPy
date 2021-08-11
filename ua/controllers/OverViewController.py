#!/usr/bin/env python



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
from utilities.utilities import *
from ua.widgets.UltrasoundAnalysisWidget import UltrasoundAnalysisWidget
from ua.widgets.OverviewWidget import OverViewWidget
from ua.models.UltrasoundAnalysisModel import get_local_optimum, UltrasoundAnalysisModel
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import math

from ua.models.OverViewModel import OverViewModel

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog, open_files_dialog 
import glob


############################################################

class OverViewController(QObject):

    file_selected_signal = pyqtSignal(str)
    folder_selected_signal = pyqtSignal(str)
    def __init__(self, app = None):
        super().__init__()
        self.model = OverViewModel()

        if app is not None:
            self.setStyle(app)
        self.widget = OverViewWidget()

        self.widget.clip_cbx.setChecked(self.model.settings['clip'])
        self.widget.scale_ebx.setValue(self.model.settings['scale'])
        self.make_connections()
        self.line_plots = {}
        self.selected_fname = ''
        self.freq = 0
        self.cond = 0
        
        
        
    def make_connections(self):  

        self.widget.open_btn.clicked.connect(self.open_btn_callback)
   
        self.widget.scale_ebx.valueChanged.connect(self.scale_changed_callback )
        self.widget.clip_cbx.clicked.connect(self.clip_changed_callback )
        self.widget.single_frequency_waterfall.plot_widget.cursor_y_signal.connect(self.single_frequency_cursor_y_signal_callback )
        self.widget.single_condition_waterfall.plot_widget.cursor_y_signal.connect(self.single_condition_cursor_y_signal_callback )

    def single_frequency_cursor_y_signal_callback(self, y_pos):

        index = round(y_pos)
        
        fnames = list(self.model.waterfalls[self.freq].scans[0].keys())
        if index >=0 and index < len(fnames):
            
            self.selected_fname = fnames[index]
            
            self.re_plot_single_frequency()

            cond = self.model.file_cond_dict[self.selected_fname]
            conds = list(self.model.fps_cond.keys())
            ind  = conds.index(cond)
            self.set_condition(ind)

            self.file_selected_signal.emit(self.selected_fname)

    def single_condition_cursor_y_signal_callback(self, y_pos):

        index = round(y_pos)
        
        fnames = list(self.model.waterfalls[self.cond].scans[0].keys())
        if index >=0 and index < len(fnames):
            
            self.selected_fname = fnames[index]
            
            self.re_plot_single_condition()

            freq = self.model.file_freq_dict[self.selected_fname]
            freqs = list(self.model.fps_Hz.keys())
            ind  = freqs.index(freq)
            self.set_frequency(ind)
            
            self.file_selected_signal.emit(self.selected_fname)

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

    def freq_btns_callback(self, btn):
        index = self.widget.freq_btns_list.index(btn)
        self.set_frequency(index)

    def cond_btns_callback(self, btn):
        index = self.widget.cond_btns_list.index(btn)
        self.set_condition(index)

    def freq_scroll_callback(self, val):
        self.set_frequency(val)

    def cond_scroll_callback(self, val):
        self.set_condition(val)

    def open_btn_callback(self):
        self.set_US_folder()

    def set_US_folder(self, *args, **kwargs):
        self.model.clear()
        default_frequency_index = 3
        default_condition_index = 0
        if 'folder' in kwargs:
            folder = kwargs['folder']
        else:
            folder = QtWidgets.QFileDialog.getExistingDirectory(self.widget, caption='Select US folder',
                                                     directory='/Users/ross/Globus/s16bmb-20210717-e244302-Aihaiti')

        self.folder_selected_signal.emit(folder)
       
        # All files ending with .txt
        self.model.set_folder_path(folder)
        freqs = list(self.model.fps_Hz.keys())
        #self.widget.set_freq_buttons(len(freqs))

        conds = list(self.model.fps_cond.keys())
        #self.widget.set_cond_buttons(len(conds))
        
        '''self.widget.freq_btns_list[default_frequency_index].setChecked(True)
        self.widget.cond_btns_list[default_condition_index].setChecked(True)'''
        
        
        self.set_frequency(default_frequency_index)
        self.widget.freq_scroll.setMaximum(len(freqs)-1)
        self.widget.freq_scroll.valueChanged .connect(self.freq_scroll_callback)


        
        self.set_condition(default_condition_index)
        self.widget.cond_scroll.setMaximum(len(conds)-1)
        self.widget.cond_scroll.valueChanged.connect(self.cond_scroll_callback)

    def set_frequency(self, index):
        freqs = list(self.model.fps_Hz.keys())
        self.freq = freqs[index]
        self.model.load_multiple_files_by_frequency(self.freq)
        
        self.widget.freq_scroll.blockSignals(True)
        self.widget.freq_scroll.setValue(index)
        self.widget.freq_scroll.blockSignals(False)
        
        self.re_plot_single_frequency()

    def set_condition(self, index):
        
        conds = list(self.model.fps_cond.keys())
        self.cond = conds[index]
        self.model.load_multiple_files_by_condition(self.cond)

        self.widget.cond_scroll.blockSignals(True)
        self.widget.cond_scroll.setValue(index)
        self.widget.cond_scroll.blockSignals(False)
        self.re_plot_single_condition()

    def re_plot_single_frequency(self ):
        waterfall = self.model.waterfalls[self.freq]
        waterfall.get_rescaled_waveforms()
    
        waterfall_waveform = waterfall.waterfall_out['waveform']
        limits=[]
        if len(self.selected_fname):
            fnames = list(waterfall.scans[0].keys())
            if self.selected_fname in fnames:
                limits = waterfall.waveform_limits[ self.selected_fname ]
        

        if len(limits):
            selected = [waterfall_waveform[0] [limits[0]:limits[1]],
                        waterfall_waveform[1] [limits[0]:limits[1]]]
            waterfall_waveform = [ np.append(waterfall_waveform[0] [:limits[0]], waterfall_waveform[0] [limits[1]:]),
                                   np.append(waterfall_waveform[1] [:limits[0]], waterfall_waveform[1] [limits[1]:])]
            selected_name = os.path.split(self.selected_fname)[-1]
        else:
            selected = [[],[]]
            selected_name = ''

        self.widget.single_frequency_waterfall.clear_plot()
        
        self.update_plot_sigle_frequency(waterfall_waveform,selected)
        self.widget.single_frequency_waterfall.set_name ( self.freq)
        self.widget.single_frequency_waterfall.set_selected_name (selected_name)

    def re_plot_single_condition(self ):
        waterfall = self.model.waterfalls[self.cond]
        waterfall.get_rescaled_waveforms()
    
        waterfall_waveform = waterfall.waterfall_out['waveform']
        limits=[]
        if len(self.selected_fname):
            fnames = list(waterfall.scans[0].keys())
            if self.selected_fname in fnames:
                limits = waterfall.waveform_limits[ self.selected_fname ]
        

        if len(limits):
            selected = [waterfall_waveform[0] [limits[0]:limits[1]],
                        waterfall_waveform[1] [limits[0]:limits[1]]]
            waterfall_waveform = [ np.append(waterfall_waveform[0] [:limits[0]], waterfall_waveform[0] [limits[1]:]),
                                   np.append(waterfall_waveform[1] [:limits[0]], waterfall_waveform[1] [limits[1]:])]
            selected_name = os.path.split(self.selected_fname)[-1]
        else:
            selected = [[],[]]
            selected_name = ''

        self.widget.single_condition_waterfall.clear_plot()
        
        self.update_plot_sigle_condition(waterfall_waveform,selected)
        self.widget.single_condition_waterfall.set_name ( self.cond)
        self.widget.single_condition_waterfall.set_selected_name (selected_name)
       

    def update_plot_sigle_frequency(self, waveform,selected=[[],[]]):
        if waveform is not None:
            self.widget.single_frequency_waterfall.plot(waveform[0],waveform[1],selected[0],selected[1])

 

    def update_plot_sigle_condition(self, waveform,selected=[[],[]]):
        if waveform is not None:
            self.widget.single_condition_waterfall.plot(waveform[0],waveform[1],selected[0],selected[1])


            

    def save_result(self):
        pass
        #filename = self.fname + '.json'
        #self.model.save_result(filename)



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