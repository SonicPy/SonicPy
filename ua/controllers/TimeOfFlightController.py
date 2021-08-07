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
from ua.widgets.TimeOfFlightWidget import TimeOfFlightWidget
from ua.models.UltrasoundAnalysisModel import get_local_optimum, UltrasoundAnalysisModel
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import math

from ua.models.TimeOfFlightModel import TimeOfFlightModel

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog, open_files_dialog 
import glob


############################################################

class TimeOfFlightController(QObject):
    def __init__(self, app = None):
        super().__init__()
        self.model = TimeOfFlightModel()

        if app is not None:
            self.setStyle(app)
        self.widget = TimeOfFlightWidget()
        self.make_connections()
        self.line_plots = {}

        self.set_US_folder(folder = '/Users/ross/Globus/s16bmb-20210717-e244302-Aihaiti/sam1/US')
        
    def make_connections(self):  

        self.widget.open_btn.clicked.connect(self.open_btn_callback)
        self.widget.waterfall_plt_btn.clicked.connect(self.waterfall_plt_btn_callback)
        self.widget.scale_ebx.valueChanged.connect(self.scale_changed_callback )
        self.widget.clip_cbx.clicked.connect(self.clip_changed_callback )
        

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
        freq = freqs[index]
        
        self.model.waterfall.set_clip(self.widget.clip_cbx.checkState())
        self.model.waterfall.set_scale(self.widget.scale_ebx.value())
        self.model.load_multiple_files(freq)
        self.re_plot()

    def re_plot(self):
        self.model.waterfall.rescale_waveforms()
    
        waterfall_waveform = self.model.waterfall.waterfall_out['waveform']
        self.widget.win.clear_plot()
        
        self.update_plot(waterfall_waveform)
        
       

    def update_plot(self, waveform):
        if waveform is not None:
            self.widget.win.plot(waveform)
            

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