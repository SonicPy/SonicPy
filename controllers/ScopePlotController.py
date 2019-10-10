

import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import time
from models.ScopeModel import Scope
from models.DPO5104 import Scope_DPO5104
import json
from widgets.scope_widget import scopeWidget

from widgets.panel import Panel
from functools import partial
from widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from controllers.pv_controller import pvController
from controllers.ScopeController import ScopeController
from utilities.utilities import *


class ScopePlotController(QObject):
    callbackSignal = pyqtSignal(dict)  
    stoppedSignal = pyqtSignal()
    fastCursorMovedSignal = pyqtSignal(str)  
    staticCursorMovedSignal = pyqtSignal(str) 

    def __init__(self, scope_controller=None, isMain = False):
        super().__init__()
        self.widget = scopeWidget()
        self.pg = self.widget.plot_widget.fig.win
        
        if scope_controller is None:
            scope_controller = ScopeController(self.widget, isMain=True)
        self.scope_controller = scope_controller
        if isMain:
            self.show_widget()

        self.make_connections()

    def make_connections(self):
        self.widget.start_stop_btn.clicked.connect(lambda:self.start_stop_btn_callback(self.widget.start_stop_btn.isChecked()))
        self.widget.erase_btn.clicked.connect(self.erase_btn_callback)
        self.widget.save_btn.clicked.connect(self.save_data_callback)
        self.scope_controller.runStateSignal.connect(self.run_state_callback)
        self.scope_controller.dataUpdatedSignal.connect(self.waveform_updated_signal_callback)
        self.scope_controller.dataBGUpdatedSignal.connect(self.bg_waveform_updated_signal_callback)

        
    
    
    def start_stop_btn_callback(self, state):
  
        if state:
            self.scope_controller.model.pvs['run_state'].set(True)
            channel_state = self.scope_controller.model.pvs['channel_state']._val
            if not channel_state:
                self.scope_controller.model.pvs['channel_state'].set(True)
            self.get_waveform()
        else:
            self.scope_controller.model.pvs['run_state'].set(False)
            self.scope_controller.stoppedSignal.emit()

    def get_waveform(self):
        if self.scope_controller.model.connected:
            self.scope_controller.model.pvs['waveform'].get()

    def run_state_callback(self, state):
        self.widget.blockSignals(True)
        self.widget.start_stop_btn.setChecked(state)
        self.widget.blockSignals(False)

    def widgetSetEnabled(self, state):
        self.widget.button_widget.setEnabled(state)
        
    def waveform_updated_signal_callback(self, waveform_data):
        data = waveform_data
        self.waveform_data = data
        waveform  = data['waveform']
        '''
        if len(waveform):
            self.widget.save_btn.setDisabled(False)
        '''
        ch = data['ch']
        filtered = zero_phase_bandstop_filter(waveform, 100e6, 340e6, 5)
        #filtered = zero_phase_bandpass_filter(filtered,30e6-30e6*0.05,30e6+30e6*0.05,1)
        #ff = fft_sig(*filtered)
        self.update_plot(filtered)
        #self.update_bg_plot(waveform)
        elapsed = data['transfer_time']
        num_acq = data['num_acq']
        self.widget.status_lbl.setText(str(num_acq))
        #dt = data['time']
        #status = 'Date/Time: ' + dt + '; Transfer time: ' + str(round(elapsed,3))
        #self.widget.status_lbl.setText(status)
        if self.widget.start_stop_btn.isChecked():
            time.sleep(0.01)
            self.get_waveform()
            pass

    def bg_waveform_updated_signal_callback(self, waveform_data):
        data = waveform_data
        self.waveform_bg_data = data
        waveform  = data['waveform']
        start = time.time()
        filtered = zero_phase_bandstop_filter(waveform, 100000000, 340000000, 5)
        
        end = time.time()
        elapsed = end - start
        self.update_bg_plot(filtered)
     
    def load_background_callback(self, *args, **kwargs):
        if 'folder' in kwargs:
            folder = kwargs['folder']
        else:
            folder = None

        if not 'filename' in kwargs:
            filename = open_file_dialog(
                            self.widget, "Open waveform",directory=folder,
                            filter=self.scope_controller.model.file_filter)
        else:
            filename = kwargs['filename']
        if filename is not '':
            self.scope_controller.model.read_file(filename)
            folder = os.path.dirname(str(filename)) 
        return folder

    def save_data_callback(self, *args, **kwargs):
        filename = ''
        if self.scope_controller.waveform_data is not None:
            if 'folder' in kwargs:
                folder = kwargs['folder']
            else:
                folder = None
            if not 'filename' in kwargs:
                filename = save_file_dialog(
                                self.widget, "Save waveform",directory=folder,
                                filter=self.scope_controller.model.file_filter)
            else:
                filename = kwargs['filename']
            if filename is not '':
                if 'params' in kwargs:
                    params = kwargs['params']
                    self.scope_controller.model.pvs['params'].set(params)
                else:
                    self.scope_controller.model.pvs['params'].set({})
                self.scope_controller.model.pvs['filename'].set(filename)
                self.scope_controller.model.pvs['save'].set(True)

    
    def close_background_callback(self):
        self.update_bg_plot([[],[]])

    def update_bg_plot(self, waveform):
        if waveform is not None:
            self.widget.plot_bg(waveform)

    def update_plot(self, waveform):
        if waveform is not None:
            self.widget.plot(waveform)

    def update_filtered_plot(self, waveform):
        if waveform is not None:
            self.widget.plot_filtered(waveform)


    def erase_btn_callback(self):
        self.scope_controller.model.pvs['erase'].set(True)

    def show_widget(self):
        self.widget.raise_widget()

