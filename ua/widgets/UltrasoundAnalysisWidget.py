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

class UltrasoundAnalysisWidget(QMainWindow):
    
    preferences_signal = pyqtSignal()
    up_down_signal = pyqtSignal(str)
    panelClosedSignal = pyqtSignal()

    def __init__(self,app,_platform,Theme):
        super().__init__()
        self.initialized = False
        self.t = None
        self.spectrum = None


        self.setWindowTitle('Ultrasound Analysis')
        self.Theme = Theme
        self.app = app  # app object
        self.resize(1250, 800)
        

        self.my_widget, self.win, self.detail_win1, \
            self.detail_win2, self.open_btn, self.calc_btn,\
                 self.output_ebx, self.fname_lbl = self.make_widget()


        self.setCentralWidget(self.my_widget)

        self.create_plots()
        self.create_menu()
        self.style_widgets()

    def create_plots(self):

        self.plot_win = self.win.fig.win
        self.main_plot = pg.PlotDataItem([], [], title="",
                        antialias=True, pen=pg.mkPen(color=(255,255,0), width=1), connect="finite" )
        self.plot_win.addItem(self.main_plot)
        self.plot_win_detail1 = self.detail_win1.fig.win
        self.plot_win_detail2 = self.detail_win2.fig.win
        

        self.detail_plot1 = pg.PlotDataItem([],[], title="",
                        antialias=True, pen=pg.mkPen(color=(0,200,255), width=1), connect="finite" )
        self.detail_plot1_bg = pg.PlotDataItem([], [], title="",
                        antialias=True, pen=pg.mkPen(color=(255,0,100), width=1), connect="finite" )
        self.plot_win_detail1.addItem(self.detail_plot1)
        self.plot_win_detail1.addItem(self.detail_plot1_bg)

        self.detail_plot2 = pg.PlotDataItem([], [], title="",
                        antialias=True, pen=pg.mkPen(color=(0,255,100), width=1), connect="finite" )
        self.detail_plot2_bg = pg.PlotDataItem([], [], title="",
                        antialias=True, pen=None, symbolBrush=(255,0,255,70), symbolPen=None)
        self.plot_win_detail2.addItem(self.detail_plot2)
        self.plot_win_detail2.addItem(self.detail_plot2_bg)

        self.lr1 = pg.LinearRegionItem()
        self.lr1.setZValue(-10)
        self.lr2 = pg.LinearRegionItem()
        self.lr2.setZValue(-10)

        

        self.echo_bounds = [self.lr1, self.lr2]

    def get_echo_bounds(self, i):
        return self.echo_bounds[i].getRegion()

    def update_view(self, t, spectrum, fname):
        
        self.t, self.spectrum, self.fname = t, spectrum, fname
        if t is not None and spectrum is not None:
            self.main_plot.setData(self.t, self.spectrum,)
            #self.detail_plot1.setData(self.t, self.spectrum,)
            #self.detail_plot2.setData(self.t, self.spectrum,)
            
            if not self.initialized:

                self.init_region_items(self.t)
            self.fname_lbl.setText(self.fname)


    def updatePlot1(self):
        self.lr1r = self.lr1.getRegion()
        self.plot_win_detail1.setXRange(*self.lr1r, padding=0)

    def updateRegion1(self):
        self.lr1.setRegion(self.detail_plot1.getViewBox().viewRange()[0])
        
    def updatePlot2(self):
        self.lr2r = self.lr2.getRegion()
        self.plot_win_detail2.setXRange(*self.lr2r, padding=0)

    def updateRegion2(self):
        self.lr2.setRegion(self.detail_plot2.getViewBox().viewRange()[0])

    def init_region_items(self, t):
        
        self.plot_win.addItem(self.lr1)
        self.plot_win.addItem(self.lr2) 
        p1l, p1r, p2l, p2r = self.get_initial_lr_positions(t)

        self.lr1.setRegion([p1l, p1r])
        self.lr2.setRegion([p2l, p2r])

        self.initialized = True
        
       

    def get_initial_lr_positions(self, t):
        mn = min(t)
        mx = max(t)
        r = mx-mn
        p1l = 0.25 * r
        p1r = 0.3 * r
        p2l = 0.7 * r
        p2r = 0.75 * r 
        return p1l, p1r, p2l, p2r

    def get_initial_lr_zoom_positions(self, region):
        lr = region.getRegion()
        rng = lr[1] - lr[0]
        l = lr[0]+ rng*0.4
        r = lr[1] + rng*0.6
        return l, r


    def make_widget(self):
        my_widget = QtWidgets.QWidget()
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
        open_btn = QtWidgets.QPushButton("Open")
        fname_lbl = QtWidgets.QLineEdit('')
        freq_lbl = QtWidgets.QLabel('   Frequency (MHz):')
        self.freq_ebx = QtWidgets.QDoubleSpinBox()
        self.freq_ebx.setMaximum(100)
        self.freq_ebx.setMinimum(1)
        self.freq_ebx.setValue(21)
        self.N_cbx = QtWidgets.QCheckBox('+/-')
        self.N_cbx.setChecked(True)
        self.save_btn = QtWidgets.QPushButton('Save result')

        
        _buttons_layout_top.addWidget(open_btn)
        _buttons_layout_top.addWidget(fname_lbl)
        _buttons_layout_top.addWidget(freq_lbl)
        _buttons_layout_top.addWidget(self.freq_ebx)
        _buttons_layout_top.addWidget(self.N_cbx)
        _buttons_layout_top.addSpacerItem(HorizontalSpacerItem())
        _buttons_layout_top.addWidget(self.save_btn)

        buttons_widget_top.setLayout(_buttons_layout_top)
        _layout.addWidget(buttons_widget_top)
        params = "Ultrasound echo analysis", 'Amplitude', 'Time'
        win = customWidget(params)
        _layout.addWidget(win)

        detail1 = "Ultrasound echo 1", 'Amplitude', 'Time'
        detail_win1 = customWidget(detail1)
        detail2 = "Ultrasound echo 2", 'Amplitude', 'Time'
        detail_win2 = customWidget(detail2)
        _detail_layout.addWidget(detail_win1)
        _detail_layout.addWidget(detail_win2)
        detail_widget.setLayout(_detail_layout)
        _layout.addWidget(detail_widget)
        calc_btn = QtWidgets.QPushButton('Correlate')
        #_buttons_layout_bottom.addWidget(calc_btn)
        #_buttons_layout_bottom.addWidget(QtWidgets.QLabel('2-way travel time:'))
        output_ebx = QtWidgets.QLineEdit('')
        #_buttons_layout_bottom.addWidget(output_ebx)
        _buttons_layout_bottom.addSpacerItem(HorizontalSpacerItem())
        buttons_widget_bottom.setLayout(_buttons_layout_bottom)
        _layout.addWidget(buttons_widget_bottom)
        my_widget.setLayout(_layout)
        return my_widget, win, detail_win1, detail_win2, open_btn, calc_btn, output_ebx, fname_lbl

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
 
 
    def create_menu(self):

        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 793, 22))
        self.file_menu = self.menuBar.addMenu('File')
        self.file_save_hdf5_act = QtWidgets.QAction('Save to HDF5', self)    
        self.actionSave_next = QtWidgets.QAction("Save", self)
        self.actionSave_As = QtWidgets.QAction("Save as...", self)
        self.actionPreferences = QtWidgets.QAction("Preferences", self)
        self.actionBG = QtWidgets.QAction("Overlay", self)
        self.actionBGclose = QtWidgets.QAction("Close overlay", self)
        self.actionCursors = QtWidgets.QAction("Phase", self)
        self.actionArrowPlot = QtWidgets.QAction("Arrow Plot", self)
        self.file_menu.addAction(self.actionSave_As)    
        self.file_menu.addAction(self.actionPreferences)  
        self.file_menu.addAction(self.actionBG) 
        self.file_menu.addAction(self.actionCursors) 
        self.file_menu.addAction(self.actionArrowPlot) 
        self.opts_menu = self.menuBar.addMenu('Arb')
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




