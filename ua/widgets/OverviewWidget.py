#!/usr/bin/env python


import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage, QWidget
from PyQt5.QtCore import QObject, pyqtSignal, Qt

import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
import numpy as np

from functools import partial

from ua.widgets.WaterfallWidget import WaterfallWidget

class OverViewWidget(QWidget):
    
    preferences_signal = pyqtSignal()
    up_down_signal = pyqtSignal(str)
    panelClosedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initialized = False
        self.t = None
        self.spectrum = None


        self.setWindowTitle('Time-of-flight analysis')

        self.resize(800, 800)
        
        self.make_widget()

        



    def make_widget(self):
        
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
        self.scale_lbl = QtWidgets.QLabel('   Scale:')
        self.scale_ebx = QtWidgets.QDoubleSpinBox()
        self.scale_ebx.setMaximum(100)
        self.scale_ebx.setMinimum(1)
        self.scale_ebx.setValue(21)
        self.clip_cbx = QtWidgets.QCheckBox('Clip')
        self.clip_cbx.setChecked(True)
        self.save_btn = QtWidgets.QPushButton('Save result')
        self.waterfall_plt_btn = QtWidgets.QPushButton('Waterfall')
        
        self._buttons_layout_top.addWidget(self.open_btn)
        self._buttons_layout_top.addWidget(self.fname_lbl)
        self._buttons_layout_top.addWidget(self.scale_lbl)
        self._buttons_layout_top.addWidget(self.scale_ebx)
        self._buttons_layout_top.addWidget(self.clip_cbx)
        
        self._buttons_layout_top.addWidget(self.save_btn)
        self._buttons_layout_top.addSpacerItem(HorizontalSpacerItem())
        self._buttons_layout_top.addWidget(self.waterfall_plt_btn)

        self.buttons_widget_top.setLayout(self._buttons_layout_top)
        self._layout.addWidget(self.buttons_widget_top)
        params = ["Waterfall plot", 'Pressure point', 'Time']
        self.win = WaterfallWidget(params=params)
        self._layout.addWidget(self.win)

        
        calc_btn = QtWidgets.QPushButton('Correlate')
        #_buttons_layout_bottom.addWidget(calc_btn)
        #_buttons_layout_bottom.addWidget(QtWidgets.QLabel('2-way travel time:'))
        output_ebx = QtWidgets.QLineEdit('')
        #_buttons_layout_bottom.addWidget(output_ebx)
       
        
        self.buttons_widget_bottom.setLayout(self._buttons_layout_bottom)
        self._layout.addWidget(self.buttons_widget_bottom)
        self.setLayout(self._layout)

    def set_freq_buttons(self, num):

        self.freqs_widget = QtWidgets.QWidget(self.buttons_widget_bottom)
        self._freqs_widget_layout = QtWidgets.QHBoxLayout(self.freqs_widget )
        self._freqs_widget_layout.setSpacing(0)

        self.freq_btns = QtWidgets.QButtonGroup( self.freqs_widget)
        self.freq_btns_list = []
        for f in range(num):
            btn = QtWidgets.QPushButton(str(f))
            btn.setObjectName('freq_btn')
            btn.setCheckable(True)
            self.freq_btns_list.append(btn)
            self.freq_btns.addButton(btn)
            self._freqs_widget_layout.addWidget(btn)

        self.freq_btns_list[0].setObjectName('freq_btn_first')
        self.freq_btns_list[-1].setObjectName('freq_btn_last')
        
        self.freqs_widget.setLayout(self._freqs_widget_layout)
        self._buttons_layout_bottom.addWidget(self.freqs_widget)
        #self._buttons_layout_bottom.addSpacerItem(HorizontalSpacerItem())
        

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()  




