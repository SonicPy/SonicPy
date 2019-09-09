
import os.path, sys
from PyQt5 import QtWidgets

import time
from datetime import datetime
import copy
from PyQt5.QtCore import pyqtSignal, QObject

from widgets.panel import Panel
from functools import partial
from widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog


class pvController(QObject):
    
    def __init__(self, parent, model, isMain = False):
        
        super().__init__()  
        self.model = model(parent)
        self.isMain = isMain
        #self.create_public_methods()
        self.panel_items =[ ]

    def init_panel(self, title, panel_items):
        self.make_panel(title, panel_items, self.isMain)
        self.make_panel_connections()

    def make_panel(self, title, panel_items, isMain):
        pvs_forPanel = []
        pvs = self.model.pvs
        for tag in panel_items:
            if tag in pvs:
                pv = pvs[tag]
                pvs_forPanel.append(pv)
        self.panel = Panel(title, pvs_forPanel, isMain)

    def save(self, *args, **kwargs):
        if not 'filename' in kwargs:
            filename = save_file_dialog(
                self.panel, "Save " + self.model.settings_file_tag+ " settings",
                filter='Instrument settings (*.json)')
        else:
            filename = kwargs['filename']
        if filename is not '':
            if filename.endswith('.json'):
                self.model.save_settings(self.panel_items, filename)

    def load(self, *args, **kwargs):
        if not 'filename' in kwargs:
            filename = open_file_dialog(
                self.panel, "Load settings")
        else:
            filename = kwargs['filename']
        if filename is not '':
            if filename.endswith('.json'):
                self.model.load_settings(filename)

  
    
    def make_panel_connections(self):
        self.panel.panelClosedSignal.connect(self.panel_closed_callback)
        self.panel.save_btn.clicked.connect(self.save)
        self.panel.load_btn.clicked.connect(self.load)

    def exit(self):
        self.model.exit()

    def panel_closed_callback(self):
        self.exit()


    ###########################################################
    ## Public methods
    ###########################################################


    def get_panel(self):
        return self.panel

    def panelSetEnabled(self, state):
        self.panel.setEnabled(state)

    '''

    def create_public_methods(self):
        tasks = self.model.tasks
        for key in tasks:
            task = tasks[key]
            if 'methods' in task:
                for method in task['methods']:
                    if task['methods'][method]:
                        attr = method+'_'+ key
                        if hasattr(self.model, attr):
                            func = self.model.__getattribute__(attr)
                            setattr(self, attr, func)
    '''
    
    def show_widget(self):
        self.panel.raise_widget()