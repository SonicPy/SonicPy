
import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QThread, pyqtSignal
import time
from um.models.ScopeModel import Scope
from um.models.ArbModel import ArbModel
import json
from um.widgets.scope_widget import scopeWidget

from um.controllers.EditController import EditController



from um.widgets.panel import Panel
from functools import partial
from um.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from um.controllers.pv_controller import pvController
from utilities.utilities import *

from um.models.ArbDefinitions import g_wavelet_controller, gx2_wavelet_controller, burst_fixed_time_controller


class ArbController(pvController):
    callbackSignal = pyqtSignal(dict)  
    waveformComputedSignal = pyqtSignal(dict)

    def __init__(self, parent, isMain = False):
        
        model = ArbModel(parent)

        super().__init__(parent, model, isMain) 

        self.arb1 = g_wavelet_controller(self)
        
        
        self.arb3 = burst_fixed_time_controller(self)


        self.arb_edit_controller = EditController(self, title='Waveform control')
        self.arb_edit_controller.add_controller(self.arb1.model.instrument, self.arb1)
        self.arb_edit_controller.add_controller(self.arb3.model.instrument, self.arb3)
        self.arb_edit_controller.select_controller(self.arb1.model.instrument)

        w_types = [self.arb1.model.instrument,  self.arb3.model.instrument]

        waveforms_task = {  'waveform_type': 
                                {'desc': 'Wave type', 'val':w_types[0], 'list':w_types, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'waveform_type','type':'l'}}}
        self.model.create_pvs(waveforms_task)

        
        
        self.panel_items =[ 'waveform_type',
                            'edit_state']
        self.init_panel("USER1 waveform", self.panel_items)

        self.make_connections()

        self.arb1.model.pvs['output_channel']._val = self.model.pvs['arb_waveform']
        self.arb3.model.pvs['output_channel']._val = self.model.pvs['arb_waveform']

        
        if isMain:
            self.show_widget()
        
    def exit(self):
        self.model.exit()

    def make_connections(self):
        self.model.pvs['waveform_type'].value_changed_signal.connect(self.waveform_type_signal_callback)
        
        self.model.pvs['edit_state'].value_changed_signal.connect(self.edit_state_signal_callback)
        self.model.pvs['arb_waveform'].value_changed_signal.connect(self.arb_waveform_signal_callback)
        self.arb_edit_controller.applyClickedSignal.connect(self.arb_edited_apply_clicked_signal_callback)

        self.arb_edit_controller.widget.controller_selection_edited_signal.connect(self.controller_selection_edited_signal_callback)

        
        
    
    def show_widget(self):
        self.panel.raise_widget()

    def waveform_changed_signal_callback(self, pv_name, data):
        data = data[0]
        print('waveform_changed_signal_callback. pv: '+ str(pv_name))
        #self.waveformComputedSignal.emit(data)
        '''if len(data):
            t = data['t']
            waveform = data['waveform']
            self.arb_edit_controller.widget.update_plot([t,waveform])'''

    def controller_selection_edited_signal_callback(self, key):
        self.arb_edit_controller.select_controller(key)

    def arb_edited_apply_clicked_signal_callback(self, selected):
        print(selected)

    def waveform_type_signal_callback(self, pv_name, data):
        data = data[0]
        print('waveform_type_signal_callback. pv: '+ str(pv_name))
        #self.arb_edit_controller.widget.set_selected_choice(data)

    def arb_waveform_signal_callback(self, pv_name, data):
        data = data[0]
        self.waveformComputedSignal.emit(data)
        #self.arb_edit_controller.update_plot(data)

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