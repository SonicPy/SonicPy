
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
from um.models.SaveDataModel import SaveDataModel
from um.models.pvServer import pvServer

class SaveDataController(pvController):
    callbackSignal = pyqtSignal(dict)  

    def __init__(self, parent, isMain = False, offline = False):
        
        model = SaveDataModel(parent, offline)
        super().__init__(parent, model, isMain) 
        self.pv_server = pvServer()
        self.panel_items =['file_system_path',
                            'subdirectory',
                            'base_name',
                            'format',
                            'file_extension',
                            'path',
                            'name',
                            'next_file_number',
                            'latest_event',
                            'save'
                        ]

        self.init_panel("Save data", self.panel_items)
        self.make_connections()

        
        
        if isMain:
            self.show_widget()


    def save_data_callback(self, *args, **kwargs):
        
        waveform_data = self.pv_server.get_pv('DPO5104:waveform')._val
        
        if waveform_data is not None:
            if 'folder' in kwargs:
                folder = kwargs['folder']
            else:
                folder = None
            if not 'filename' in kwargs:
                filename = save_file_dialog(
                                self.panel, "Save waveform",directory=folder,
                                filter=self.model.pvs['file_filter']._val)
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

    def make_connections(self):
        pass


    def show_widget(self):
        self.panel.raise_widget()