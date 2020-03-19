#!/usr/bin/env python


import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage, QWidget
from PyQt5.QtCore import QObject, pyqtSignal, Qt

import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
import numpy as np

from um.widgets.PltWidget import SimpleDisplayWidget, customWidget
from functools import partial

class ArrowPlotWidget(QWidget):
    

    up_down_signal = pyqtSignal(str)
    panelClosedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initialized = False
        self.t = None
        self.spectrum = None
        self.setWindowTitle('Arrow Plot')
        self.resize(600, 800)
        self.make_widget()
        self.create_plots()
        self.style_widgets()

    def create_plots(self):
        self.plot_win = self.win.fig.win
        self.main_plot = pg.PlotDataItem([], [], title="",
                        antialias=True, pen=None, symbolBrush=(255,0,255), symbolPen=None, symbolSize = 5)
        self.plot_win.addItem(self.main_plot)

    def update_view(self, xData, yData):
        self.xData, self.yData = xData, yData
        if xData is not None and yData is not None:
            self.main_plot.setData(self.xData, self.yData)
         
    def make_widget(self):
        my_widget = self
        _layout = QtWidgets.QVBoxLayout()
        _layout.setContentsMargins(10, 10, 10, 10)
        detail_widget = QtWidgets.QWidget()
        _detail_layout = QtWidgets.QHBoxLayout()
        _detail_layout.setContentsMargins(0, 0, 0, 0)
        buttons_widget_top = QtWidgets.QWidget()
        _buttons_layout_top = QtWidgets.QHBoxLayout()
        _buttons_layout_top.setContentsMargins(0, 0, 0, 0)
        buttons_widget_bottom = QtWidgets.QWidget()
        _buttons_layout_bottom = QtWidgets.QHBoxLayout()
        _buttons_layout_bottom.setContentsMargins(0, 0, 0, 0)
        self.open_btn = QtWidgets.QPushButton("Open")
        self.clear_btn = QtWidgets.QPushButton('clear')
        self.fname_lbl = QtWidgets.QLineEdit('')
        freq_lbl = QtWidgets.QLabel('   Frequency (MHz):')
        self.freq_ebx = QtWidgets.QDoubleSpinBox()
        self.freq_ebx.setMaximum(100)
        self.freq_ebx.setMinimum(1)
        self.freq_ebx.setValue(21)
        self.N_cbx = QtWidgets.QCheckBox('+/-')
        self.N_cbx.setChecked(True)
        self.save_btn = QtWidgets.QPushButton('Save result')

        
        _buttons_layout_top.addWidget(self.open_btn)
        _buttons_layout_top.addWidget(self.clear_btn)
        _buttons_layout_top.addWidget(self.N_cbx)
        _buttons_layout_top.addSpacerItem(HorizontalSpacerItem())
        _buttons_layout_top.addWidget(self.save_btn)

        buttons_widget_top.setLayout(_buttons_layout_top)
        _layout.addWidget(buttons_widget_top)
        params = "Ultrasound echo analysis", 'Amplitude', 'Time'
        self.win = customWidget(params)
        _layout.addWidget(self.win)

       
        detail_widget.setLayout(_detail_layout)
        _layout.addWidget(detail_widget)
        self.calc_btn = QtWidgets.QPushButton('Correlate')
        #_buttons_layout_bottom.addWidget(calc_btn)
        #_buttons_layout_bottom.addWidget(QtWidgets.QLabel('2-way travel time:'))
        self.output_ebx = QtWidgets.QLineEdit('')
        #_buttons_layout_bottom.addWidget(output_ebx)
        _buttons_layout_bottom.addSpacerItem(HorizontalSpacerItem())
        buttons_widget_bottom.setLayout(_buttons_layout_bottom)
        _layout.addWidget(buttons_widget_bottom)
        my_widget.setLayout(_layout)
        

    def closeEvent(self, QCloseEvent, *event):
        self.panelClosedSignal.emit()
        super().closeEvent(QCloseEvent, *event)
        

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
 

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()  




