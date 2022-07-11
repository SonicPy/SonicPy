#!/usr/bin/env python



import os.path, sys
import wave
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
from ua.models.UltrasoundAnalysisModel import UltrasoundAnalysisModel
from um.models.tek_fileIO import load_any_waveform_file 
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import math, time

from ua.controllers.ArrowPlotController import ArrowPlotController
from functools import partial

#from um.models.WaveformModel import Waveform

#from um.controllers.PhaseController import PhaseController


#import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog

from ua.models.EchoesResultsModel import EchoesResultsModel

############################################################

class UltrasoundAnalysisController(QObject):
    cursor_position_signal = pyqtSignal(float)
    correlation_saved_signal = pyqtSignal(dict)
    wave_type_toggled_signal = pyqtSignal(str)

    def __init__(self, app=None, results_model= EchoesResultsModel()):
        super().__init__()
        self.model = UltrasoundAnalysisModel(results_model)
        self.fname = None
    
        if app is not None:
            self.setStyle(app)
        self.display_window = UltrasoundAnalysisWidget()
        
        self.make_connections()
       
        
        '''filename='resources/ultrasonic/4000psi-300K_+21MHz000.csv'
        self.update_data(filename=filename)'''

    def make_connections(self): 
        self.display_window.open_btn.clicked.connect(self.update_data)
        self.display_window.freq_ebx.valueChanged.connect(self.calculate_data)
        self.display_window.lr1_p.sigRegionChangeFinished.connect(self.calculate_data)
        self.display_window.lr2_p.sigRegionChangeFinished.connect(self.calculate_data)

        self.display_window.lr1_s.sigRegionChangeFinished.connect(self.calculate_data)
        self.display_window.lr2_s.sigRegionChangeFinished.connect(self.calculate_data)

        self.display_window.N_cbx.stateChanged.connect(self.calculate_data)

        self.display_window.plot_widget.cursor_changed_singal.connect(self.sync_cursors)
        self.display_window.detail_win0.cursor_changed_singal.connect(self.sync_cursors)
        self.display_window.detail_win1.cursor_changed_singal.connect(self.sync_cursors)

        self.display_window.plot_widget.cursor_changed_singal.connect(self.emit_cursor)
        self.display_window.detail_win0.cursor_changed_singal.connect(self.emit_cursor)
        self.display_window.detail_win1.cursor_changed_singal.connect(self.emit_cursor)
        

        self.display_window.save_btn.clicked.connect(self.save_result)

       
        

        self.display_window.echo1_cursor_btn.clicked.connect(partial(self.set_echo_region_position,0))
        self.display_window.echo2_cursor_btn.clicked.connect(partial(self.set_echo_region_position,1))
    
        self.display_window.p_wave_btn.clicked.connect(partial(self.p_s_wave_btn_callback,'P'))
        self.display_window.s_wave_btn.clicked.connect(partial(self.p_s_wave_btn_callback,'S'))


    def p_s_wave_btn_callback(self, wave_type):
        self.display_window.plot_win.removeItem(self.display_window.lr1_s)
        self.display_window.plot_win.removeItem(self.display_window.lr2_s)
        self.display_window.plot_win.removeItem(self.display_window.lr1_p)
        self.display_window.plot_win.removeItem(self.display_window.lr2_p)

        if wave_type == 'P':
            
            self.display_window.plot_win.addItem(self.display_window.lr1_p)
            self.display_window.plot_win.addItem(self.display_window.lr2_p)
        if wave_type == 'S':
            self.display_window.plot_win.addItem(self.display_window.lr1_s)
            self.display_window.plot_win.addItem(self.display_window.lr2_s)

        self.model.wave_type = wave_type
        self.calculate_data()

        self.wave_type_toggled_signal.emit(wave_type)

    

    def save_result(self):
        if self.fname is not None:
            filename = self.fname + '.json'
            out = self.model.save_result(self.fname)
            if out['ok']: 
                self.correlation_saved_signal.emit(out['data'])


    def emit_cursor(self, pos):
        self.cursor_position_signal.emit(pos)

    def sync_cursors(self, pos):
        
        
        self.display_window.plot_widget.fig.set_cursor(pos)
        self.display_window.plot_widget.cursor_pos = pos
        self.display_window.detail_win0.fig.set_cursor(pos)
        self.display_window.detail_win0.cursor_pos = pos
        self.display_window.detail_win1.fig.set_cursor(pos)
        self.display_window.detail_win1.cursor_pos = pos


    def set_echo_region_position(self, index):
        center = self.display_window.plot_widget.cursor_pos
        pad = 0.06e-6
        wave_type = self.model.wave_type
        if wave_type == 'P':
            echo = self.display_window.echo_bounds_p[index]
            echo.setRegion([center-pad, center+pad])
        elif wave_type == 'S':
            echo = self.display_window.echo_bounds_s[index]
            echo.setRegion([center-pad, center+pad])
        

    def calculate_data(self):

        freq = self.display_window.freq_ebx.value()*1e6
        
        t = self.model.t
        spectrum = self.model.spectrum

        

        if t is not None and spectrum is not None:
                
            min_roi = abs(t[1]-t[0])*10

            wave_type = self.model.wave_type
            if wave_type == 'P':
                [l1, r1] = self.display_window.get_echo_bounds_p(0)
                [l2, r2] = self.display_window.get_echo_bounds_p(1)
            elif wave_type == 'S':
                [l1, r1] = self.display_window.get_echo_bounds_s(0)
                [l2, r2] = self.display_window.get_echo_bounds_s(1)
            
            if l1 >  0 and l2 >0 and abs(l1-r1) > min_roi and abs(l2-r2) > min_roi:

                
                
                start_time = time.time()
                self.model.filter_echoes(l1, r1, l2, r2, freq)

                self.model.cross_correlate()
                self.model.exract_optima()

                
               

                self.display_window.detail_plot0.setData(*self.model.echo_tk1)
                self.display_window.detail_plot0_bg.setData(*self.model.echo_tk2)
                
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

        t, spectrum = load_any_waveform_file(filename)
        
        return t,spectrum, filename

    def update_data(self, *args, **kwargs):
        filename = kwargs.get('filename', None)
        if filename is None:
            filename = open_file_dialog(None, "Load File(s).")
        if len(filename):
            t, spectrum, fname = self.load_file(filename)

            if len(spectrum):
                self._update_spectrum (t, spectrum, fname)

    def update_data_by_dict(self, data):
        t, spectrum, fname = data['t'], data['spectrum'], data['fname']
        self._update_spectrum(t, spectrum, fname)
        
    def _update_spectrum(self, t, spectrum, fname):
        
        if len(spectrum):

            self.model.t, self.model.spectrum, self.fname = t, spectrum, fname
            #freq = self.display_window.freq_ebx.value()
            #amplitude_envelope  =  demodulate(t, spectrum, freq, True)
            #self.model.demodulated = amplitude_envelope
            self.display_window.update_view(self.model.t, self.model.spectrum, self.fname)
            #self.display_window.update_demodulated(t, self.model.demodulated)
            

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
