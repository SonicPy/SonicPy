
import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QThread, pyqtSignal
import time
from models.ScopeModel import Scope
from models.DPO5104 import Scope_DPO5104
import json
from widgets.scope_widget import scopeWidget

from widgets.panel import Panel
from functools import partial
from widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from controllers.pv_controller import pvController
from utilities.utilities import *


class ScopeController(pvController):
    callbackSignal = pyqtSignal(dict)  
    stoppedSignal = pyqtSignal()
    dataUpdatedSignal = pyqtSignal(dict)
    dataBGUpdatedSignal = pyqtSignal(dict)
    runStateSignal = pyqtSignal(bool)

    def __init__(self, parent, isMain = False):
        model = Scope_DPO5104
        super().__init__(parent, model, isMain) 
        
        self.panel_items =[ 'instrument',
                            'channel',
                            'vertical_scale',
                            'acquisition_type',
                            'num_av',
                            'run_state']
        self.init_panel("Scope", self.panel_items)
        self.make_connections()
        self.waveform_data = None
        self.waveform_bg_data = None
        if isMain:
            self.show_widget()
        
    def channel_changed_callback(self, channel):
        panel_items =['channel_state',
                        'vertical_scale']
        for item in panel_items:
            self.model.pvs[item].get()
        
    def exit(self):
        self.model.exit()

    def make_connections(self):
        self.model.pvs['waveform'].value_changed_signal.connect(self.waveform_updated_signal_callback)
        self.model.pvs['bg_waveform'].value_changed_signal.connect(self.bg_waveform_updated_signal_callback)
        self.model.pvs['channel'].value_changed_signal.connect(self.channel_changed_callback)
        self.model.pvs['run_state'].value_changed_signal.connect(self.run_state_callback)
        
    def run_state_callback(self, tag, data):
        state = data[0]
        self.runStateSignal.emit(state)

    def bg_waveform_updated_signal_callback(self, pv_name, data):
        data = data[0]
        self.waveform_bg_data = data
        self.dataBGUpdatedSignal.emit(data)

    def waveform_updated_signal_callback(self, pv_name, data):
        data = data[0]
        self.waveform_data = data
        self.dataUpdatedSignal.emit(data)
    
    def show_widget(self):
        self.panel.raise_widget()