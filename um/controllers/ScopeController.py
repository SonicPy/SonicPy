
import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QThread, pyqtSignal
import time
from um.models.ScopeModel import Scope
from um.models.DPO5104 import Scope_DPO5104
import json


from um.widgets.panel import Panel
from functools import partial
from um.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from um.controllers.pv_controller import pvController
from utilities.utilities import *
from um.controllers.envController import envController

class ScopeController(pvController):
    callbackSignal = pyqtSignal(dict)  
    #stoppedSignal = pyqtSignal()
    dataUpdatedSignal = pyqtSignal(dict)
    #dataBGUpdatedSignal = pyqtSignal(dict)
    #runStateSignal = pyqtSignal(bool)

    def __init__(self, parent, isMain = False, offline = False):
        visa_hostname = '143'
        model = Scope_DPO5104(parent, visa_hostname=visa_hostname, offline = offline)
        super().__init__(parent, model, isMain) 
        
        self.panel_items =[ 'instrument',
                            'channel',
                            'vertical_scale',
                            'acquisition_type',
                            'num_av',
                            'num_acq',
                            'run_state',
                            'stop_after_num_av_preset',
                            '_divider',
                            'autoscale_t_min',
                            'autoscale_t_max',
                            'autoscale_margin',
                            'do_autoscale',
                            'auto_autoscale']
        self.init_panel("Scope", self.panel_items)
        self.make_connections()

        #self.env_controller = envController(offline = offline)
        
        if isMain:
            self.show_widget()
        
    def channel_changed_callback(self, channel):
        panel_items =['channel_state',
                        'vertical_scale']
        for item in panel_items:
            self.model.pvs[item].get()
        
    

    def make_connections(self):
        self.model.pvs['waveform'].value_changed_signal.connect(self.waveform_updated_signal_callback)
      
        self.model.pvs['channel'].value_changed_signal.connect(self.channel_changed_callback)
        self.model.pvs['run_state'].value_changed_signal.connect(self.run_state_callback)
        
    def run_state_callback(self, tag, data):
        state = data[0]

        if state:
            self.get_waveform()

    def waveform_updated_signal_callback(self, pv_name, data):
        self.dataUpdatedSignal.emit(data[0])
        time.sleep(0.03)
        if self.model.pvs['run_state']._val:
            self.get_waveform()         

    def get_waveform(self):
        #self.model._get_waveform()
        self.model.pvs['waveform'].get()

    def show_widget(self):
        self.panel.raise_widget()
