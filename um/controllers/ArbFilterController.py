
import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QThread, pyqtSignal
import time
from um.models.ScopeModel import Scope
from um.models.ArbFilterModel import ArbFilterModel
import json
from um.widgets.scope_widget import scopeWidget

from um.controllers.EditController import EditController
#from um.models.FilterDefinitions import filters

from um.widgets.panel import Panel
from functools import partial
from um.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from um.controllers.pv_controller import pvController
from utilities.utilities import *
from um.models.FilterDefinitions import no_filter_controller

class ArbFilterController(pvController):
    callbackSignal = pyqtSignal(dict)  
    #stoppedSignal = pyqtSignal()
    #dataUpdatedSignal = pyqtSignal(dict)
    #dataBGUpdatedSignal = pyqtSignal(dict)
    #runStateSignal = pyqtSignal(bool)

    def __init__(self, parent, isMain = False):
        #definitions = filters
        model = ArbFilterModel(parent)
        super().__init__(parent, model, isMain) 
        self.arb_filter_edit_controller = EditController(self, title='Filter control')

        self.arb_filter_1 = no_filter_controller(self)
        #self.arb_filter_2 = burst_fixed_time_controller(self)

        self.arb_filter_edit_controller.add_controller(self.arb_filter_1.model.instrument, self.arb_filter_1)
        #self.arb_filter_edit_controller.add_controller(self.arb3.model.instrument, self.arb3)

        self.arb_filter_edit_controller.select_controller(self.arb_filter_1.model.instrument)


        f_types = [self.arb_filter_1.model.instrument]



        filters_task = {  'filter_type': 
                                {'desc': 'Wave type', 'val':f_types[0], 'list':f_types, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'waveform_type','type':'l'}}}
        self.model.create_pvs(filters_task)



        self.panel_items =[ 'filter_type',
                            'edit_state']
        self.init_panel("Waveform filter", self.panel_items)
        self.make_connections()
        
        if isMain:
            self.show_widget()
        
    def exit(self):
        self.model.exit()

    def make_connections(self):
        self.model.pvs['filter_type'].value_changed_signal.connect(self.filter_type_signal_callback)
        #self.model.pvs['variable_parameter'].value_changed_signal.connect(self.variable_parameter_signal_callback)
        self.model.pvs['edit_state'].value_changed_signal.connect(self.edit_state_signal_callback)
        self.arb_filter_edit_controller.applyClickedSignal.connect(self.arb_filter_edited_apply_clicked_signal_callback)
    
    def show_widget(self):
        self.panel.raise_widget()

    def filter_type_signal_callback(self, pv_name, data):
        data = data[0]
        
        self.arb_filter_edit_controller.widget.set_selected_choice(data)

    def arb_filter_edited_apply_clicked_signal_callback(self, selected):
        print(selected)

    '''
    def variable_parameter_signal_callback(self, pv_name, data):
        data = data[0]
    '''    

    def edit_state_signal_callback(self, pv_name, data):
        data = data[0]
        
        if data:
            self.arb_filter_edit_controller.show_widget()
        else: 
            self.arb_filter_edit_controller.hide_widget()