
import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QThread, pyqtSignal
import time
from um.models.ScopeModel import Scope
from um.models.DPO5104 import Scope_DPO5104
import json
from um.widgets.scope_widget import scopeWidget

from um.widgets.panel import Panel
from functools import partial
from um.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from um.controllers.pv_controller import pvController
from utilities.utilities import *
from um.models.SaveDataModel import SaveDataModel


class SaveDataController(pvController):
    callbackSignal = pyqtSignal(dict)  

    def __init__(self, parent, isMain = False, offline = False):
        
        model = SaveDataModel(parent, offline)
        super().__init__(parent, model, isMain) 
        
        self.panel_items =[ ]

        self.init_panel("Save data", self.panel_items)
        self.make_connections()
        
        if isMain:
            self.show_widget()


    def save_data_callback(self, *args, **kwargs):
        filename = ''
        if self.scope_controller.waveform_data is not None:
            if 'folder' in kwargs:
                folder = kwargs['folder']
            else:
                folder = None
            if not 'filename' in kwargs:
                filename = save_file_dialog(
                                self.widget, "Save waveform",directory=folder,
                                filter=self.scope_controller.model.file_filter)
            else:
                filename = kwargs['filename']
            if filename is not '':
                if 'params' in kwargs:
                    params = kwargs['params']
                    self.scope_controller.model.pvs['params'].set(params)
                else:
                    self.scope_controller.model.pvs['params'].set({})
                self.scope_controller.model.pvs['filename'].set(filename)
                self.scope_controller.model.pvs['save'].set(True)

    def make_connections(self):
        pass


    def exit(self):
        self.model.exit()


    def show_widget(self):
        self.panel.raise_widget()