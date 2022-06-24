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
from utilities.utilities import *
from ua.widgets.UltrasoundAnalysisWidget import UltrasoundAnalysisWidget
from ua.widgets.ArrowPlotWidget import ArrowPlotWidget
from ua.models.UltrasoundAnalysisModel import UltrasoundAnalysisModel
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import math

from ua.models.ArrowPlotModel import ArrowPlotModel

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog, open_files_dialog


############################################################

class ArrowPlotController(QObject):

    arrow_plot_freq_cursor_changed_signal = pyqtSignal(dict)

    def __init__(self, app = None):
        super().__init__()
        self.model = ArrowPlotModel()
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

    def cursor_changed_singal_callback(self, *args):
        
        freqs = np.asarray(list(self.model.optima.keys()))
        freq = 1/args[0]
        if freq <= np.amin(freqs):
            part_ind = 0
        elif freq >= np.amax(freqs):
            part_ind = len(freqs)-1
        else:
            part_ind = get_partial_index(freqs, freq)
        ind = int(round(part_ind))
        freq_out = freqs[ind]
        optima = self.model.optima[freq_out]
        fname = optima.filename_waveform
        self.arrow_plot_freq_cursor_changed_signal.emit({'frequency':freq_out, 'filename_waveform':fname})

    def calc_callback(self):
        self.calculate_data()
        self.update_plot()

    def auto_data(self):
        num_pts = len(self.model.optima)
        if num_pts > 2:
            opt = self.get_opt()
            self.model.auto_sort_optima(opt)
            self.calculate_data()
            self.update_plot()
        else: self.error_not_enough_datapoints()
 
    def point_clicked_callback(self, pt):
        f = pt[0]
        t = pt[1]
        opt = self.get_opt()
        self.model.set_optimum(opt, t,f)
        self.update_plot()
        #self.calculate_data()

    def clear_data(self):
        self.line_plots = {}
        self.model.clear()
        self.update_plot()
        self.arrow_plot_window.update_max_line([],[])

    def save_result(self):
        pass
        #filename = self.fname + '.json'
        #self.model.save_result(filename)

    def set_frequency_cursor(self, freq):
        inv_freq = 1/(freq*1e6)
        self.sync_cursors(inv_freq)

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
        opt = self.get_opt()
        xMax, yMax = self.model.get_opt_data_points(opt)
        xData, yData = self.model.get_other_data_points(opt)
        self.arrow_plot_window.update_view(xData,yData)
        self.arrow_plot_window.update_maximums(np.asarray(xMax),np.asarray(yMax))
        if opt in self.line_plots:
            self.arrow_plot_window.update_max_line(*self.line_plots[opt])
        else:
            self.arrow_plot_window.update_max_line([],[])

    def error_not_enough_datapoints(self):
        pass
    

    def calculate_data(self):
        
        num_pts = len(self.model.optima)
        if num_pts > 2:
            opt = self.get_opt()

            indexes = [-3,-2,-1,0,1,2,3]
            X = []
            Y = []
            fits = []
            for i in indexes:
                x, y, fit = self.model.get_line(opt,i)
                fits.append(fit[1])
                X = X +x
                Y = Y+y
                X = X +[np.nan]
                Y = Y+[np.nan]
            self.line_plots[opt] = (np.asarray(X),np.asarray(Y))
            
            s = np.std(np.asarray(fits))
            out = 'Time delay = ' + \
                str(round(sum(np.asarray(fits))/len(fits)*1e6,5)) + \
                    ' microseconds, st.dev. = ' + \
                        str(round(s*1e6,5)) +' microseconds'
            self.arrow_plot_window.output_ebx.setText(out)
        else:
            self.error_not_enough_datapoints()

    '''def load_file(self, filename):
        t, spectrum = read_tek_csv(filename, subsample=4)
        t, spectrum = zero_phase_highpass_filter([t,spectrum],1e4,1)
        return t,spectrum, filename'''
        
    def update_data(self, *args, **kwargs):
        filenames = kwargs.get('filenames', None)
        if filenames is None:
            filenames = open_files_dialog(self.arrow_plot_window, 'Open files',filter='*.json')
        if len(filenames):
            for fname in filenames:
                self.model.add_result_from_file(fname)
            #self.auto_data()
            self.update_plot()

    def set_data_by_dict(self, correlations):
        self.model.set_all_freqs(correlations)
        self.update_plot()

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
