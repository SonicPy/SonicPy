
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



from widgets.panel import Panel
from functools import partial
from widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from controllers.pv_controller import pvController
from utilities.utilities import *

from models.ArbDefinitions import g_wavelet_controller, gx2_wavelet_controller, burst_fixed_time_controller


class ArbController(pvController):
    callbackSignal = pyqtSignal(dict)  
    stoppedSignal = pyqtSignal()
    dataUpdatedSignal = pyqtSignal(dict)
    dataBGUpdatedSignal = pyqtSignal(dict)
    runStateSignal = pyqtSignal(bool)

    def __init__(self, parent, isMain = False):
        
        model = ArbModel(parent, ['g_wavelet', 'gx2_wavelet', 'burst_fixed_time'])

        super().__init__(parent, model, isMain) 

        arb1 = g_wavelet_controller(self)
        arb2 = gx2_wavelet_controller(self)
        arb3 = burst_fixed_time_controller(self)


        self.arb_edit_controller = EditController(self, title='Waveform control')
        self.arb_edit_controller.add_controller(arb1.model.instrument, arb1)
        self.arb_edit_controller.add_controller(arb2.model.instrument, arb2)
        self.arb_edit_controller.add_controller(arb3.model.instrument, arb3)

        self.arb_edit_controller.select_controller(arb1.model.instrument)
        
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
        #self.model.pvs['variable_parameter'].value_changed_signal.connect(self.variable_parameter_signal_callback)
        self.model.pvs['edit_state'].value_changed_signal.connect(self.edit_state_signal_callback)
        self.model.pvs['arb_waveform'].value_changed_signal.connect(self.arb_waveform_signal_callback)
        self.arb_edit_controller.applyClickedSignal.connect(self.arb_edited_apply_clicked_signal_callback)

        self.arb_edit_controller.widget.controller_selection_edited_signal.connect(self.controller_selection_edited_signal_callback)
    
    def show_widget(self):
        self.panel.raise_widget()

    def controller_selection_edited_signal_callback(self, key):
        self.arb_edit_controller.select_controller(key)

    def arb_edited_apply_clicked_signal_callback(self, selected):
        print(selected)

    def waveform_type_signal_callback(self, pv_name, data):
        data = data[0]
        self.arb_edit_controller.widget.set_selected_choice(data)

    def arb_waveform_signal_callback(self, pv_name, data):
        data = data[0]['plot']
        self.arb_edit_controller.update_plot(data)

    '''
    def variable_parameter_signal_callback(self, pv_name, data):
        data = data[0]
    '''    

    def edit_state_signal_callback(self, pv_name, data):
        data = data[0]
        
        if data:
            self.arb_edit_controller.show_widget()
        else: 
            self.arb_edit_controller.hide_widget()