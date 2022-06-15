
import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QThread, pyqtSignal
import time
from um.models.ScopeModel import Scope
from um.models.ArbFilterModel import ArbFilterModel
import json


from um.controllers.EditController import EditController
#from um.models.FilterDefinitions import filters

from um.widgets.panel import Panel
from functools import partial
from um.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from um.controllers.pv_controller import pvController
from utilities.utilities import *
from um.models.FilterDefinitions import no_filter_controller, tukey_filter_controller

from um.models.pvServer import pvServer

class ArbFilterController(pvController):
    callbackSignal = pyqtSignal(dict)  
    waveformFilteredcallbackSignal = pyqtSignal(dict)

    def __init__(self, parent, isMain = False):
        #definitions = filters
        model = ArbFilterModel(parent)
        super().__init__(parent, model, isMain) 
        self.pv_server = pvServer()

        self.arb_filter_1 = no_filter_controller(self)
        self.arb_filter_2 = tukey_filter_controller(self)

        self.f_types = [self.arb_filter_1.model.param['name'], self.arb_filter_2.model.param['name']]

        

        filters_task = {  'selected_item': 
                                {'desc': 'Window type', 'val':self.f_types[1], 'list':self.f_types, 
                                'param':{'type':'l'}},

                        'user1_channel': 
                                {'desc': 'user1 channel', 'val':'AFG3251:user1_waveform',  
                                'param':{'type':'s'}},

                        'waveform_in_channel': 
                                {'desc': 'user1 channel', 'val':'ArbModel:arb_waveform',  
                                'param':{'type':'s'}}
                                }
        self.model.create_pvs(filters_task)

        self.panel_items =[ 'selected_item',
                            'edit_state']
        self.init_panel("Waveform filter", self.panel_items)
        
        
        self.arb_filter_edit_controller = EditController(self, title='Filter control', selector_pv='ArbFilter:selected_item')

        self.arb_filter_edit_controller.add_controller(self.arb_filter_1.model.param['name'], self.arb_filter_1)
        self.arb_filter_edit_controller.add_controller(self.arb_filter_2.model.param['name'], self.arb_filter_2)

        self.arb_filter_edit_controller.select_controller(self.arb_filter_2.model.param['name'])

        output_pv = 'ArbFilter:waveform_out'

        self.arb_filter_1.model.pvs['output_channel'].set(output_pv)
        self.arb_filter_2.model.pvs['output_channel'].set(output_pv)

        self.make_connections()

        #self.model.pvs['selected_item'].set(self.arb_filter_2.model.param['name'])
        
        if isMain:
            self.show_widget()
        
    


    def make_connections(self):

        waveform_in = self.pv_server.get_pv(self.model.pvs['waveform_in_channel']._val)
        waveform_in.value_changed_signal.connect(self.waveform_in_updated)


        self.model.pvs['selected_item'].value_changed_signal.connect(self.filter_type_signal_callback)
        #self.model.pvs['variable_parameter'].value_changed_signal.connect(self.variable_parameter_signal_callback)
        self.model.pvs['edit_state'].value_changed_signal.connect(self.edit_state_signal_callback)
        #self.arb_filter_edit_controller.applyClickedSignal.connect(self.arb_filter_edited_apply_clicked_signal_callback)
        #self.arb_filter_edit_controller.widget.controller_selection_edited_signal.connect(self.controller_selection_edited_signal_callback)
        self.model.pvs['waveform_in'].value_changed_signal.connect(self.waveform_in_signal_callback)

        self.model.pvs['waveform_out'].value_changed_signal.connect(self.waveform_changed_signal_callback)

    def waveform_in_updated(self, pv_name, data):
        data = data[0]
        if len(data):
            self.model.pvs['waveform_in'].set(data)
        
    def show_widget(self):
        self.panel.raise_widget()

    def filter_type_signal_callback(self, pv_name, data):
        data = data[0]
        
        self.arb_filter_edit_controller.widget.set_selected_choice(data)

    

    def waveform_in_signal_callback(self, pv_name, data):
        data = data[0]
        #print (pv_name)
        filter_type = self.model.pvs['selected_item']._val
        index = self.f_types.index(filter_type)
        filter_controller = self.arb_filter_edit_controller.controllers[index]
        filter_controller.model.pvs['waveform_in'].set(data)
        filter_controller.model.pvs['apply'].set(True)
    

    def waveform_changed_signal_callback(self, pv_name, data):
        data = data[0]
        
        if len(data):
            print('waveform_changed_signal_callback. pv: '+ str(pv_name))
            pv = self.pv_server.get_pv(self.model.pvs['user1_channel']._val)
            pv.set(data)
    

    def controller_selection_edited_signal_callback(self, key):
        self.arb_filter_edit_controller.select_controller(key)

    def arb_filter_edited_apply_clicked_signal_callback(self, selected):
        pass
        
        

    def edit_state_signal_callback(self, pv_name, data):
        data = data[0]
        
        if data:
            self.arb_filter_edit_controller.show_widget()
        else: 
            self.arb_filter_edit_controller.hide_widget()


