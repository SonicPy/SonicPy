#!/usr/bin/env python


import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage, QWidget
from PyQt5.QtCore import QObject, pyqtSignal, Qt

import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
#from pyqtgraph.Qt import qWait
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton, DoubleSpinBoxAlignRight
import numpy as np

from um.widgets.PltWidget import SimpleDisplayWidget
from functools import partial

class UltrasoundAnalysisWidget(QWidget):
    
    preferences_signal = pyqtSignal()
    up_down_signal = pyqtSignal(str)
    panelClosedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initialized = False
        self.t = None
        self.spectrum = None


        self.setWindowTitle('Ultrasound Analysis')

        
        self.make_widget()


        self.create_plots()
    
 

    def create_plots(self):

        
        self.plot_win = self.plot_widget.fig.win 
        self.plot_win.create_plots([],[],[],[],'Time')
        self.plot_win.set_colors( { 
                        'data_color': '#7AE7FF',\
                        'rois_color': '#FF6977', \
                        })
        self._CH1_plot = self.plot_win.plotForeground
        self.plot_demodulated = self.plot_win.plotRoi


        self.main_plot = self.plot_win.plotForeground

        self.plot_win_detail0 = self.detail_win0.fig.win
        self.plot_win_detail1 = self.detail_win1.fig.win
        self.plot_win_detail2 = self.detail_win2.fig.win

        detail_plot0 = self.detail_win0.fig.win
        detail_plot0.create_plots([],[],[],[],'Time')
        detail_plot0.set_colors( { 
                        'data_color': (0,200,255),\
                        'rois_color': (255,0,100), \
                        })
        self.detail_plot0 = detail_plot0.plotForeground
        self.detail_plot0_bg = detail_plot0.plotRoi
        self.detail_win0.setText('Echo 1' , 0)
        self.detail_win0.setText('Echo 2' , 1)

        detail_plot1 = self.detail_win1.fig.win
        detail_plot1.create_plots([],[],[],[],'Time')
        detail_plot1.set_colors( { 
                        'data_color': (0,200,255),\
                        'rois_color': (255,0,100), \
                        })
        self.detail_plot1 = detail_plot1.plotForeground
        self.detail_plot1_bg = detail_plot1.plotRoi
        self.detail_win1.setText('Echo 1' , 0)
        self.detail_win1.setText('Echo 2' , 1)

        detail_plot2 = self.detail_win2.fig.win
        detail_plot2.create_plots([],[],[],[],'Time')
        detail_plot2.set_colors( { 
                        'data_color': (0,255,100),\
                        })
        self.detail_plot2 = detail_plot2.plotForeground
        self.detail_plot2_bg = pg.PlotDataItem([], [], title="",
                        antialias=True, pen=None, symbolBrush=(0,255,100,150), symbolPen=None)
        self.plot_win_detail2.addItem(self.detail_plot2_bg)
        self.detail_win2.setText('Correlation' , 0)
        
        

        self.lr1_p = pg.LinearRegionItem()
        self.lr1_p.setZValue(-10)
        self.lr2_p = pg.LinearRegionItem()
        self.lr2_p.setZValue(-10)

        self.lr1_s = pg.LinearRegionItem()
        self.lr1_s.setZValue(-10)
        self.lr2_s = pg.LinearRegionItem()
        self.lr2_s.setZValue(-10)

        

        self.echo_bounds_p = [self.lr1_p, self.lr2_p]
        self.plot_win.addItem(self.lr1_p)
        self.plot_win.addItem(self.lr2_p) 
        self.lr1_p.setRegion([0, 0])
        self.lr2_p.setRegion([0, 0])

        self.echo_bounds_s = [self.lr1_s, self.lr2_s]
        self.lr1_s.setRegion([0, 0])
        self.lr2_s.setRegion([0, 0])

    def get_echo_bounds_p(self, i):
        return self.echo_bounds_p[i].getRegion()

    def get_echo_bounds_s(self, i):
        return self.echo_bounds_s[i].getRegion()

    def update_view(self, t, spectrum, fname):
        
        self.t, self.spectrum, self.fname = t, spectrum, fname
        if t is not None and spectrum is not None:
            self.main_plot.setData(self.t, self.spectrum)

    def update_demodulated(self, t, spectrum):
        
        if t is not None and spectrum is not None:
            self.plot_demodulated.setData(t, spectrum)

    def updatePlot1(self):
        self.lr1_pr = self.lr1_p.getRegion()
        self.plot_win_detail1.setXRange(*self.lr1_pr, padding=0)

    def updateRegion1(self):
        self.lr1_p.setRegion(self.detail_plot1.getViewBox().viewRange()[0])
        
    def updatePlot2(self):
        self.lr2_pr = self.lr2_p.getRegion()
        self.plot_win_detail2.setXRange(*self.lr2_pr, padding=0)

    def updateRegion2(self):
        self.lr2_p.setRegion(self.detail_plot2.getViewBox().viewRange()[0])


    def make_widget(self):
        
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.detail_widget = QtWidgets.QTabWidget()
        
        '''self._detail_layout = QtWidgets.QTabWidget()
        self._detail_layout.setContentsMargins(0, 0, 0, 0)'''
        self.buttons_widget_top = QWidget()
        self._buttons_layout_top = QtWidgets.QHBoxLayout()
        self._buttons_layout_top.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget_bottom = QWidget()
        self._buttons_layout_bottom = QtWidgets.QHBoxLayout()
        self._buttons_layout_bottom.setContentsMargins(0, 0, 0, 0)
        self.open_btn = QtWidgets.QPushButton("Open")
        self.fname_lbl = QtWidgets.QLineEdit('')
        self.freq_lbl = QtWidgets.QLabel(' 𝑓')
        self.freq_ebx = DoubleSpinBoxAlignRight()
        self.freq_ebx.setMaximum(100)
        self.freq_ebx.setMinimum(1)
        self.freq_ebx.setValue(21)
        self.N_cbx = QtWidgets.QCheckBox('+/-')
        self.N_cbx.setChecked(True)
        self.save_btn = QtWidgets.QPushButton('Save')
        self.arrow_plt_btn = QtWidgets.QPushButton(u'Inverse 𝑓')

        self.echo1_cursor_btn = QtWidgets.QPushButton('Echo 1')
        self.echo2_cursor_btn = QtWidgets.QPushButton('Echo 2')

        
        
        self._buttons_layout_top.addWidget(self.open_btn)
        #self._buttons_layout_top.addWidget(self.fname_lbl)
        self._buttons_layout_top.addWidget(self.freq_lbl)
        self._buttons_layout_top.addWidget(self.freq_ebx)

        self._buttons_layout_top.addWidget(self.echo1_cursor_btn)
        self._buttons_layout_top.addWidget(self.echo2_cursor_btn)
        #self._buttons_layout_top.addWidget(self.N_cbx)

        self.p_s_widget = QWidget(self.buttons_widget_top)
        self._p_s_widget_layout = QtWidgets.QHBoxLayout(self.p_s_widget)
        self._p_s_widget_layout.setContentsMargins(0,0,0,0)
        self._p_s_widget_layout.setSpacing(0)
        self.p_wave_btn = QtWidgets.QPushButton('P')
        self.p_wave_btn.setObjectName('p_wave_btn')
        self.p_wave_btn.setCheckable(True)
        self.s_wave_btn = QtWidgets.QPushButton('S')
        self.s_wave_btn.setObjectName('s_wave_btn')
        self.s_wave_btn.setCheckable(True)
        self._p_s_widget_layout.addWidget(self.p_wave_btn)
        self._p_s_widget_layout.addWidget(self.s_wave_btn)
        self.p_s_widget.setLayout(self._p_s_widget_layout)
        self.wave_btn_group = QtWidgets.QButtonGroup()
        self.wave_btn_group.addButton(self.p_wave_btn)
        self.wave_btn_group.addButton(self.s_wave_btn)
        self.p_wave_btn.setChecked(True)
        self._buttons_layout_top.addWidget(self.p_s_widget)
  
        self._buttons_layout_top.addWidget(self.save_btn)
        self._buttons_layout_top.addSpacerItem(HorizontalSpacerItem())
        #self._buttons_layout_top.addWidget(self.arrow_plt_btn)

        self.buttons_widget_top.setLayout(self._buttons_layout_top)
        self._layout.addWidget(self.buttons_widget_top)
        params = "Ultrasound echo analysis", 'Amplitude', 'Time'

        self.splitter_vertical = QtWidgets.QSplitter(Qt.Vertical)


        self.plot_widget = SimpleDisplayWidget(params)
        self.splitter_vertical.addWidget(self.plot_widget)

        self.detail0 = "Selected echoes", 'Amplitude', 'Time'
        self.detail_win0 = SimpleDisplayWidget(self.detail0)
        self.detail1 = "Filtered echoes", 'Amplitude', 'Time'
        self.detail_win1 = SimpleDisplayWidget(self.detail1)
        self.detail2 = "Correlation", 'Amplitude', 'Time'
        self.detail_win2 = SimpleDisplayWidget(self.detail2)

        self.detail_widget.addTab(self.detail_win0, 'Selected')
        self.detail_widget.addTab(self.detail_win1, 'Filtered')
        self.detail_widget.addTab(self.detail_win2, 'Correlation')

        #self.detail_widget.setLayout(self._detail_layout)
        self._detail_widget = QtWidgets.QWidget()
        self._detail_widget_layout = QtWidgets.QVBoxLayout(self._detail_widget)
        self._detail_widget_layout.setContentsMargins(0,15,0,0)
        self._detail_widget_layout.addWidget(self. detail_widget)
        self.splitter_vertical.addWidget(self._detail_widget)

        self._layout.addWidget(self.splitter_vertical)

        #self.calc_btn = QtWidgets.QPushButton('Correlate')
        #_buttons_layout_bottom.addWidget(calc_btn)
        #_buttons_layout_bottom.addWidget(QtWidgets.QLabel('2-way travel time:'))
        #self.output_ebx = QtWidgets.QLineEdit('')
        #_buttons_layout_bottom.addWidget(output_ebx)
        #self._buttons_layout_bottom.addSpacerItem(HorizontalSpacerItem())
        #self.buttons_widget_bottom.setLayout(self._buttons_layout_bottom)
        #self._layout.addWidget(self.buttons_widget_bottom)
        self.setLayout(self._layout)
        



