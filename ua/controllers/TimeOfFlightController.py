#!/usr/bin/env python


import os.path, sys
import shutil
from PyQt5 import QtWidgets, QtGui
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
from ua.controllers.MultipleFrequencyController import MultipleFrequencyController
from ua.controllers.OutputController import OutputController

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog, open_files_dialog, save_file_dialog
import glob 

from ua. models.EchoesResultsModel import EchoesResultsModel

from .. import resources_path, __version__, title


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
        
        self.multiple_frequencies_controller = MultipleFrequencyController(self.overview_controller, self.correlation_controller, self.arrow_plot_controller, self.app, self.echoes_results_model)
        multiple_frequencies_widget = self.multiple_frequencies_controller.widget

        self.output_controller = OutputController(self.overview_controller, self.correlation_controller, self.arrow_plot_controller, self.app, self.echoes_results_model)
        output_widget = self.output_controller.widget


        self.widget = TimeOfFlightWidget(app, overview_widget, multiple_frequencies_widget, analysis_widget, arrow_plot_widget, output_widget)
        self.widget.setWindowTitle(title)
        
        if app is not None:
            self.setStyle(app)
        
        self.make_connections()
        
    def make_connections(self):  

        self.widget.import_multiple_freq_act.triggered.connect(partial( self.overview_controller.open_btn_callback, 'discrete_f'))
        self.widget.import_broadband_act.triggered.connect(partial( self.overview_controller.open_btn_callback, 'broadband'))
        self.widget.sort_data_act.triggered.connect(self.overview_controller.folder_widget.raise_widget)

        self.widget.proj_close_act.triggered.connect(self.close_project_act_callback)
        self.widget.proj_new_act.triggered.connect(self.new_project_act_callback)
        self.widget.proj_save_act.triggered.connect(self.save_project_act_callback)   
        self.widget.proj_save_as_act.triggered.connect(self.save_project_as_act_callback)
        self.widget.proj_open_act.triggered.connect(self.open_project_act_callback)

        self.widget.export_single_frequency_plot_act.triggered.connect(partial( self.export_overview_act_callback, 0))     
        self.widget.export_single_condition_plot_act.triggered.connect(partial( self.export_overview_act_callback, 1)) 

        self.widget.export_selected_waveform_plot_act.triggered.connect(partial( self.export_correlation_act_callback, -1))  
        self.widget.export_selected_ehcoes_plot_act.triggered.connect(partial( self.export_correlation_act_callback, 0))  
        self.widget.export_filtered_echoes_plot_act.triggered.connect(partial( self.export_correlation_act_callback, 1))
        self.widget.export_correlation_plot_act.triggered.connect(partial( self.export_correlation_act_callback, 2)) 

        self.widget.export_arrow_plot_act.triggered.connect(self.export_arrow_plot_act_callback)  
        
        self.widget.export_results_act.triggered.connect(self.export_results_act_callback)           
   

        self.overview_controller.file_selected_signal.connect(self.file_selected_signal_callback)
        self.overview_controller.folder_selected_signal.connect(self.folder_selected_signal_callback)
        self.overview_controller.freq_settings_changed_signal.connect(self.freq_settings_changed_signal_callback)
        self.overview_controller.cursor_position_signal.connect(self.correlation_controller.sync_cursors)
        self.overview_controller.folders_sorted_signal.connect(self.output_controller.folders_sorted_signal_callback)

        self.correlation_controller.cursor_position_signal.connect(self.overview_controller.sync_cursors)
        self.correlation_controller.correlation_saved_signal.connect(self.correlation_saved_signal_callback)
        self.correlation_controller.wave_type_toggled_signal.connect(self.wave_type_toggled_signal_callback)

        self.arrow_plot_controller.arrow_plot_freq_cursor_changed_signal.connect(self.arrow_plot_freq_cursor_changed_signal_callback)
        self.arrow_plot_controller.arrow_plot_del_clicked_signal.connect(self.arrow_plot_del_clicked_signal_callback)
        self.arrow_plot_controller.arrow_plot_clear_clicked_signal.connect(self.arrow_plot_clear_clicked_signal_callback)

        self.arrow_plot_controller.new_result_calculated_signal.connect(self.new_result_calculated_signal_callback )

        self.output_controller.condition_selected_signal.connect(self.condition_selected_signal_callback)

    ###
    # Project file callbacks
    ###

    def new_project_act_callback(self):
        filename = save_file_dialog(None, "New project file", filter = 'Time of Flight Analysis Project (*.bz;*.json)', warn_overwrite=True)
        if len(filename):
            if os.path.isfile(filename):
                os.rename(filename, filename + '.bak')
            self._open_project(filename)
        
    def open_project_act_callback(self):
        filename = open_file_dialog(None, "Open project file", filter = 'Time of Flight Analysis Project (*.bz;*.json)')
        if os.path.isfile(filename):
            set_ok = self._open_project(filename)

        

    def _open_project(self, filename):
        
        self.close_project_act_callback()
        set_ok = self.echoes_results_model.open_project(filename)
        self.project_menus_enabled(set_ok)
        if not set_ok:
                msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,"Notice","Project file not selected")
                msg.exec()
        else:
            folder = self.echoes_results_model.get_folder()
            mode = self.echoes_results_model.get_mode()
            if os.path.isdir(folder) and len(folder) and len(mode):
                
                QtWidgets.QApplication.processEvents()
                self.overview_controller.set_US_folder(folder=folder, mode=mode)
                return
            if len(folder) and len(mode):
                ret = QtWidgets.QMessageBox.question(self.widget, 'Data folder question', "Data folder not found, select new location?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                yes = ret == QtWidgets.QMessageBox.Yes
                if yes:
                    self.overview_controller.open_btn_callback(mode = mode)
                else:
                    self.close_project_act_callback()
                    msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,"Notice","Project data not available.")
                    msg.exec()
            

    def close_project_act_callback(self):
        self.widget.clear_title()
        self.echoes_results_model.clear()
        self.reset_controllers()
        self.project_menus_enabled(False)

    def save_project_as_act_callback(self):
        new_filename = save_file_dialog(None, "New project file", filter = 'Time of Flight Analysis Project (*.bz;*.json)', warn_overwrite=True)
        if len(new_filename):
            QtWidgets.QApplication.processEvents()
            set_ok = self.echoes_results_model.save_project_as(new_filename)
           
        

    def save_project_act_callback(self):
        self.echoes_results_model.save_project()


    def export_overview_act_callback(self, tab):
        new_filename = save_file_dialog(None, "Export plot as csv", filter = 'Export as (*.csv)', warn_overwrite=True)
        if len(new_filename):
            self.overview_controller.export_plot(new_filename, tab)

    def export_correlation_act_callback(self, tab):
        new_filename = save_file_dialog(None, "Export plot as csv", filter = 'Export as (*.csv)', warn_overwrite=True)
        if len(new_filename):
            self.correlation_controller.export_plot(new_filename, tab)

    def export_arrow_plot_act_callback(self):
        new_filename = save_file_dialog(None, "Export plot as csv", filter = 'Export as (*.csv)', warn_overwrite=True)
        if len(new_filename):
            self.arrow_plot_controller.export_plot(new_filename)

    def export_results_act_callback(self):
        self.output_controller.save_btn_callback()



    def project_menus_enabled(self, state):
        self.widget.import_menu_mnu.setEnabled(state)
        self.widget.export_menu_mnu.setEnabled(state)
        self.widget.sort_data_act.setEnabled(state)
        self.widget.proj_save_act.setEnabled(state)
        self.widget.proj_save_as_act.setEnabled(state)
        self.widget.proj_close_act.setEnabled(state)

    def reset_controllers(self):
        
        self.overview_controller.reset() 
        self.correlation_controller.reset() 
        self.output_controller.reset()
        self.multiple_frequencies_controller.reset()
        self.arrow_plot_controller.reset()  


    ###
    # Overview controller callbacks
    ###

    def freq_settings_changed_signal_callback(self, freq_settings):
        selected_freq = freq_settings['f_selected']
        self.correlation_controller.display_window.freq_ebx.setValue(selected_freq)
        self.multiple_frequencies_controller.update_freq_settings(freq_settings)

    def file_selected_signal_callback(self, data):

        self.multiple_frequencies_controller.file_selected(data)
        condition = data['cond']
        self.output_controller.select_condition(condition)

    
    def folder_selected_signal_callback(self, folder):
        self.widget.setWindowTitle( title + " Data folder: "+ os.path.abspath( folder))

        

        subfolders = copy.copy(self.echoes_results_model.get_folders_sorted())
        self.echoes_results_model.set_folder(folder)
        self.echoes_results_model.set_subfolders(subfolders)
        self.echoes_results_model.load_echoes_from_file()   
        self.echoes_results_model.load_tof_results_from_file()
        saved_echoes_p, saved_echoes_s = self.echoes_results_model.get_echoes()
        self.overview_controller.correlation_echoes_added(saved_echoes_p)
        self.overview_controller.correlation_echoes_added(saved_echoes_s)
        self.overview_controller.re_plot_single_frequency()
        self.overview_controller.re_plot_single_condition()

        self.correlation_controller.clear()
        self.correlation_controller.model.restore_folder_settings(folder)
        self.correlation_controller.sync_widget_controls_with_model_non_signaling()

        echo_type = ''
        if  self.correlation_controller.display_window.p_wave_btn.isChecked():
            echo_type = "P"
        elif self.correlation_controller.display_window.s_wave_btn.isChecked():
            echo_type = "S"

        self.arrow_plot_controller.clear()
        self.arrow_plot_controller.refresh_model()
        #self.arrow_plot_controller.

        self.output_controller.update_conditions()
        self.output_controller.update_tof_results()

        mode = self.echoes_results_model.get_mode()
        if mode == 'broadband':
            index = 1
        else:
            index = 0
        self.multiple_frequencies_controller.widget.mode_tab_widget.setCurrentIndex(index)

    ###
    # Ultrasound controller callbacks
    ##

    def correlation_saved_signal_callback(self, correlation):
        
        correlations = {correlation['filename_waveform']:[correlation]}
        

        
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
        
        cleared = self.echoes_results_model.delete_echoes(clear_info)

        if cleared:
            self.arrow_plot_controller.condition_cleared(clear_info)
            self.overview_controller.condition_cleared(clear_info) 
            self.output_controller.delete_result(clear_info)


    def arrow_plot_freq_cursor_changed_signal_callback(self, cursor_info):
        fname = cursor_info['filename_waveform']
        freq = cursor_info['frequency']
        
        mode = self.echoes_results_model.get_mode()
        if mode == 'discrete_f':
            self.overview_controller. select_fname(fname, freq)
        elif mode == 'broadband':
            self.correlation_controller.set_freq(freq )

    def new_result_calculated_signal_callback(self, package):
        
        self.output_controller.new_result(package)

    ###
    # Output controller callbacks
    ###

    def condition_selected_signal_callback(self, condition):
        conds = self.overview_controller.get_conditions_list()
        ind = conds.index(condition)
        self.overview_controller.widget.cond_scroll.setValue(ind)
        #print(condition)

    ###
    # General stuff
    ###

    

    def preferences_module(self, *args, **kwargs):
        pass


    def show_window(self):
        self.widget.raise_widget()

    def relative_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

                
    def setStyle(self, app):
        from .. import theme 
        from .. import style_path
        self.app = app
        if theme==1:
            WStyle = 'plastique'
            file = open(os.path.join(style_path, "stylesheet.qss"))
            stylesheet = file.read()


            down_arrow_url = self.relative_path("ua/resources/style/angle-down.png").replace("\\", "/")
            up_arrow_url = self.relative_path("ua/resources/style/angle-up.png").replace("\\", "/")

            stylesheet = stylesheet.replace("down_arrow_url", down_arrow_url)
            stylesheet = stylesheet.replace("up_arrow_url", up_arrow_url)
            

            self.app.setStyleSheet(stylesheet)
            file.close()
            self.app.setStyle(WStyle)
        else:
            WStyle = "windowsvista"
            self.app.setStyleSheet(" ")
            #self.app.setPalette(self.win_palette)
            self.app.setStyle(WStyle)