#!/usr/bin/env python


import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt

import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
import numpy as np

from um.widgets.PltWidget import SimpleDisplayWidget, customWidget
from functools import partial

class ImageAnalysisWidget(QMainWindow):
    
    preferences_signal = pyqtSignal()
    up_down_signal = pyqtSignal(str)
    panelClosedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initialized = False
        self.t = None
        self.spectrum = None


        self.setWindowTitle('Image Analysis')

        self.resize(1250, 800)
        
        self.make_widget()


        self.setCentralWidget(self.my_widget)

        self.create_plots()
        self.create_menu()
        self.style_widgets()

    def create_plots(self):

        pass
        

    def get_echo_bounds(self, i):
        return self.echo_bounds[i].getRegion()

    def update_view(self, image):
        
        print(image)



    def make_widget(self):
        self.my_widget = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(10, 10, 10, 10)
        self.detail_widget = QtWidgets.QWidget()
        self._detail_layout = QtWidgets.QHBoxLayout()
        self._detail_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget_top = QtWidgets.QWidget()
        self._buttons_layout_top = QtWidgets.QHBoxLayout()
        self._buttons_layout_top.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget_bottom = QtWidgets.QWidget()
        self._buttons_layout_bottom = QtWidgets.QHBoxLayout()
        self._buttons_layout_bottom.setContentsMargins(0, 0, 0, 0)
        self.open_btn = QtWidgets.QPushButton("Open")
        self.fname_lbl = QtWidgets.QLineEdit('')
        
        self.save_btn = QtWidgets.QPushButton('Save result')
        
        
        self._buttons_layout_top.addWidget(self.open_btn)
        self._buttons_layout_top.addWidget(self.fname_lbl)
       
        
        self._buttons_layout_top.addWidget(self.save_btn)
        self._buttons_layout_top.addSpacerItem(HorizontalSpacerItem())
        

        self.buttons_widget_top.setLayout(self._buttons_layout_top)
        self._layout.addWidget(self.buttons_widget_top)
        params = "Image echo analysis", 'Amplitude', 'Time'
        self.imv = pg.ImageView(self.my_widget)
        self.imv_filtered = pg.ImageView(self.my_widget)
        self._layout.addWidget(self.imv)
        self._layout.addWidget(self.imv_filtered)
        
        calc_btn = QtWidgets.QPushButton('Correlate')
        #_buttons_layout_bottom.addWidget(calc_btn)
        #_buttons_layout_bottom.addWidget(QtWidgets.QLabel('2-way travel time:'))
        output_ebx = QtWidgets.QLineEdit('')
        #_buttons_layout_bottom.addWidget(output_ebx)
        self._buttons_layout_bottom.addSpacerItem(HorizontalSpacerItem())
        self.buttons_widget_bottom.setLayout(self._buttons_layout_bottom)
        self._layout.addWidget(self.buttons_widget_bottom)
        self.my_widget.setLayout(self._layout)
        

    def closeEvent(self, QCloseEvent, *event):
        self.panelClosedSignal.emit()
        

    def keyPressEvent(self, e):
        event = None
        if e.key() == Qt.Key_Up:
            event = 'up'
        if e.key() == Qt.Key_Down:
            event = 'down'
        if event is not None:
            self.up_down_signal.emit(event)


    def style_widgets(self):
        
        self.setStyleSheet("""
            #scope_waveform_widget FlatButton {
                min-width: 70;
                max-width: 70;
            }
            #scope_waveform_widget QLabel {
                min-width: 110;
                max-width: 110;
            }
            #controls_sidebar QLineEdit {
                min-width: 120;
                max-width: 120;
            }
            #controls_sidebar QLabel {
                min-width: 110;
                max-width: 110;
            }
            
        """)
 
 
    def create_menu(self):

        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 793, 22))
        
        self.file_save_hdf5_act = QtWidgets.QAction('Save to HDF5', self)    
        self.actionSave_next = QtWidgets.QAction("Save", self)
        self.actionSave_As = QtWidgets.QAction("Save as...", self)
        self.actionPreferences = QtWidgets.QAction("Preferences", self)
        self.actionBG = QtWidgets.QAction("Overlay", self)
        self.actionBGclose = QtWidgets.QAction("Close overlay", self)
        self.actionCursors = QtWidgets.QAction("Phase", self)
        
        
        self.ActionRecallSetup = QtWidgets.QAction('Recall setup', self)        
        self.ActionSaveSetup = QtWidgets.QAction('Save setup', self)   
        self.ActionSetUserWaveform = QtWidgets.QAction('Edit user waveform', self)   
        self.setMenuBar(self.menuBar)

    def preferences_module(self):
        self.preferences_signal.emit()

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()  




