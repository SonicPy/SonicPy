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

        self.freq_btns_list = []
        self.cond_btns_list = []


    def make_widget(self):
        
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(10, 10, 10, 10)
        self.detail_widget = QtWidgets.QWidget()
        self._detail_layout = QtWidgets.QHBoxLayout()
        self._detail_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget_top = QtWidgets.QWidget()
        self._buttons_layout_top = QtWidgets.QHBoxLayout()
        self._buttons_layout_top.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget_bottom_single_frequency = QtWidgets.QWidget()
        self.buttons_widget_bottom_single_condition = QtWidgets.QWidget()
        
        self._buttons_layout_bottom_single_frequency = QtWidgets.QHBoxLayout()
        self._buttons_layout_bottom_single_frequency.setContentsMargins(0, 0, 0, 0)
        self._buttons_layout_bottom_single_condition = QtWidgets.QHBoxLayout()
        self._buttons_layout_bottom_single_condition.setContentsMargins(0, 0, 0, 0)
        
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
       
        self._buttons_layout_top.addWidget(self.open_btn)
        self._buttons_layout_top.addWidget(self.fname_lbl)
        self._buttons_layout_top.addWidget(self.scale_lbl)
        self._buttons_layout_top.addWidget(self.scale_ebx)
        self._buttons_layout_top.addWidget(self.clip_cbx)
        
        self._buttons_layout_top.addWidget(self.save_btn)
        self._buttons_layout_top.addSpacerItem(HorizontalSpacerItem())
        

        self.buttons_widget_top.setLayout(self._buttons_layout_top)
        self._layout.addWidget(self.buttons_widget_top)

        self.plots_tab_widget= QtWidgets.QTabWidget(self)
        self.plots_tab_widget.setObjectName("plots_tab_widget")

        self.single_frequency_widget = QtWidgets.QWidget(self.plots_tab_widget)
        self._single_frequency_widget_layout = QtWidgets.QVBoxLayout(self.single_frequency_widget)
        self._single_frequency_widget_layout.setContentsMargins(0,0,0,0)
        params = ["Waterfall plot", 'Pressure point', 'Time']
        self.single_frequency_waterfall = WaterfallWidget(params=params)
        self._single_frequency_widget_layout.addWidget(self.single_frequency_waterfall)
        self.freqs_widget = QtWidgets.QWidget(self.buttons_widget_bottom_single_frequency)
        self._freqs_widget_layout = QtWidgets.QHBoxLayout(self.freqs_widget )
        self._freqs_widget_layout.setSpacing(0)
        self.freq_btns = QtWidgets.QButtonGroup( self.freqs_widget)
        self.freqs_widget.setLayout(self._freqs_widget_layout)
        self._buttons_layout_bottom_single_frequency.addWidget(self.freqs_widget)
        self.buttons_widget_bottom_single_frequency.setLayout(self._buttons_layout_bottom_single_frequency)
        self._single_frequency_widget_layout.addWidget(self.buttons_widget_bottom_single_frequency)
        self.plots_tab_widget.addTab(self.single_frequency_widget, 'Single Frequency')

        self.single_condition_widget = QtWidgets.QWidget(self.plots_tab_widget)
        self._single_condition_widget_layout = QtWidgets.QVBoxLayout(self.single_condition_widget)
        self._single_condition_widget_layout.setContentsMargins(0,0,0,0)
        params = ["Waterfall plot", 'Frequency point', 'Time']
        self.single_condition_waterfall = WaterfallWidget(params=params)
        self._single_condition_widget_layout.addWidget(self.single_condition_waterfall)
        self.conds_widget = QtWidgets.QWidget(self.buttons_widget_bottom_single_condition)
        self._conds_widget_layout = QtWidgets.QHBoxLayout(self.conds_widget )
        self._conds_widget_layout.setSpacing(0)
        self.cond_btns = QtWidgets.QButtonGroup( self.conds_widget)
        self.conds_widget.setLayout(self._conds_widget_layout)
        self._buttons_layout_bottom_single_condition.addWidget(self.conds_widget)
        self.buttons_widget_bottom_single_condition.setLayout(self._buttons_layout_bottom_single_condition)
        self._single_condition_widget_layout.addWidget(self.buttons_widget_bottom_single_condition)
        self.plots_tab_widget.addTab(self.single_condition_widget, 'Single P-T Condition')


        self._layout.addWidget(self.plots_tab_widget)
        self.setLayout(self._layout)

    def set_freq_buttons(self, num):

        for b in self.freq_btns_list:
            self._freqs_widget_layout.removeWidget(b)
            self.freq_btns.removeButton(b)
            b.deleteLater()
            b= None
        self.freq_btns_list.clear()

        for f in range(num):
            btn = QtWidgets.QPushButton(str(f))
            btn.setObjectName('freq_btn')
            btn.setCheckable(True)
            self.freq_btns_list.append(btn)
            self.freq_btns.addButton(btn)
            self._freqs_widget_layout.addWidget(btn)

        self.freq_btns_list[0].setObjectName('freq_btn_first')
        self.freq_btns_list[-1].setObjectName('freq_btn_last')
        
    def set_cond_buttons(self, num):

        for b in self.cond_btns_list:
            self._conds_widget_layout.removeWidget(b)
            self.cond_btns.removeButton(b)
            b.deleteLater()
            b= None
        self.cond_btns_list.clear()

        for f in range(num):
            btn = QtWidgets.QPushButton(str(f))
            btn.setObjectName('cond_btn')
            btn.setCheckable(True)
            self.cond_btns_list.append(btn)
            self.cond_btns.addButton(btn)
            self._conds_widget_layout.addWidget(btn)

        self.cond_btns_list[0].setObjectName('cond_btn_first')
        self.cond_btns_list[-1].setObjectName('cond_btn_last')    
        

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()  




