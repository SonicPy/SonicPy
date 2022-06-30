#!/usr/bin/env python


import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage, QWidget
from PyQt5.QtCore import QObject, pyqtSignal, Qt

import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
import numpy as np

from um.widgets.PltWidget import SimpleDisplayWidget
from functools import partial

class ArrowPlotWidget(QWidget):
    

    up_down_signal = pyqtSignal(str)
    panelClosedSignal = pyqtSignal()
    point_clicked_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.initialized = False
        self.t = None
        self.spectrum = None
        self.setWindowTitle('Inverse frequency analysis')
        self.resize(600, 800)
        self.make_widget()
        self.create_plots()
        self.style_widgets()

    def create_plots(self):
        self.plot_win = self.win.fig.win
        self.main_plot = pg.PlotDataItem([], [], title="",
                        antialias=True, pen=None, symbolBrush=(255,0,100), symbolPen=None, symbolSize = 9)
        self.maximums = pg.PlotDataItem([], [], title="",
                        antialias=True, pen=None, symbolBrush=(0,100,255), symbolPen=None, symbolSize = 9)
        self.max_line_plot = pg.PlotDataItem([], [], title="",
                        antialias=True, pen=pg.mkPen(color=(255,255,255,150), width=2), connect="finite" )
        self.main_plot.sigPointsClicked.connect(self.point_clicked)
        self.maximums.sigPointsClicked.connect(self.point_clicked)
        self.plot_win.addItem(self.max_line_plot)
        self.plot_win.addItem(self.main_plot)
        self.plot_win.addItem(self.maximums)

    def point_clicked(self, item, pt):
        point = [pt[0].pos().x(),pt[0].pos().y()]
        self.point_clicked_signal.emit(point)

    def update_max_line(self, xData, yData):
        if xData is not None and yData is not None:
            self.max_line_plot.setData(xData, yData)

    def update_view(self, xData, yData):
        
        if xData is not None and yData is not None:
            self.main_plot.setData(xData, yData)
    def update_maximums(self, xData, yData):
        
        if xData is not None and yData is not None:
            self.maximums.setData(xData, yData)

    def get_cursor_pos(self):
        return self.win.fig.win.get_cursor_pos()
         
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
        self.auto_btn = QtWidgets.QPushButton("Auto")
        self.calc_btn = QtWidgets.QPushButton("Calculate")
        self.del_btn = QtWidgets.QPushButton('Delete')
        self.clear_btn = QtWidgets.QPushButton('Clear')
        self.fname_lbl = QtWidgets.QLineEdit('')
        freq_lbl = QtWidgets.QLabel('   Inverse Frequency (1/MHz):')
        self.freq_ebx = QtWidgets.QDoubleSpinBox()
        self.freq_ebx.setMaximum(100)
        self.freq_ebx.setMinimum(1)
        self.freq_ebx.setValue(21)
        self.N_cbx = QtWidgets.QCheckBox('+/-')
        self.N_cbx.setChecked(True)
        self.save_btn = QtWidgets.QPushButton('Save result')

        
        #_buttons_layout_top.addWidget(self.open_btn)
        _buttons_layout_top.addWidget(self.N_cbx)
        _buttons_layout_top.addWidget(self.calc_btn)
        _buttons_layout_top.addWidget(self.auto_btn)
        _buttons_layout_top.addWidget(self.del_btn)
        _buttons_layout_top.addWidget(self.clear_btn)
        
        _buttons_layout_top.addSpacerItem(HorizontalSpacerItem())
        #_buttons_layout_top.addWidget(self.save_btn)

        buttons_widget_top.setLayout(_buttons_layout_top)
        _layout.addWidget(buttons_widget_top)
        params = "Arrow Plot", 'Time delay (s)', 'Inverse frequency (1/Hz)'
        self.win = SimpleDisplayWidget(params)
        
        _layout.addWidget(self.win)


       
        detail_widget.setLayout(_detail_layout)
        _layout.addWidget(detail_widget)
        
        self.output_condition_lbl =QtWidgets.QLabel('')
        _buttons_layout_bottom.addWidget(self.output_condition_lbl)
        self.output_ebx = QtWidgets.QLineEdit('')
        _buttons_layout_bottom.addWidget(self.output_ebx)
        #_buttons_layout_bottom.addSpacerItem(HorizontalSpacerItem())
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




