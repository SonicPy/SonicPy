
import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QThread, pyqtSignal
import time
from models.ScopeModel import Scope
from models.ArbModel import ArbModel
import json
from widgets.scope_widget import scopeWidget

from controllers.EditController import EditController
from models.ArbDefinitions import arb_waveforms


from widgets.panel import Panel
from functools import partial
from widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from controllers.pv_controller import pvController
from utilities.utilities import *


class ArbController(pvController):
    callbackSignal = pyqtSignal(dict)  
    stoppedSignal = pyqtSignal()
    dataUpdatedSignal = pyqtSignal(dict)
    dataBGUpdatedSignal = pyqtSignal(dict)
    runStateSignal = pyqtSignal(bool)

    def __init__(self, parent, isMain = False):
        model = ArbModel
        super().__init__(parent, model, isMain) 
        self.arb_edit_controller = EditController(self, title='Waveform control', definitions =arb_waveforms, default='g_wavelet')
        
        self.panel_items =[ 'waveform_type',
                            'edit_state']
        self.init_panel("USER1 waveform", self.panel_items)
        self.make_connections()
        
        if isMain:
            self.show_widget()
        
    def exit(self):
        self.model.exit()

    def make_connections(self):
        self.model.pvs['waveform_type'].value_changed_signal.connect(self.waveform_type_signal_callback)
        self.model.pvs['variable_parameter'].value_changed_signal.connect(self.variable_parameter_signal_callback)
        self.model.pvs['edit_state'].value_changed_signal.connect(self.edit_state_signal_callback)
    
    def show_widget(self):
        self.panel.raise_widget()

    def waveform_type_signal_callback(self, pv_name, data):
        data = data[0]
        

    def variable_parameter_signal_callback(self, pv_name, data):
        data = data[0]
        

    def edit_state_signal_callback(self, pv_name, data):
        data = data[0]
        
        if data:
            self.arb_edit_controller.show_widget()
        else: 
            self.arb_edit_controller.hide_widget()