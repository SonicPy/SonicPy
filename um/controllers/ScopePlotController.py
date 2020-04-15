

import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import time
from um.models.ScopeModel import Scope
from um.models.DPO5104 import Scope_DPO5104
import json
from um.widgets.scope_widget import scopeWidget

from um.widgets.panel import Panel
from functools import partial
from um.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from um.controllers.pv_controller import pvController
from um.controllers.ScopeController import ScopeController
from utilities.utilities import *
from um.models.pvServer import pvServer


class ScopePlotController(QObject):
    callbackSignal = pyqtSignal(dict)  
    stoppedSignal = pyqtSignal()
    fastCursorMovedSignal = pyqtSignal(str)  
    staticCursorMovedSignal = pyqtSignal(str) 
    dataPlotUpdated = pyqtSignal()

    def __init__(self, scope_controller=None, afg_controller=None, save_data_controller = None, isMain = False):
        super().__init__()
        self.pv_server = pvServer()
        if scope_controller is None:
            self.widget = scopeWidget()
            scope_controller = ScopeController(self.widget, isMain=True)
        self.scope_controller = scope_controller
        btn_erase, _ = self.scope_controller.make_pv_widget('DPO5104:erase')
        btn_on_off, _ = self.scope_controller.make_pv_widget('DPO5104:run_state')
        
        self.save_data_controller= save_data_controller
        btn_save, _ = self.save_data_controller.make_pv_widget('SaveData:save')

        self.widget = scopeWidget([btn_erase,btn_on_off, 'spacer', btn_save])
        self.pg = self.widget.plot_widget.fig.win
        if isMain:
            self.show_widget()

        self.afg_controller = afg_controller
        self.plt = self.widget.plot_widget.fig.win

        self.make_connections()

    def make_connections(self):
        if self.afg_controller is not None:
            self.afg_controller.model.pvs['user1_waveform'].value_changed_signal.connect(self.user1_waveform_changed_callback)
        
        
        self.scope_controller.dataUpdatedSignal.connect(self.waveform_updated_signal_callback)
        
    def user1_waveform_changed_callback(self, pv_name, data):
        waveform = data[0]
        self.update_plot([waveform['t'],waveform['waveform']])

    def getRange(self):
        plt = self.plt
        if plt.xAxis is not None:
            x_range = [min(plt.xAxis), max(plt.xAxis)]
        else:
            x_range = [0, 10e-6]
        if plt.yData is not None:
            y_range = [min(plt.yData), max(plt.yData)]
        else:
            y_range = [-1,1]
        
        return [x_range, y_range]

    def widgetSetEnabled(self, state):
        self.widget.button_widget.setEnabled(state)
        
    def waveform_updated_signal_callback(self, waveform_data):
        data = waveform_data
        self.waveform_data = data
        waveform  = data['waveform']
 
        ch = data['ch']
        filtered = zero_phase_bandstop_filter(waveform, 100e6, 340e6, 5)
        
        self.update_plot(filtered)
  
        num_acq = data['num_acq']
        #self.widget.status_lbl.setText(str(num_acq))




    def update_plot(self, waveform):
        if waveform is not None:
            self.widget.plot(waveform)
            self.dataPlotUpdated.emit()


    def show_widget(self):
        self.widget.raise_widget()

