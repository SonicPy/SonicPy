
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
    def __init__(self, parent, isMain = False):
        model = Scope_DPO5104
        super().__init__(parent, model, isMain) 
        
        self.widget = scopeWidget()
        self.panel_items =[ 'instrument',
                            'channel',
                            'vertical_scale',
                            'acquisition_type',
                            'num_av']
        self.init_panel("Scope", self.panel_items)
        self.make_connections()
        self.waveform_data = None
        self.waveform_bg_data = None
        if isMain:
            self.show_widget()

    def close_background_callback(self):
        self.update_bg_plot([[],[]])


    def load_background_callback(self, *args, **kwargs):

        if 'folder' in kwargs:
            folder = kwargs['folder']
        else:
            folder = None

        if not 'filename' in kwargs:
            filename = open_file_dialog(
                            self.widget, "Open waveform",directory=folder,
                            filter=self.model.file_filter)
        else:
            filename = kwargs['filename']
        if filename is not '':
            self.model.read_file(filename)

            folder = os.path.dirname(str(filename)) 
            
        return folder
        

    def save_data_callback(self, *args, **kwargs):
        filename = ''
        if self.waveform_data is not None:
            if 'folder' in kwargs:
                folder = kwargs['folder']
            else:
                folder = None
            if not 'filename' in kwargs:
                filename = save_file_dialog(
                                self.widget, "Save waveform",directory=folder,
                                filter=self.model.file_filter)
            else:
                filename = kwargs['filename']
            if filename is not '':
                if 'params' in kwargs:
                    params = kwargs['params']
                    self.model.pvs['params'].set(params)
                else:
                    self.model.pvs['params'].set({})
                self.model.pvs['filename'].set(filename)
                self.model.pvs['save'].set(True)
                
        return filename
        
    def channel_changed_callback(self, channel):
        panel_items =['channel_state',
                        'vertical_scale']
        tasks_all = self.model.tasks
        tasks = {}
        for item in panel_items:
            self.model.pvs[item].get()
        
    def exit(self):
        self.model.exit()
        self.widget.close()

    def make_connections(self):
        self.widget.start_stop_btn.clicked.connect(lambda:self.start_stop_btn_callback(self.widget.start_stop_btn.isChecked()))
        self.model.pvs['waveform'].value_changed_signal.connect(self.waveform_updated_signal_callback)
        self.model.pvs['bg_waveform'].value_changed_signal.connect(self.bg_waveform_updated_signal_callback)
        self.widget.erase_btn.clicked.connect(self.erase_btn_callback)
        self.widget.save_btn.clicked.connect(self.save_data_callback)
        self.model.pvs['channel'].value_changed_signal.connect(self.channel_changed_callback)
        self.model.pvs['run_state'].value_changed_signal.connect(self.run_state_callback)
        


    def run_state_callback(self, tag, data):
        state = data[0]
        if state:
            self.widget.start_stop_btn.setChecked(True)
            channel_state = self.model.pvs['channel_state']._val
            if not channel_state:
                self.model.pvs['channel_state'].set(True)
            self.get_waveform()
        else:
            self.widget.start_stop_btn.setChecked(False)
            self.stoppedSignal.emit()

    def start_stop_btn_callback(self, state):
        if state:
            self.model.pvs['run_state'].set(True)
        else:
            self.model.pvs['run_state'].set(False)

    

    def erase_btn_callback(self):
        self.model.pvs['erase'].set(True)
        #self.widget.clear_plot()
        #self.widget.save_btn.setDisabled(True)

    

    def bg_waveform_updated_signal_callback(self, pv_name, data):
        data = data[0]
        self.waveform_bg_data = data
        waveform  = data['waveform']
        
        
        
        
        start = time.time()
        filtered = zero_phase_bandstop_filter(waveform, 120000000, 300000000, 5)
        end = time.time()
        elapsed = end - start
        #print(str(elapsed))
        self.update_bg_plot(filtered)
        #self.update_filtered_plot(filtered)

    def waveform_updated_signal_callback(self, pv_name, data):
        data = data[0]
        self.waveform_data = data
        waveform  = data['waveform']
        '''
        if len(waveform):
            self.widget.save_btn.setDisabled(False)
        '''
        ch = data['ch']
        self.update_plot(waveform)
        elapsed = data['transfer_time']
        num_acq = data['num_acq']
        self.widget.status_lbl.setText(str(num_acq))
        #dt = data['time']
        #status = 'Date/Time: ' + dt + '; Transfer time: ' + str(round(elapsed,3))
        #self.widget.status_lbl.setText(status)
        if self.widget.start_stop_btn.isChecked():
            self.get_waveform()
            
    def update_plot(self, waveform):
        if waveform is not None:
            self.widget.plot(waveform)

    def update_bg_plot(self, waveform):
        if waveform is not None:
            self.widget.plot_bg(waveform)

    def update_filtered_plot(self, waveform):
        if waveform is not None:
            self.widget.plot_filtered(waveform)

    
 
    ###########################################################
    ## Public methods
    ###########################################################

    def get_waveform(self):
        if self.model.connected:
            self.model.pvs['waveform'].get()
        
    def widgetSetEnabled(self, state):
        self.widget.button_widget.setEnabled(state)
    
    def show_widget(self):
        self.widget.raise_widget()
        self.panel.raise_widget()