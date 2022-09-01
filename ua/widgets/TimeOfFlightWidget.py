#!/usr/bin/env python


import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt

import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
import numpy as np

from functools import partial

from ua.widgets.WaterfallWidget import WaterfallWidget

class TimeOfFlightWidget(QMainWindow):
    
    preferences_signal = pyqtSignal()
    up_down_signal = pyqtSignal(str)
    panelClosedSignal = pyqtSignal()

    def __init__(self, app, overview_widget, multiple_frequencies_widget, analysis_widget, arrow_plot_widget):
        super().__init__()
        self.app = app
        self.overview_widget = overview_widget

        self.multiple_frequencies_widget = multiple_frequencies_widget
        self.analysis_widget = analysis_widget

        self.middle_widget = QtWidgets.QWidget()
        self._middle_widget_layout = QtWidgets.QVBoxLayout()
        self._middle_widget_layout.addWidget(self.analysis_widget)
        self._middle_widget_layout.addWidget(self.multiple_frequencies_widget)
        
        self.middle_widget.setLayout(self._middle_widget_layout)

        self.arrow_plot_widget = arrow_plot_widget

        #self.analysis_widget.resize(800,800)


        self.setWindowTitle('Time-of-flight analysis. (C) R. Hrubiak 2021')

        self.resize(1920, 1000)
        
        self.make_widget()

        self.setCentralWidget(self.my_widget)

        self.create_menu()
        self.style_widgets()

    def closeEvent(self, QCloseEvent, *event):
        self.app.closeAllWindows()
        self.panelClosedSignal.emit()

    def make_widget(self):
        self.my_widget = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.detail_widget = QtWidgets.QWidget()
        self._detail_layout = QtWidgets.QHBoxLayout()
        self._detail_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget_top = QtWidgets.QWidget()
        self._buttons_layout_top = QtWidgets.QHBoxLayout()
        self._buttons_layout_top.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget_bottom = QtWidgets.QWidget()
        
        self._buttons_layout_bottom = QtWidgets.QHBoxLayout()
        self._buttons_layout_bottom.setContentsMargins(0, 0, 0, 0)
        
        

        
        self._buttons_layout_top.addSpacerItem(HorizontalSpacerItem())
        
        self.buttons_widget_top.setLayout(self._buttons_layout_top)
        #self._layout.addWidget(self.buttons_widget_top)
        
        
        self.center_widget = QtWidgets.QWidget(self)
        self._center_widget_layout = QtWidgets.QHBoxLayout(self.center_widget)

        

        self.splitter_horizontal = QtWidgets.QSplitter(Qt.Horizontal)

        self.splitter_horizontal.addWidget(self.overview_widget)



        self.splitter_horizontal.addWidget(self.middle_widget)

        self.splitter_horizontal.addWidget(self.arrow_plot_widget)
        
        self.splitter_horizontal.setSizes([600,600, 600])

        self._center_widget_layout.addWidget(self.splitter_horizontal)


        self.center_widget.setLayout(self._center_widget_layout)
        self._layout.addWidget(self.center_widget)

        
        calc_btn = QtWidgets.QPushButton('Correlate')
        #_buttons_layout_bottom.addWidget(calc_btn)
        #_buttons_layout_bottom.addWidget(QtWidgets.QLabel('2-way travel time:'))
        output_ebx = QtWidgets.QLineEdit('')
        #_buttons_layout_bottom.addWidget(output_ebx)
       
        
        self.buttons_widget_bottom.setLayout(self._buttons_layout_bottom)
        #self._layout.addWidget(self.buttons_widget_bottom)
        self.my_widget.setLayout(self._layout)

    

        

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
        #self.file_menu = self.menuBar.addMenu('Tools')
        self.file_save_hdf5_act = QtWidgets.QAction('Save to HDF5', self)    
        self.actionSave_next = QtWidgets.QAction("Save", self)
        self.actionSave_As = QtWidgets.QAction("Save as...", self)
        self.actionPreferences = QtWidgets.QAction("Preferences", self)
        self.actionBG = QtWidgets.QAction("Overlay", self)
        self.actionBGclose = QtWidgets.QAction("Close overlay", self)
        self.actionCursors = QtWidgets.QAction("Phase", self)
        self.actionArrowPlot = QtWidgets.QAction("Arrow Plot", self)
        #self.file_menu.addAction(self.actionSave_As)    
        #self.file_menu.addAction(self.actionPreferences)  
        #self.file_menu.addAction(self.actionBG) 
        #self.file_menu.addAction(self.actionCursors) 
        #self.file_menu.addAction(self.actionArrowPlot) 
        #self.opts_menu = self.menuBar.addMenu('Arb')
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




