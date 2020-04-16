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
from um.widgets.UltrasoundWidget_2 import UltrasoundWidget
from um.controllers.SweepController import SweepController
from um.controllers.AFGController import AFGController
from um.controllers.ScopeController import ScopeController
from um.controllers.ScopePlotController import ScopePlotController
from um.controllers.ArbController import ArbController
from um.controllers.ArbFilterController import ArbFilterController
from um.controllers.SaveDataController import SaveDataController

from um.controllers.OverlayController import OverlayController

from um.models.WaveformModel import Waveform
import math

from um.controllers.PhaseController import PhaseController

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename, increment_filename_extra

from .. import style_path

from um.models.pvServer import pvServer

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
        
        self.afg_controller = AFGController(self, offline = offline)
        self.arb_controller = ArbController(self)
        self.save_data_controller = SaveDataController(self)
        self.scan_pv = self.arb_controller.scan_pv
        self.arb_filter_controller = ArbFilterController(self)
        self.scope_controller = ScopeController(self, offline = offline)
        self.scope_plot_controller = ScopePlotController(self.scope_controller, 
                                                afg_controller=self.afg_controller, 
                                                save_data_controller=self.save_data_controller)
        self.overlay_controller = OverlayController(self, self.scope_plot_controller)
        
        self.sweep_controller = SweepController(self,
                                                self.scope_controller.model.pvs, 
                                                self.afg_controller.model.pvs)


        self.phase_controller = PhaseController(self.scope_plot_controller.plt,
                                                self.scope_plot_controller, self.working_directories)

        afg_panel = self.afg_controller.get_panel()
        scope_panel = self.scope_controller.get_panel()
        sweep_widget = self.sweep_controller.get_panel()
        arb_panel = self.arb_controller.get_panel()
        arb_filter_panel = self.arb_filter_controller.get_panel()

        self.display_window.insert_panel(scope_panel)
        self.display_window.insert_panel(afg_panel)
        self.display_window.insert_panel(arb_panel)
        self.display_window.insert_panel(arb_filter_panel)
        self.display_window.insert_panel(sweep_widget)

        scope_waveform_widget = self.scope_plot_controller.widget
        self.display_window.scope_waveform_layout.addWidget(scope_waveform_widget)

        self.display_window.panelClosedSignal.connect(self.panel_closed_callback)
        
        
        self.waveform_index = 0
        
        
        self.make_connections()

        self.pv_server = pvServer()
        

    def make_connections(self): 
        self.sweep_controller.scanStartRequestSignal.connect(self.scanStartRequestCallback)
        self.sweep_controller.scanDoneSignal.connect(self.scanDoneCallback)
        self.scope_controller.model.pvs['run_state'].value_changed_signal.connect(self.scopeStoppedCallback)
        self.display_window.actionPreferences.triggered.connect(self.preferences_module)
        self.display_window.actionSave_As.triggered.connect(self.scopeSaveAsCallback)
        self.display_window.actionBG.triggered.connect(self.overlay_btn_callback)
        #self.display_window.actionBGclose.triggered.connect(self.close_background_callback)
        self.display_window.ActionRecallSetup.triggered.connect(self.RecallSetupCallback)
        self.display_window.ActionSaveSetup.triggered.connect(self.SaveSetupCallback)
        self.display_window.ActionSetUserWaveform.triggered.connect(self.SetUserWaveformCallback)
        self.display_window.actionCursors.triggered.connect(self.cursorsCallback)

        # User waveform events
        self.arb_controller.waveformComputedSignal.connect(self.waveform_computed_callback)
        self.arb_filter_controller.waveformFilteredcallbackSignal.connect(self.waveform_filtered_callback)
    
    def cursorsCallback(self):
        self.phase_controller.show_view()

    def SetUserWaveformCallback(self):

        
        '''
        arb = get_arb()
        waveform={}
        waveform['binary_waveform'] = arb

        self.afg_controller.model.pvs['user1_waveform'].set(copy.deepcopy(waveform))
        '''

    def RecallSetupCallback(self):
        print('RecallSetupCallback')

    def SaveSetupCallback(self):
        print('SaveSetupCallback')

    
    def close_background_callback(self):
        
        self.scope_controller.close_background_callback()

    def overlay_btn_callback(self):
        self.overlay_controller.showWidget()

    def scopeSaveAsCallback(self):
        start_folder = self.working_directories.savedata 
        self.save_data_controller.save_data_callback(folder=start_folder)

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
                fname = self.save_data_controller.model.pvs['filename']._val
                if fname != '':
                    freq = None
                    try:
                        afg_pvs = self.afg_controller.model.pvs
                        freq = afg_pvs['frequency']._val
                    except:
                        pass
                    new_file = increment_filename_extra(fname, frequency = freq)
                    print(new_file)
                    if new_file != fname:
                        self.saveFile(new_file)
                        #print('save: ' + new_file)
            if self.file_options.autorestart:
                pass
                #self.model.acq_erase_start()

    

    def saveFile(self, filename, params = {}):
        afg_pvs = self.afg_controller.model.pvs
        saved_filename = self.save_data_controller.save_data_callback(filename=filename, params=params)
        new_folder = os.path.dirname(str(saved_filename))
        old_folder = self.working_directories.savedata
        if new_folder != old_folder:
            self.working_directories.savedata = new_folder
            mcaUtil.save_folder_settings(self.working_directories, self.scope_working_directories_file)

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

    def show_window(self):
        self.display_window.raise_widget()

    def cursor_dragged(self, cursor):
        pos = cursor.getYPos()
        c1 = self.display_window.hLine1
        c2 = self.display_window.hLine2
        
        ind = int(math.floor(pos))
        self.show_waveform(ind)
        if c1 is not cursor:
            c1.setPos(pos)
        if c2 is not cursor:
            c2.setPos(pos)

    def up_down_signal_callback(self, event):
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
                        self.display_window.hLine2.setPos(ind+.5)

    def apply_callback(self):
        '''
        g = self.display_window.gradient
        state = g.saveState()
        print(state)
        '''
        pass

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


    ####################################################
    ### Next is the User waveform handling
    ####################################################

    def waveform_computed_callback(self, data):
        
        if len(data):
            t = data['t']
            waveform = data['waveform']
            #self.arb_controller.arb_edit_controller.widget.update_plot([t,waveform])
            self.arb_filter_controller.model.pvs['waveform_in'].set(data)
            
    
    def waveform_filtered_callback(self, data):
        if len(data):
            t = np.asarray(data['t'])
            waveform = np.asarray(data['waveform'])
            out = {'waveform':(t,waveform),'ch':1, 'time':1, 'num_acq':1000}
            self.arb_filter_controller.arb_filter_edit_controller.widget.update_plot([t,waveform])
            #self.scope_controller.model.pvs['waveform'].set(out)