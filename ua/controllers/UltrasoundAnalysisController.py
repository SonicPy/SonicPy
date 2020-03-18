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
from ua.models.UltrasoundAnalysisModel import get_local_optimum, UltrasoundAnalysisModel
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import math



from um.models.WaveformModel import Waveform

from um.controllers.PhaseController import PhaseController


import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog
from .. import style_path


############################################################

class UltrasoundAnalysisController(QObject):
    def __init__(self, app, _platform, theme, offline = False):
        super().__init__()
        self.model = UltrasoundAnalysisModel()
        
        self.style_path = style_path

        self.app = app
        
        self.setStyle(theme)
        self.display_window = UltrasoundAnalysisWidget(app, _platform, theme)
        self.make_connections()
        self.display_window.raise_widget()
        
       

    def make_connections(self): 
        self.display_window.open_btn.clicked.connect(self.update_data)
        self.display_window.calc_btn.clicked.connect(self.calculate_data)

    def calculate_data(self):
        t = self.model.t
        spectrum = self.model.spectrum
        t_f, spectrum_f = zero_phase_lowpass_filter([t,spectrum],60e6,1)
        #pg.plot(np.asarray(spectrum_f), title="spectrum_f")
        c1 = self.display_window.plot_win_detail1.get_cursor_pos()
        c2 = self.display_window.plot_win_detail2.get_cursor_pos()
        optima_x_1, optima_x_2, optima_y_1, optima_y_2 = self.snap_cursors_to_optimum(c1, c2,t_f, spectrum_f)
        self.display_window.plot_win_detail1.set_cursor_pos(optima_x_1[0])
        self.display_window.plot_win_detail2.set_cursor_pos(optima_x_2[0])
        c1 = self.display_window.plot_win_detail1.get_cursor_pos()
        c2 = self.display_window.plot_win_detail2.get_cursor_pos()

        self.model.calculate_data(c1,c2)

        self.display_window.detail_plot1_bg.setData(*self.model.plot1_bg)
        self.display_window.detail_plot2_bg.setData(*self.model.plot2_bg)
        
        self.display_window.output_ebx.setText('%.5e' % (self.model.c_diff_optimized))


    def snap_cursors_to_optimum(self, c1, c2, t, spectrum):
        cor_range = 50
        pilo1 = int(get_partial_index(t,c1))-int(cor_range/2)
        pihi1 = int(get_partial_index(t,c1))+int(cor_range/2)
        pilo2 = int(get_partial_index(t,c2))-int(cor_range/2)
        pihi2 = int(get_partial_index(t,c2))+int(cor_range/2)
        slice1 = np.asarray(spectrum)[pilo1:pihi1]
        #pg.plot(np.asarray(slice1), title="slice1")
        t1 = np.asarray(t)[pilo1:pihi1]
        slice2 = np.asarray(spectrum)[pilo2:pihi2]
        #pg.plot(np.asarray(slice1), title="slice1")
        t2 = np.asarray(t)[pilo2:pihi2]
        (optima_x_1, optima_y_1), optima_type_1 = get_local_optimum (c1, t1, slice1)
        (optima_x_2, optima_y_2), optima_type_2 = get_local_optimum (c2, t2, slice2)
        return optima_x_1, optima_x_2, optima_y_1, optima_y_2

    def cursorsCallback(self):
        pass
        

    def RecallSetupCallback(self):
        print('RecallSetupCallback')

    def SaveSetupCallback(self):
        print('SaveSetupCallback')

 
    def preferences_module(self, *args, **kwargs):
        pass

  

    def saveFile(self, filename, params = {}):
        pass

 
    def load_file(self):
        filename = open_file_dialog(None, "Load File(s).",filter='*.csv')
        if len(filename):
            t, spectrum = read_tek_csv(filename, subsample=4)
            t, spectrum = zero_phase_highpass_filter([t,spectrum],1e4,1)
            return t,spectrum, filename
        else:
            return None, None, filename



    def update_data(self):
        
        self.model.t, self.model.spectrum, self.fname = self.load_file()
        self.display_window.update_view(self.model.t, self.model.spectrum, self.fname)
    

    def panel_closed_callback(self):
        pass

    def show_window(self):
        self.display_window.raise_widget()

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
        freqs = sorted(list(self.model.sweep.keys()))
        freq = freqs[-1]
        ind = freqs.index(freq)
        self.show_waveform(ind, update_cursor_pos=True)

    

    def setStyle(self, Style):
        print('style:  ' + str(Style))
        if Style==1:
            WStyle = 'plastique'
            file = open(os.path.join(self.style_path, "stylesheet.qss"))
            stylesheet = file.read()
            self.app.setStyleSheet(stylesheet)
            file.close()
            self.app.setStyle(WStyle)
        else:
            WStyle = "windowsvista"
            self.app.setStyleSheet(" ")
            #self.app.setPalette(self.win_palette)
            self.app.setStyle(WStyle)