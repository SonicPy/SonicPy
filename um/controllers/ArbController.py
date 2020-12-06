
import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QThread, pyqtSignal
import time
from um.models.ScopeModel import Scope
from um.models.ArbModel import ArbModel
import json


from um.controllers.EditController import EditController



from um.widgets.panel import Panel
from functools import partial
from um.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from um.controllers.pv_controller import pvController
from utilities.utilities import *

from um.models.ArbDefinitions import g_wavelet_controller, gx2_wavelet_controller, burst_fixed_time_controller
from um.models.pvServer import pvServer

class ArbController(pvController):
    callbackSignal = pyqtSignal(dict)  
    waveformComputedSignal = pyqtSignal(dict)

    def __init__(self, parent, isMain = False):
        
        model = ArbModel(parent)
        self.pv_server = pvServer()

        super().__init__(parent, model, isMain) 

        self.arb1 = g_wavelet_controller(self)
        self.arb3 = burst_fixed_time_controller(self)
        self.scan_pv = self.arb3.scan_pv

        w_types = [self.arb1.model.param['name'],  self.arb3.model.param['name']]

        
        waveforms_task = {  'selected_item': 
                                {'desc': 'Waveform type', 'val':w_types[1], 'list':w_types, 
                                'param':{'type':'l'}}
                                }

        self.model.create_pvs(waveforms_task)

        
        self.panel_items =[ 'selected_item',
                            'edit_state']
        self.init_panel("USER1 waveform", self.panel_items)

        
        self.arb_edit_controller = EditController(self, title='Waveform control', selector_pv = 'ArbModel:selected_item')
        self.arb_edit_controller.add_controller(self.arb1.model.param['name'], self.arb1)
        self.arb_edit_controller.add_controller(self.arb3.model.param['name'], self.arb3)
        self.arb_edit_controller.select_controller(self.arb3.model.param['name'])

        output_pv = 'ArbModel:arb_waveform'
        self.arb1.model.pvs['output_channel'].set(output_pv)
        self.arb3.model.pvs['output_channel'].set(output_pv)
        self.arb1.model.pvs['auto_process'].set(True)
        self.arb3.model.pvs['auto_process'].set(True)


        self.make_connections()


        #self.model.pvs['selected_item'].set(self.arb3.model.param['name'])

        if isMain:
            self.show_widget()
        
    

    def make_connections(self):
        self.model.pvs['selected_item'].value_changed_signal.connect(self.waveform_type_signal_callback)
        
        self.model.pvs['edit_state'].value_changed_signal.connect(self.edit_state_signal_callback)
        self.model.pvs['arb_waveform'].value_changed_signal.connect(self.arb_waveform_signal_callback)
        #self.arb_edit_controller.applyClickedSignal.connect(self.arb_edited_apply_clicked_signal_callback)

        #self.arb_edit_controller.widget.controller_selection_edited_signal.connect(self.controller_selection_edited_signal_callback)

 
    def show_widget(self):
        self.panel.raise_widget()


    def controller_selection_edited_signal_callback(self, key):
        self.arb_edit_controller.select_controller(key)

    def arb_edited_apply_clicked_signal_callback(self, selected):
        print(selected)

    def waveform_type_signal_callback(self, pv_name, data):
        data = data[0]
        #print('waveform_type_signal_callback. pv: '+ str(pv_name))
        #self.arb_edit_controller.widget.set_selected_choice(data)

    def arb_waveform_signal_callback(self, pv_name, data):
        data = data[0]
        
        
        #self.arb_edit_controller.update_plot(data)


    def edit_state_signal_callback(self, pv_name, data):
        data = data[0]
        
        if data:
            self.arb_edit_controller.show_widget()
        else: 
            self.arb_edit_controller.hide_widget()