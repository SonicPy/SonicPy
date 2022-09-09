#!/usr/bin/env python



import os.path, sys
import wave
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
from functools import partial
import json
import copy
from pathlib import Path
from numpy import arange
from utilities.utilities import *
from ua.widgets.UltrasoundAnalysisWidget import UltrasoundAnalysisWidget
from ua.widgets.ArrowPlotWidget import ArrowPlotWidget
from ua.models.UltrasoundAnalysisModel import UltrasoundAnalysisModel
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import math

from ua.models.ArrowPlotModel import ArrowPlotsModel

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog, open_files_dialog
from ua.models.EchoesResultsModel import EchoesResultsModel

############################################################

class ArrowPlotController(QObject):

    arrow_plot_freq_cursor_changed_signal = pyqtSignal(dict)
    arrow_plot_del_clicked_signal = pyqtSignal(dict)
    arrow_plot_clear_clicked_signal = pyqtSignal(dict) # contains list of del type dicts

    new_result_calculated_signal = pyqtSignal(dict)

    def __init__(self, app = None, results_model= EchoesResultsModel()):
        super().__init__()
        
        self.model = ArrowPlotsModel(results_model)
        self.cond = None
        self.wave_type = 'P'
        if app is not None:
            self.setStyle(app)
        self.arrow_plot_window = ArrowPlotWidget()
        self.make_connections()
        self.line_plots = {}
        
    def make_connections(self): 
        self.arrow_plot_window.open_btn.clicked.connect(self.update_data)
        self.arrow_plot_window.auto_btn.clicked.connect(self.auto_data)
        self.arrow_plot_window.calc_btn.clicked.connect(self.calc_callback)
        self.arrow_plot_window.clear_btn.clicked.connect(self.clear_data)
        self.arrow_plot_window.N_cbx.stateChanged.connect(self.update_plot)
        self.arrow_plot_window.point_clicked_signal.connect(self.point_clicked_callback)
        #self.arrow_plot_window.save_btn.clicked.connect(self.save_result)
        self.arrow_plot_window.win.cursor_changed_singal.connect(self.cursor_changed_singal_callback)
        self.arrow_plot_window.del_btn.clicked.connect(self. del_btn_callback)

    def del_btn_callback(self):
        arrow_plot = self.model.get_arrow_plot(self.cond, self.wave_type)
        if arrow_plot != None:
            freq = round(1/self. arrow_plot_window.get_cursor_pos(),1)
            if freq in arrow_plot.optima:
                fname = arrow_plot.optima[freq].filename_waveform
                wave_type = arrow_plot.optima[freq].wave_type
                self.arrow_plot_del_clicked_signal.emit({'frequency':freq, 'filename_waveform':fname, 'wave_type': wave_type})

    def echo_deleted(self, del_info):
        
        fname = del_info['filename_waveform']
        freq = del_info['frequency']
        wave_type = del_info['wave_type']
        self. model.delete_optima(self.cond, wave_type, freq)

        self.update_plot()

    def condition_cleared(self, clear_info):

        
        self.model.clear_condition(clear_info)
        self.update_plot()

    def cursor_changed_singal_callback(self, *args):
        
        arrow_plot = self.model.get_arrow_plot(self.cond, self.wave_type)
        if arrow_plot != None:
            freqs = np.asarray(list(arrow_plot.optima.keys()))
            freq = 1/args[0]
            if len(freqs):
                if freq <= np.amin(freqs): 
                    part_ind = 0
                elif freq >= np.amax(freqs):
                    part_ind = len(freqs)-1
                else:
                    part_ind = get_partial_index(freqs, freq)
                ind = int(round(part_ind))
                if ind < len(freqs):
                    freq_out = freqs[ind]
                    optima = arrow_plot.optima[freq_out]
                    fname = optima.filename_waveform
                    self.arrow_plot_freq_cursor_changed_signal.emit({'frequency':freq_out, 'filename_waveform':fname})

    def calc_callback(self):
        self.calculate_data()
        self.update_plot()

    def auto_data(self):
        # starts the automatic point sorting and finding the most horizontal line, the 
        # most horizontal points are the opt_data_points, other points are the other_data_points

        arrow_plot = self.model.get_arrow_plot(self.cond, self.wave_type)
        if arrow_plot != None:
            num_pts = len(arrow_plot.optima)
            if num_pts > 2:
                opt = self.get_opt()
                arrow_plot.auto_sort_optima(opt)
                self.calculate_data()
                self.update_plot()
            else: self.error_not_enough_datapoints()
 
    def point_clicked_callback(self, pt):
        arrow_plot = self.model.get_arrow_plot(self.cond, self.wave_type)
        if arrow_plot != None:
            f = pt[0]
            t = pt[1]
            opt = self.get_opt()
            arrow_plot.set_optimum(opt, t,f)
            self.update_plot()
            #self.calculate_data()

    def clear_data(self):

        arrow_plot = self.model.get_arrow_plot(self.cond, self.wave_type)
      
        wave_type = self.wave_type

        clear_info = []

        for freq in arrow_plot.optima:
            fname = arrow_plot.optima[freq].filename_waveform
            wave_type = arrow_plot.optima[freq].wave_type
            clear_info.append({'frequency':freq, 'filename_waveform':fname, 'wave_type': wave_type, 'condition':self.cond})

        self.arrow_plot_clear_clicked_signal.emit({'condition':self.cond,'wave_type':wave_type, 'clear_info':clear_info})

    def save_result(self):
        pass
        #filename = self.fname + '.json'
        #self.model.save_result(filename)

    def set_frequency_cursor(self, freq):
        inv_freq = 1/(freq*1e6)
        self.sync_cursors(inv_freq)

        self.arrow_plot_window.set_selected_frequency(str(freq)+ ' MHz')

    def sync_cursors(self, pos):
        self.arrow_plot_window.win.blockSignals(True)
        self.arrow_plot_window.win.update_cursor(pos)
        self.arrow_plot_window.win.blockSignals(False)

    def get_opt(self):
        N = self.arrow_plot_window.N_cbx.checkState()
        if N:
            opt = 'max'
        else: 
            opt = 'min'
        return opt

    def update_plot(self):
        arrow_plot = self.model.get_arrow_plot(self.cond, self.wave_type)
        
        if arrow_plot != None:
            opt = self.get_opt()
            xMax, yMax = arrow_plot.get_opt_data_points(opt)
            xData, yData = arrow_plot.get_other_data_points(opt)


            self.arrow_plot_window.update_view(xData,yData)
            self.arrow_plot_window.update_maximums(np.asarray(xMax),np.asarray(yMax))

            self.arrow_plot_window.set_selected_folder(str(self.cond))

            if opt in arrow_plot.line_plots:
                self.arrow_plot_window.update_max_line(*arrow_plot.line_plots[opt])
                
                result = arrow_plot.result[opt]
                out_str = 'Time delay = ' + \
                            str(result['time_delay']) + \
                                ' microseconds, st.dev. = ' + \
                                    str(result['time_delay_std']) +' microseconds'
                self.arrow_plot_window.output_ebx.setText(out_str)
            else:
                self.arrow_plot_window.update_max_line([],[])
                self.arrow_plot_window.output_ebx.setText('')
            
          
            

    def error_not_enough_datapoints(self):
        pass
    

    def calculate_data(self):
        arrow_plot = self.model.get_arrow_plot(self.cond, self.wave_type)
        if arrow_plot != None:
            opt = self.get_opt()
            arrow_plot.calculate_lines(opt)
            package = arrow_plot.package
            package['wave_type']= self.wave_type
            self.new_result_calculated_signal.emit(package)


    '''def load_file(self, filename):
        t, spectrum = read_tek_csv(filename, subsample=4)
        t, spectrum = zero_phase_highpass_filter([t,spectrum],1e4,1)
        return t,spectrum, filename'''
        
    def update_data(self, *args, **kwargs):
        if self.cond != None:
            
            filenames = kwargs.get('filenames', None)
            if filenames is None:
                filenames = open_files_dialog(self.arrow_plot_window, 'Open files',filter='*.json')
            if len(filenames):
                for fname in filenames:
                    self.model.add_result_from_file(self.cond,fname)
                #self.auto_data()
                self.update_plot()

    

    def refresh_model(self):
        self.model.refresh_all_freqs(self.cond, self.wave_type)
        self.update_plot()

    def set_condition(self, cond):
        self.cond = cond

    def set_wave_type(self, wave_type):
        self.wave_type = wave_type

    def show_window(self):
        self.arrow_plot_window.raise_widget()

    def cursor_dragged(self, cursor):
        pos = cursor.getYPos()
        c1 = self.display_window.hLine1
        c2 = self.display_window.hLine2
        
        ind = int(math.floor(pos))
        self.show_waveform(ind)
        if c1 is not cursor:
            c1.setPos(pos)
        if c2 is not cursor:
            c2.setPos(pos)

    def up_down_signal_callback(self, event):
        new_ind = self.waveform_index
        if event == 'up':
            new_ind = self.waveform_index + 1
        if event == 'down':
            new_ind = self.waveform_index - 1
        self.show_waveform(new_ind, update_cursor_pos=True)
                
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
