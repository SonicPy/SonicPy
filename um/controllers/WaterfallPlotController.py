

import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import time

import json


from um.widgets.panel import Panel
from functools import partial
from um.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from um.controllers.pv_controller import pvController
from um.widgets.pvWidgets import pvQWidgets

from utilities.utilities import *
from um.models.pvServer import pvServer


class WaterfallPlotController(QObject):
    callbackSignal = pyqtSignal(dict)  
   
    fastCursorMovedSignal = pyqtSignal(str)  
    staticCursorMovedSignal = pyqtSignal(str) 
    dataPlotUpdated = pyqtSignal()

    def __init__(self, waterfall_controller, waterfall_widget,  isMain = False):
        super().__init__()
        self.pv_server = pvServer()
        self.pv_widgets = pvQWidgets()
        self.widget = waterfall_widget
        self.waterfall_controller = waterfall_controller
        #self.waveform = self.pv_server.get_pv('Waterfall:waterfall_out')

        self.pg = self.widget.plot_widget.fig.win
        if isMain:
            self.show_widget()

        
        self.plt = self.widget.plot_widget.fig.win

        
        btn_erase, _ = self.pv_widgets.pvWidget('Waterfall:clear')
        ctrl_scale, _ = self.pv_widgets.pvWidget('Waterfall:scale')
        
        btn_clip, _ = self.pv_widgets.pvWidget('Waterfall:clip')

        waterfall_widget_controls = [btn_erase, 'spacer', QtWidgets.QLabel('Scale'), ctrl_scale, btn_clip ]
        self.widget.add_buttons(waterfall_widget_controls)

        self.make_connections()

    def make_connections(self):
        
        self.waterfall_controller.model.pvs['waterfall_out'].value_changed_signal.connect(self.waterfall_out_changed_callback)
        
        
    def waterfall_out_changed_callback(self, pv_name, data):
        waveforms = data[0]
        keys = list( waveforms.keys())
        if len(keys):
            key = keys[0]
            waveform = waveforms[key]
            
            self.update_plot([waveform[0],waveform[1]])
        else:
            self.widget.clear_plot()



    def widgetSetEnabled(self, state):
        self.widget.button_widget.setEnabled(state)
 

    def update_plot(self, waveform):
        if waveform is not None:
            self.widget.plot(waveform[0],waveform[1])
            self.dataPlotUpdated.emit()


    def show_widget(self):
        self.widget.raise_widget()

