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
from ua.models.UltrasoundAnalysisModel import  UltrasoundAnalysisModel
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import math

from ua.models.OverViewModel import OverViewModel
from ua.controllers.OverViewController import OverViewController
from ua.controllers.UltrasoundAnalysisController import UltrasoundAnalysisController
from ua.controllers.ArrowPlotController import ArrowPlotController

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog, open_files_dialog 
import glob 

from ua. models.EchoesResultsModel import EchoesResultsModel

from .. import resources_path, __version__


############################################################

class TimeOfFlightController(QObject):
    def __init__(self, app = None, offline = True):
        super().__init__()
        self.app = app
        self.echoes_results_model = EchoesResultsModel()
        self.overview_controller = OverViewController(self.app, self.echoes_results_model)
        overview_widget = self.overview_controller.widget
        self.correlation_controller = UltrasoundAnalysisController(self.app, self.echoes_results_model)
        analysis_widget = self.correlation_controller.display_window

        self.arrow_plot_controller = ArrowPlotController(self.app, self.echoes_results_model)
        arrow_plot_widget = self.arrow_plot_controller.arrow_plot_window

        self.widget = TimeOfFlightWidget(app, overview_widget, analysis_widget, arrow_plot_widget)
        self.widget.setWindowTitle("Time-of-flight analysis. ver." + __version__ + "  © R. Hrubiak, 2022.")
        
        if app is not None:
            self.setStyle(app)
        
        self.make_connections()
        
    def make_connections(self):  

        self.overview_controller.file_selected_signal.connect(self.file_selected_signal_callback)
        self.overview_controller.folder_selected_signal.connect(self.folder_selected_signal_callback)
        self.overview_controller.freq_settings_changed_signal.connect(self.freq_settings_changed_signal_callback)
        self.overview_controller.cursor_position_signal.connect(self.correlation_controller.sync_cursors)

        self.correlation_controller.cursor_position_signal.connect(self.overview_controller.sync_cursors)
        self.correlation_controller.correlation_saved_signal.connect(self.correlation_saved_signal_callback)
        self.correlation_controller.wave_type_toggled_signal.connect(self.wave_type_toggled_signal_callback)

        self.arrow_plot_controller.arrow_plot_freq_cursor_changed_signal.connect(self.arrow_plot_freq_cursor_changed_signal_callback)
        self.arrow_plot_controller.arrow_plot_del_clicked_signal.connect(self.arrow_plot_del_clicked_signal_callback)
        self.arrow_plot_controller.arrow_plot_clear_clicked_signal.connect(self.arrow_plot_clear_clicked_signal_callback)


    ###
    # Overview controller callbacks
    ##

    def freq_settings_changed_signal_callback(self, freq):
        self.correlation_controller.display_window.freq_ebx.setValue(freq)

    def file_selected_signal_callback(self, data):

        fname = data['fname']
        fbase = data['freq']
        cond = data['cond']

        echo_type = ''
        if  self.correlation_controller.display_window.p_wave_btn.isChecked():
            echo_type = "P"
        elif self.correlation_controller.display_window.s_wave_btn.isChecked():
            echo_type = "S"


        echoes_p, echoes_s = self.echoes_results_model.get_echoes()

    
        if fname in echoes_p:
            echo_p = echoes_p[fname]
            bounds_p = echo_p['echo_bounds']
            self.correlation_controller.display_window.lr1_p.setRegion(bounds_p[0])
            self.correlation_controller.display_window.lr2_p.setRegion(bounds_p[1])
        
        if fname in echoes_s:
            echo_s = echoes_s[fname]
            bounds_s = echo_s['echo_bounds']
            self.correlation_controller.display_window.lr1_s.setRegion(bounds_s[0])
            self.correlation_controller.display_window.lr2_s.setRegion(bounds_s[1])

        f_start = self.overview_controller.widget.freq_start.value()
        f_step = self.overview_controller.widget.freq_step.value()
        
        f_freq_ind = int(fbase)
        freq = f_start + f_freq_ind * f_step

        self.correlation_controller.update_data_by_dict(data)
        
        # setting frequency input normally triggers calculation of correlation so set with out triggeing signals        
        self.correlation_controller.display_window.freq_ebx.blockSignals(True)
        self.correlation_controller.display_window.freq_ebx.setValue(freq)
        self.correlation_controller.display_window.freq_ebx.blockSignals(False)
        
        
        self.correlation_controller.calculate_data()

        echoes_by_condition = self.echoes_results_model.get_echoes_by_condition(cond, echo_type)
        self.arrow_plot_controller.set_wave_type(echo_type)
        self.arrow_plot_controller.set_condition( cond) 
        self.arrow_plot_controller.refresh_model()
        self.arrow_plot_controller.set_frequency_cursor(freq)

    
    def folder_selected_signal_callback(self, folder):
        self.widget.setWindowTitle("Time-of-flight analysis. V." + __version__ + "  © R. Hrubiak, 2022. Folder: "+ os.path.abspath( folder))
        subfolders = copy.copy(self.overview_controller.model.conditions_folders_sorted)
        self.echoes_results_model.folder = folder
        self.echoes_results_model.subfolders = subfolders
        self.echoes_results_model.load_result_from_file()
        saved_echoes_p, saved_echoes_s = self.echoes_results_model.get_echoes()
        self.overview_controller.correlation_echoes_added(saved_echoes_p)
        self.overview_controller.correlation_echoes_added(saved_echoes_s)
        self.overview_controller.re_plot_single_frequency()
        self.overview_controller.re_plot_single_condition()

        echo_type = ''
        if  self.correlation_controller.display_window.p_wave_btn.isChecked():
            echo_type = "P"
        elif self.correlation_controller.display_window.s_wave_btn.isChecked():
            echo_type = "S"
        self.arrow_plot_controller.set_wave_type(echo_type)

    ###
    # Ultrasound controller callbacks
    ##

    def correlation_saved_signal_callback(self, correlation):
        
        correlations = {correlation['filename_waveform']:correlation}
        

        self.echoes_results_model.add_echoe(correlation)
        self.echoes_results_model.save_result(correlation)

        self.overview_controller.correlation_echoes_added(correlations)

        self.arrow_plot_controller.refresh_model()

    def wave_type_toggled_signal_callback(self, wave_type):
        
        self.arrow_plot_controller.set_wave_type(wave_type)
        self.arrow_plot_controller.refresh_model()
    ###
    # Arrow plot controller callbacks
    ##

    def arrow_plot_del_clicked_signal_callback(self, del_info):
        fname = del_info['filename_waveform']
        freq = del_info['frequency']
        wave_type = del_info['wave_type']
        deleted = self.echoes_results_model.delete_echo(fname, freq, wave_type)
        if deleted:
            self.arrow_plot_controller.echo_deleted(del_info)
            self.overview_controller.echo_deleted(del_info)

    def arrow_plot_clear_clicked_signal_callback(self, clear_info):
        cl = clear_info['clear_info']
        cleared = self.echoes_results_model.delete_echoes(cl)
        if cleared:
            self.arrow_plot_controller.condition_cleared(clear_info)
            self.overview_controller.condition_cleared(clear_info) 


    def arrow_plot_freq_cursor_changed_signal_callback(self, cursor_info):
        fname = cursor_info['filename_waveform']
        freq = cursor_info['frequency']
        
        #self.overview_controller. set_frequency_by_value(freq)
        self.overview_controller. select_fname(fname)



    ###
    # General stuff
    ###

    

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