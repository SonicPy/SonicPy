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
    def __init__(self, app = None):
        super().__init__()
        self.model = OverViewModel()

        if app is not None:
            self.setStyle(app)
        self.widget = OverViewWidget()
        self.make_connections()
        self.line_plots = {}
        self.selected_fname = ''
        self.freq = 0
        self.set_US_folder(folder = '/Users/ross/Globus/s16bmb-20210717-e244302-Aihaiti/sam2/US')
        
    def make_connections(self):  

        self.widget.open_btn.clicked.connect(self.open_btn_callback)
        self.widget.waterfall_plt_btn.clicked.connect(self.waterfall_plt_btn_callback)
        self.widget.scale_ebx.valueChanged.connect(self.scale_changed_callback )
        self.widget.clip_cbx.clicked.connect(self.clip_changed_callback )
        self.widget.win.plot_widget.cursor_y_signal.connect(self.cursor_y_signal_callback )

    def cursor_y_signal_callback(self, y_pos):

        index = round(y_pos)
        
        fnames = list(self.model.waterfall.scans[0].keys())
        if index >=0 and index < len(fnames):
            
            self.selected_fname = fnames[index]
            
            
            self.re_plot()
            self.file_selected_signal.emit(self.selected_fname)
            


    def preferences_module(self, *args, **kwargs):
        pass

    def scale_changed_callback(self):
        scale = self.widget.scale_ebx.value()
        self.model.waterfall.set_scale(scale)
        self.re_plot()

    def clip_changed_callback(self):
        clip = self.widget.clip_cbx.checkState()
        self.model.waterfall.set_clip(clip)
        
        self.re_plot()

    def freq_btns_callback(self, btn):
        index = self.widget.freq_btns_list.index(btn)
        self.set_frequency(index)

    def waterfall_plt_btn_callback(self):
        self.update_data()

    def open_btn_callback(self):
        self.set_US_folder()

    def set_US_folder(self, *args, **kwargs):

        default_index = 5
        if 'folder' in kwargs:
            folder = kwargs['folder']
        else:
            folder = QtWidgets.QFileDialog.getExistingDirectory(self.widget, caption='Select US folder',
                                                     directory='/Users/ross/Globus/s16bmb-20210717-e244302-Aihaiti')
       
        # All files ending with .txt
        self.model.set_folder_path(folder)
        freqs = list(self.model.fps_Hz.keys())
        self.widget.set_freq_buttons(len(freqs))
        
        self.widget.freq_btns_list[default_index].setChecked(True)

        self.widget.fname_lbl.setText(folder)
        
        self.set_frequency(default_index)
        self.widget.freq_btns.buttonClicked.connect(self.freq_btns_callback)

    def set_frequency(self, index):
        self.model.waterfall.clear()
        freqs = list(self.model.fps_Hz.keys())
        self.freq = freqs[index]
        
        self.model.waterfall.set_clip(self.widget.clip_cbx.checkState())
        self.model.waterfall.set_scale(self.widget.scale_ebx.value())
        self.model.load_multiple_files(self.freq)
        self.re_plot()

    def re_plot(self, ):
        self.model.waterfall.rescale_waveforms()
    
        waterfall_waveform = self.model.waterfall.waterfall_out['waveform']
        limits=[]
        if len(self.selected_fname):
            fnames = list(self.model.waterfall.scans[0].keys())
            if self.selected_fname in fnames:
                limits = self.model.waterfall.waveform_limits[ self.selected_fname ]
        

        if len(limits):
            selected = [waterfall_waveform[0] [limits[0]:limits[1]],
                        waterfall_waveform[1] [limits[0]:limits[1]]]
            waterfall_waveform = [ np.append(waterfall_waveform[0] [:limits[0]], waterfall_waveform[0] [limits[1]:]),
                                   np.append(waterfall_waveform[1] [:limits[0]], waterfall_waveform[1] [limits[1]:])]
            selected_name = os.path.split(self.selected_fname)[-1]
        else:
            selected = [[],[]]
            selected_name = ''

        self.widget.win.clear_plot()
        
        self.update_plot(waterfall_waveform,selected)
        self.widget.win.set_name ( self.freq)
        self.widget.win.set_selected_name (selected_name)
       

    def update_plot(self, waveform,selected=[[],[]]):
        if waveform is not None:
            self.widget.win.plot(waveform[0],waveform[1],selected[0],selected[1])

    def update_selected(self, waveform):
        if waveform is not None:
            self.widget.win.plot_selected(waveform)
            

    def save_result(self):
        pass
        #filename = self.fname + '.json'
        #self.model.save_result(filename)


    def update_data(self, *args, **kwargs):
        pass
        

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