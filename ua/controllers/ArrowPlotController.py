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
from ua.models.UltrasoundAnalysisModel import get_local_optimum, UltrasoundAnalysisModel
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import math

from ua.models.ArrowPlotModel import ArrowPlotModel

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog, open_files_dialog


############################################################

class ArrowPlotController(QObject):
    def __init__(self, app = None):
        super().__init__()
        self.model = ArrowPlotModel()
        if app is not None:
            self.setStyle(app)
        self.arrow_plot_window = ArrowPlotWidget()
        self.make_connections()
        
       

    def make_connections(self): 
        self.arrow_plot_window.open_btn.clicked.connect(self.update_data)
        self.arrow_plot_window.clear_btn.clicked.connect(self.clear_data)
        self.arrow_plot_window.N_cbx.stateChanged.connect(self.calculate_data)
        self.arrow_plot_window.point_clicked_signal.connect(self.point_clicked_callback)
        self.arrow_plot_window.save_btn.clicked.connect(self.save_result)

 
    def point_clicked_callback(self, pt):
        f = pt[0]
        t = pt[1]
        N = self.arrow_plot_window.N_cbx.checkState()
        if N:
            opt = 'max'
        else: 
            opt = 'min'
        self.model.set_optimum(opt, t,f)
        self.calculate_data()

    def clear_data(self):
        self.model.clear()
        self.calculate_data()

    def save_result(self):
        filename = self.fname + '.json'
        self.model.save_result(filename)


    def sync_cursors(self, pos):
        self.display_window.win.fig.set_cursor(pos)
        self.display_window.detail_win1.fig.set_cursor(pos)

    def calculate_data(self):
        N = self.arrow_plot_window.N_cbx.checkState()
        if N:
            opt = 'max'
        else: 
            opt = 'min'

        xMax, yMax = self.model.get_opt_data_points(opt)
        
        xData, yData = self.model.get_other_data_points(opt)
        self.arrow_plot_window.update_view(xData,yData)

        self.arrow_plot_window.update_maximums(np.asarray(xMax),np.asarray(yMax))

        indexes = [-3,-2,-1,0,1,2,3]
        X = []
        Y = []
        for i in indexes:
            try:
                x, y = self.model.get_line(opt,i)
                X = X +x
                Y = Y+y
                X = X +[np.nan]
                Y = Y+[np.nan]
            except:
                pass
        self.arrow_plot_window.update_max_line(np.asarray(X),np.asarray(Y))
 
    def load_file(self, filename):
        
        t, spectrum = read_tek_csv(filename, subsample=4)
        t, spectrum = zero_phase_highpass_filter([t,spectrum],1e4,1)
        return t,spectrum, filename
        
    def update_data(self, *args, **kwargs):
        filenames = kwargs.get('filenames', None)
        if filenames is None:
            filenames = open_files_dialog(self.arrow_plot_window, 'Open files',filter='*.json')
        if len(filenames):
            for fname in filenames:
                self.model.add_result_from_file(fname)

            self.calculate_data()

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
                
    def show_latest_waveform(self):
        pass
    

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