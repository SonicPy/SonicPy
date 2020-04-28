
import os.path, sys
from PyQt5 import QtWidgets

import time
from datetime import datetime
import copy
from PyQt5.QtCore import pyqtSignal, QObject

from um.widgets.panel import Panel
from functools import partial
from um.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog

from um.widgets.pvWidgets import pvQWidgets



class pvController(QObject):
    
    def __init__(self, parent, model, isMain = False):
        
        super().__init__()  
        self.model = model
        self.isMain = isMain
        #self.create_public_methods()
        self.panel_items =[ ]

    def init_panel(self, title, panel_items):
        self.make_panel(title, panel_items, self.isMain)
        self.make_panel_connections()


    def make_panel(self, title, panel_items, isMain):
        pvs_forPanel = []
        pvs = list(self.model.pvs.keys())
        instr = self.model.instrument
        for tag in panel_items:
            if tag in pvs:
                pv = instr+':'+tag
                pvs_forPanel.append(pv)
        self.panel = Panel(title, pvs_forPanel, isMain)

    
    def make_panel_connections(self):
        self.panel.panelClosedSignal.connect(self.panel_closed_callback)
   

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
    
    def show_widget(self):
        self.panel.raise_widget()