#!/usr/bin/env python



import os.path, sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
from functools import partial
import json
import copy
from pathlib import Path
from numpy import arange
from utilities.utilities import *
from um.widgets.UltrasoundWidget import UltrasoundWidget
from um.controllers.SweepController import SweepController
from um.controllers.AFGController import AFGController
from um.controllers.AFGPlotController import AFGPlotController
from um.controllers.ScopeController import ScopeController
from um.controllers.ScopePlotController import ScopePlotController
from um.controllers.ArbController import ArbController
from um.controllers.ArbFilterController import ArbFilterController
from um.controllers.SaveDataController import SaveDataController
from um.controllers.WaterfallController import WaterfallController
from um.controllers.WaterfallPlotController import WaterfallPlotController

from um.controllers.OverlayController import OverlayController


import math

from um.controllers.PhaseController import PhaseController

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra

from .. import style_path

from um.models.pvServer import pvServer
from um.widgets.panel import Panel

############################################################

class UltrasoundController(QObject):
    def __init__(self, app, _platform, theme, offline = False):
        super().__init__()
    
        self.scope_file_options_file='scope_file_settings.json'
        self.scope_working_directories_file = 'scope_folder_settings.json'
      
        self.working_directories = mcaUtil.restore_folder_settings(self.scope_working_directories_file)
        self.file_options = mcaUtil.restore_file_settings(self.scope_file_options_file)
        
        self.style_path = style_path

        self.app = app
        
        self.setStyle(theme)
        self.display_window = UltrasoundWidget(app, _platform, theme)
        #self.progress_bar = self.display_window.progress_bar
        
        self.arb_controller = ArbController(self)
        self.arb_filter_controller = ArbFilterController(self)
        self.afg_controller = AFGController(self, arb_controller = self.arb_controller, arb_filter_controller= self.arb_filter_controller,  offline = offline)
        
        self.save_data_controller = SaveDataController(self)
        self.scan_pv = self.arb_controller.scan_pv
        
        self.scope_controller = ScopeController(self, offline = offline)

        scope_waveform_widget = self.display_window.scope_widget
        self.scope_plot_controller = ScopePlotController(scope_controller = self.scope_controller,
                                                scope_widget= scope_waveform_widget)

        afg_waveform_widget = self.display_window.afg_widget
        self.afg_plot_controller = AFGPlotController(afg_controller = self.afg_controller,
                                                afg_waveform_widget= afg_waveform_widget)
                                                
        self.overlay_controller = OverlayController(self, self.scope_plot_controller)
        
        self.sweep_controller = SweepController(self,
                                                self.scope_controller.model.pvs, 
                                                self.afg_controller.model.pvs)
        self.waterfall_controller = WaterfallController(self)
        waterfall_widget = self.display_window.scan_widget
        self.waterfall_plotController = WaterfallPlotController(self.waterfall_controller,waterfall_widget)

        self.phase_controller = PhaseController(self.scope_plot_controller.plt,
                                                self.scope_plot_controller, self.working_directories)

        afg_panel = self.afg_controller.get_panel()
        scope_panel = self.scope_controller.get_panel()
        sweep_panel = self.sweep_controller.get_panel()
        arb_panel = self.arb_controller.get_panel()
        arb_filter_panel = self.arb_filter_controller.get_panel()
        save_data_panel = self.save_data_controller.get_panel()

        arb_and_filter_panel = Panel('USER1 waveform', 
                                        ['ArbModel:selected_item',
                                        'ArbModel:edit_state',
                                        'ArbFilter:selected_item',
                                        'ArbFilter:edit_state'])

        self.display_window.insert_panel(scope_panel)
        self.display_window.insert_panel(afg_panel)
        #self.display_window.insert_panel(arb_panel)
        #self.display_window.insert_panel(arb_filter_panel)
        self.display_window.insert_panel(arb_and_filter_panel)
        self.display_window.insert_panel_right(sweep_panel)
        self.display_window.insert_panel_right(save_data_panel)


        self.display_window.panelClosedSignal.connect(self.panel_closed_callback)
        
        
        self.waveform_index = 0
        self.current_tab_index = 0
        
        self.make_connections()

        self.pv_server = pvServer()

        # for some reason this helps resize the plots in the frames properly 
        self.display_window.afg_mode_btn.setChecked(True)
        self.display_window.scan_mode_btn.setChecked(True)
        self.display_window.scope_mode_btn.setChecked(True)

        

    def make_connections(self): 
        #self.display_window.tabWidget.currentChanged.connect(self.tab_changed)
        self.display_window.mode_btn_group.buttonToggled.connect(self.tab_changed)
        self.display_window.scope_mode_btn.toggled.connect(self.display_window.scope_widget.setVisible)
        self.display_window.afg_mode_btn.toggled.connect(self.display_window.afg_widget.setVisible)
        self.display_window.scan_mode_btn.toggled.connect(self.display_window.scan_widget.setVisible)


        self.sweep_controller.scanStartRequestSignal.connect(self.scanStartRequestCallback)
        self.sweep_controller.scanDoneSignal.connect(self.scanDoneCallback)
        self.scope_controller.model.pvs['run_state'].value_changed_signal.connect(self.scopeStoppedCallback)
        self.display_window.actionPreferences.triggered.connect(self.preferences_module)
        self.display_window.actionSave_As.triggered.connect(self.scopeSaveAsCallback)
        self.display_window.actionBG.triggered.connect(self.overlay_btn_callback)
        #self.display_window.actionBGclose.triggered.connect(self.close_background_callback)
        self.display_window.ActionRecallSetup.triggered.connect(self.RecallSetupCallback)
        self.display_window.ActionSaveSetup.triggered.connect(self.SaveSetupCallback)
        #self.display_window.ActionSetUserWaveform.triggered.connect(self.SetUserWaveformCallback)
        self.display_window.actionCursors.triggered.connect(self.cursorsCallback)

    
    def cursorsCallback(self):
        self.phase_controller.show_view()

    def tab_changed(self):
        if self.display_window.scope_mode_btn.isChecked():
            ind = 0
        elif self.display_window.afg_mode_btn.isChecked():
            ind = 1
        elif self.display_window.scan_mode_btn.isChecked():
            ind = 2
        else:
            return

        old_index = self.current_tab_index
        self.current_tab_index = ind

    

    def RecallSetupCallback(self):
        print('RecallSetupCallback')

    def SaveSetupCallback(self):
        print('SaveSetupCallback')

    
    def close_background_callback(self):
        
        self.scope_controller.close_background_callback()

    def overlay_btn_callback(self):
        self.overlay_controller.showWidget()

    def scopeSaveAsCallback(self):
        
        self.save_data_controller.save_data_callback()

    def preferences_module(self, *args, **kwargs):
        [ok, file_options] = mcaUtil.mcaFilePreferences.showDialog(self.display_window, self.file_options) 
        if ok :
            self.file_options = file_options
            if self.scope_controller.model != None:
                self.scope_controller.model.file_settings = file_options
            mcaUtil.save_file_settings(file_options, file=self.scope_file_options_file)

    def scopeStoppedCallback(self, pv, data):
        running  = data[0]
        if not running:
            #print('stopped')
            if self.file_options.autosave:
                self.save_data_controller.model.pvs['save'].set(True)
                
            if self.file_options.autorestart:
                pass
                #self.model.acq_erase_start()

    def scanStartRequestCallback(self):
        #print('starting frequency sweep!')
        self.controls_setEnable(False)
        self.sweep_controller.start_sweep()

    def scanDoneCallback(self):
        #print('ending frequency sweep!')
        self.controls_setEnable(True)

    def controls_setEnable(self, state):
        self.afg_controller.panelSetEnabled(state)
        self.scope_controller.panelSetEnabled(state)
        self.scope_plot_controller.widgetSetEnabled(state)

    def panel_closed_callback(self):
        self.afg_controller.exit()
        self.scope_controller.exit()
        self.sweep_controller.exit()
        self.arb_controller.exit()
        self.arb_filter_controller.exit()
        self.overlay_controller.overlay_widget.close()
        self.save_data_controller.exit()

    def show_window(self):
        self.display_window.raise_widget()

    '''def cursor_dragged(self, cursor):
        pos = cursor.getYPos()
        c1 = self.display_window.hLine1
        c2 = self.display_window.hLine2
        
        ind = int(math.floor(pos))
        self.show_waveform(ind)
        if c1 is not cursor:
            c1.setPos(pos)
        if c2 is not cursor:
            c2.setPos(pos)'''

    '''def up_down_signal_callback(self, event):
        new_ind = self.waveform_index
        if event == 'up':
            new_ind = self.waveform_index + 1
        if event == 'down':
            new_ind = self.waveform_index - 1
        self.show_waveform(new_ind, update_cursor_pos=True)
                
    def show_latest_waveform(self):
        freqs = sorted(list(self.model.sweep.keys()))
        freq = freqs[-1]
        ind = freqs.index(freq)
        self.show_waveform(ind, update_cursor_pos=True)


    def show_waveform(self, ind, update_cursor_pos=False):
        if ind != self.waveform_index:
            ans = self.model.get_waveform(ind)
            if ans is not None:
                sw, freq = ans[0], ans[1]
                if sw is not None:
                    self.display_window.plot_waveform(*sw,text=str(freq)+ ' MHz')
                    self.waveform_index = ind
                    if update_cursor_pos:
                        self.display_window.hLine1.setPos(ind+.5)
                        self.display_window.hLine2.setPos(ind+.5)'''

    '''def apply_callback(self):
        
        g = self.display_window.gradient
        state = g.saveState()
        print(state)
        
        pass'''

    def setStyle(self, Style):
        #print('style:  ' + str(Style))
        if Style==1:
            WStyle = 'plastique'
            file = open(os.path.join(self.style_path, "stylesheet.qss"))
            stylesheet = file.read()
            self.app.setStyleSheet(stylesheet)
            file.close()
            self.app.setStyle(WStyle)
        else:
            WStyle = "windowsvista"
            self.app.setStyleSheet(" ")
            #self.app.setPalette(self.win_palette)
            self.app.setStyle(WStyle)


    