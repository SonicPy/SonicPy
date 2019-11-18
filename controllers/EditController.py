
import os.path, sys
from PyQt5 import QtWidgets
import copy
from PyQt5.QtCore import QObject, pyqtSignal
import time
from models.ScopeModel import Scope
from models.ArbModel import ArbModel
import json
from widgets.PopUpWidget import EditWidget

from widgets.panel import Panel
from functools import partial
from widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from controllers.pv_controller import pvController
from utilities.utilities import *


class EditController(QObject):
    callbackSignal = pyqtSignal(dict)  
    applyClickedSignal = pyqtSignal(str)
        
    def __init__(self, arb_controller, title, definitions, default,  isMain = False):
        super().__init__()
        self.widget = EditWidget(title, definitions, default)
        self.definitions = definitions
        #self.pg = self.widget.plot_widget.fig.win
        
        self.arb_controller = arb_controller
        self.widget_shown = False
        self.widget.widget_closed.connect(self.widget_closed_callback)

        if isMain:
            self.show_widget()

        self.make_connections()

    

    
    
    def update_plot(self, data):
        self.widget.update_plot(data)
        
    def exit(self):
        self.model.exit()

    def make_connections(self):
        self.widget.get_apply_btn().clicked.connect(self.edit_widget_apply_clicked_signal_callback)

    def edit_widget_apply_clicked_signal_callback(self):
        selected = self.widget.get_selected_choice()
        self.applyClickedSignal.emit(selected)
        
    
    def show_widget(self):
        self.widget.raise_widget()
        self.widget_shown = True

    def hide_widget(self):
        self.widget.hide()
        self.widget_shown = False

    def widget_closed_callback(self):
        self.arb_controller.model.pvs['edit_state'].set(False)

    