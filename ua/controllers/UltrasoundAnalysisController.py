#!/usr/bin/env python



import os.path, sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
#from functools import partial
#import json
#import copy
##from pathlib import Path
from numpy import arange
from utilities.utilities import *
from ua.widgets.UltrasoundAnalysisWidget import UltrasoundAnalysisWidget
from ua.widgets.ArrowPlotWidget import ArrowPlotWidget
from ua.models.UltrasoundAnalysisModel import get_local_optimum, UltrasoundAnalysisModel
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import math, time

from ua.controllers.ArrowPlotController import ArrowPlotController
from functools import partial

#from um.models.WaveformModel import Waveform

#from um.controllers.PhaseController import PhaseController


#import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog



############################################################

class UltrasoundAnalysisController(QObject):
    cursor_position_signal = pyqtSignal(float)
    correlation_saved_signal = pyqtSignal(dict)
    def __init__(self, app=None, offline = False):
        super().__init__()
        self.model = UltrasoundAnalysisModel()
        self.fname = None
    
        if app is not None:
            self.setStyle(app)
        self.display_window = UltrasoundAnalysisWidget()
        self.arrow_plot_controller = ArrowPlotController()
        self.make_connections()
       
        
        '''filename='resources/ultrasonic/4000psi-300K_+21MHz000.csv'
        self.update_data(filename=filename)'''

    def make_connections(self): 
        self.display_window.open_btn.clicked.connect(self.update_data)
        self.display_window.freq_ebx.valueChanged.connect(self.calculate_data)
        self.display_window.lr1.sigRegionChangeFinished.connect(self.calculate_data)
        self.display_window.lr2.sigRegionChangeFinished.connect(self.calculate_data)
        self.display_window.N_cbx.stateChanged.connect(self.calculate_data)

        self.display_window.plot_widget.cursor_changed_singal.connect(self.sync_cursors)
        self.display_window.detail_win1.cursor_changed_singal.connect(self.sync_cursors)
        self.display_window.plot_widget.cursor_changed_singal.connect(self.emit_cursor)
        self.display_window.detail_win1.cursor_changed_singal.connect(self.emit_cursor)

        self.display_window.save_btn.clicked.connect(self.save_result)

       
        self.display_window.arrow_plt_btn.clicked.connect(self.ArrowPlotShow)

        self.display_window.echo1_cursor_btn.clicked.connect(partial(self.set_echo_region_position,0))
        self.display_window.echo2_cursor_btn.clicked.connect(partial(self.set_echo_region_position,1))
    
        self.display_window.p_wave_btn.clicked.connect(partial(self.p_s_wave_btn_callback,'P'))
        self.display_window.s_wave_btn.clicked.connect(partial(self.p_s_wave_btn_callback,'S'))


    def p_s_wave_btn_callback(self, wave_type):
        self.model.wave_type = wave_type

    def ArrowPlotShow(self):
        self.arrow_plot_controller.arrow_plot_window.raise_widget()

    def save_result(self):
        if self.fname is not None:
            filename = self.fname + '.json'
            out = self.model.save_result(self.fname)
            if out['saved']:
                self.correlation_saved_signal.emit(out['data'])


    def emit_cursor(self, pos):
        self.cursor_position_signal.emit(pos)

    def sync_cursors(self, pos):
        
        
        self.display_window.plot_widget.fig.set_cursor(pos)
        self.display_window.plot_widget.cursor_pos = pos
        self.display_window.detail_win1.fig.set_cursor(pos)
        self.display_window.detail_win1.cursor_pos = pos


    def set_echo_region_position(self, index):
        center = self.display_window.plot_widget.cursor_pos
        pad = 0.06e-6
        echo = self.display_window.echo_bounds[index]
        echo.setRegion([center-pad, center+pad])
        

    def calculate_data(self):

        freq = self.display_window.freq_ebx.value()*1e6
        
        t = self.model.t
        spectrum = self.model.spectrum
        if t is not None and spectrum is not None:

            t_f, spectrum_f = zero_phase_lowpass_filter([t,spectrum],60e6,1)
            min_roi = abs(t_f[1]-t_f[0])*10
            [l1, r1] = self.display_window.get_echo_bounds(0)
            [l2, r2] = self.display_window.get_echo_bounds(1)
            if l1 >  0 and l2 >0 and abs(l1-r1) > min_roi and abs(l2-r2) > min_roi:

                #pg.plot(np.asarray(spectrum_f), title="spectrum_f")
                
                start_time = time.time()
                self.model.filter_echoes(l1, r1, l2, r2, freq)

                self.model.cross_correlate()
                self.model.exract_optima()
                print("cross correlated in %s seconds." % (time.time() - start_time))

                self.display_window.detail_plot1.setData(*self.model.filtered1)
                self.display_window.detail_plot1_bg.setData(*self.model.filtered2)
                self.display_window.detail_plot2.setData(self.model.cross_corr_shift, self.model.cross_corr)

            
                
                out = [np.append(self.model.maxima[0] ,self.model.minima[0]) , np.append(self.model.maxima[1] ,self.model.minima[1])]
                
                self.display_window.detail_plot2_bg.setData(*out)
                #self.display_window.output_ebx.setText('%.5e' % (self.model.c_diff_optimized))
            

    '''def snap_cursors_to_optimum(self, c1, c2, t, spectrum):
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
        return optima_x_1, optima_x_2, optima_y_1, optima_y_2'''

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

 
    def load_file(self, filename):
        
        t, spectrum = read_tek_csv(filename, subsample=1)
        t, spectrum = zero_phase_highpass_filter([t,spectrum],1e4,1)
        return t,spectrum, filename
        
    def update_data(self, *args, **kwargs):
        filename = kwargs.get('filename', None)
        if filename is None:
            filename = open_file_dialog(None, "Load File(s).",filter='*.csv')
        if len(filename):


            self.model.t, self.model.spectrum, self.fname = self.load_file(filename)
            self.display_window.update_view(self.model.t, self.model.spectrum, self.fname)
            

            path = os.path.normpath(self.fname)
            fldr = path.split(os.sep)[-2]
            file = path.split(os.sep)[-1]
            name = os.path.join( fldr,file)
            self.display_window.plot_widget.setText(name,0)

    


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