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

from ua.models.OverViewModel import OverViewModel
from ua.controllers.OverViewController import OverViewController
from ua.controllers.UltrasoundAnalysisController import UltrasoundAnalysisController

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog, open_files_dialog 
import glob 

from .. import resources_path


############################################################

class TimeOfFlightController(QObject):
    def __init__(self, app = None, offline = True):
        super().__init__()

        self.overview_controller = OverViewController()
        overview_widget = self.overview_controller.widget
        self.correlation_controller = UltrasoundAnalysisController()
        analysis_widget = self.correlation_controller.display_window

        self.model = OverViewModel()
        self.widget = TimeOfFlightWidget(overview_widget, analysis_widget)
        

        if app is not None:
            self.setStyle(app)
        
        
        self.make_connections()

        #self.overview_controller.set_US_folder(folder = '/Users/ross/Globus/s16bmb-20210717-e244302-Aihaiti/sam2/US')
        
    def make_connections(self):  

        self.overview_controller.file_selected_signal.connect(self.file_selected_signal_callback)
        self.overview_controller.folder_selected_signal.connect(self.folder_selected_signal_callback)

        self.overview_controller.cursor_position_signal.connect(self.correlation_controller.sync_cursors)
        self.correlation_controller.cursor_position_signal.connect(self.overview_controller.sync_cursors)

        self.correlation_controller.correlation_saved_signal.connect(self.correlation_saved_signal_callback)

    def correlation_saved_signal_callback(self, correlation):
        self.overview_controller.correlation_echoes_added(correlation)
    
    def folder_selected_signal_callback(self, folder):
        self.widget.setWindowTitle("Time-of-flight analysis. © R. Hrubiak, 2021. Folder: "+ os.path.abspath( folder))

    def file_selected_signal_callback(self, fname):

        f_start = self.overview_controller.widget.freq_start.value()
        f_step = self.overview_controller.widget.freq_step.value()
        name = os.path.split(fname)[-1]
        fbase = name[-7:-4]
        
        f_freq_ind = int(fbase)
        freq = f_start + f_freq_ind * f_step

        self.correlation_controller.update_data(filename=fname)
        
        # setting frequency input triggers calculation of correlation
        current_freq = self.correlation_controller.display_window.freq_ebx.value()
        if current_freq != freq:
            self.correlation_controller.display_window.freq_ebx.setValue(freq)
        else:
            self.correlation_controller.calculate_data()

    def preferences_module(self, *args, **kwargs):
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