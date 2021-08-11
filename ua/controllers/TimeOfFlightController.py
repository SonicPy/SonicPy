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

        self.overview_controller.set_US_folder(folder = '/Users/ross/Globus/s16bmb-20210717-e244302-Aihaiti/sam2/US')
        
    def make_connections(self):  

        self.overview_controller.file_selected_signal.connect(self.file_selected_signal_callback)
        self.overview_controller.folder_selected_signal.connect(self.folder_selected_signal_callback)

    
    def folder_selected_signal_callback(self, folder):
        self.widget.setWindowTitle("Time-of-flight analysis. © R. Hrubiak, 2021. Folder: "+folder)

    def file_selected_signal_callback(self, fname):
        self.correlation_controller.update_data(filename=fname)
        
        #remove this next line if setting frequency instead
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