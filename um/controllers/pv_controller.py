
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
import json

from um import autosave_settings_path
from um import autosave_data_path


class pvController(QObject):
    
    def __init__(self, parent, model, isMain = False):
        
        super().__init__()  
        self.model = model
        self.isMain = isMain
        #self.create_public_methods()
        self.panel_items =[ ]


        # this is where we load saved values from autosave.json
        self.tag = self.model.instrument
        self.autosave_settings = self.load_autosave(autosave_settings_path, self.tag)
        self.autosave_data_path = os.path.join(autosave_data_path, self.tag)
        
        if self.autosave_settings is not None:
            pass

            '''print(self.tag)
            print(self.autosave_settings)'''

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
            else:
                if tag == '_divider':
                    pvs_forPanel.append(tag)
        self.panel = Panel(title, pvs_forPanel, isMain)

    
    def make_panel_connections(self):
        self.panel.panelClosedSignal.connect(self.panel_closed_callback)


    def exit(self):
        
        self.model.exit()
        tag = self.tag
        if self.autosave_settings is not None:
            self.save_pvs(self.autosave_settings,self.tag)

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


    def load_autosave(self, filename, tag):

        try:
            with open(filename) as f:
                openned_file = json.load(f)

                
                if tag in openned_file:
                    settings = openned_file[tag]
                    return settings
        except:
            pass
        return None

    def save_pvs(self, autosave_settings, tag):


        data_out = self.model.get_settings(autosave_settings)
        # print (data_out)

        '''
        try:
            with open(filename, 'w') as outfile:
                json.dump(data_out, outfile, sort_keys=True, indent=4)
                outfile.close()
                #print(data_out)
        except:
            pass
        '''
