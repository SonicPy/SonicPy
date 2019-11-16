#!/usr/bin/env python

# 
# TODO :
import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from widgets.PltWidget import SimpleDisplayWidget
import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
import numpy as np
from widgets.panel import Panel
import time

class UltrasoundWidget(QMainWindow):
    
    preferences_signal = pyqtSignal()
    up_down_signal = pyqtSignal(str)
    panelClosedSignal = pyqtSignal()

    def __init__(self,app,_platform,Theme):
        super().__init__()
        self.setWindowTitle('sonicPy')
        self.Theme = Theme
        self.app = app  # app object
        self.resize(1250, 700)
        self.centralwidget = QtWidgets.QWidget()
        self._layout = QtWidgets.QHBoxLayout()
        self.controls_sidebar = QtWidgets.QWidget()
        self.controls_sidebar.setObjectName('controls_sidebar')
        self.controls_layout = QtWidgets.QVBoxLayout()
        self.controls_layout.setContentsMargins(1, 1, 1, 1)
        self.controls_layout.setSpacing(15)


        self.controls_grid_layout= QtWidgets.QGridLayout()
        self.grid_rows = 0

        self.controls_layout.addLayout(self.controls_grid_layout)


        self.control_panels = []
        
        self.controls_vertical_spacer = VerticalSpacerItem()
        self.controls_layout.addSpacerItem(self.controls_vertical_spacer)
        self.controls_sidebar.setLayout(self.controls_layout)
        self._layout.addWidget(self.controls_sidebar)
        self.DisplayLayout = QtWidgets.QVBoxLayout()
        self.DisplayLayout.setContentsMargins(0, 0, 0, 0)
        self.scope_waveform_layout = QtWidgets.QVBoxLayout()
        self.DisplayLayout.addLayout(self.scope_waveform_layout)
        '''
        US1_fig_parameters = 'Signal Full', 'Voltage','Time'
        self.US1 = SimpleDisplayWidget(US1_fig_parameters)
        win = self.US1.fig
        win.win.setLabel('bottom', units='s')
        win.win.setLabel('left', units='V')
        win.setPlotMouseMode(0)
        self.US1.setMaximumHeight(200)
        self.US1.setMinimumHeight(200)
        self.DisplayLayout.addWidget(self.US1)
        self.us1_plot =None
        '''

        self.detail_plots_layout = QtWidgets.QHBoxLayout()
        self.detail_plots_layout.setContentsMargins(0,0,0,0)
        self.detail_plots_layout.setSpacing(10)

        

        '''
        US3_fig_parameters = 'Signal Detail', 'Voltage','Time'
        self.US3 = SimpleDisplayWidget(US3_fig_parameters)
        self.US3.enable_cursors()
        win3 = self.US3.fig
        win3.win.setLabel('bottom', units='s')
        win3.win.setLabel('left', units='V')
        win3.setPlotMouseMode(0)
        self.US3.setMinimumHeight(200)
        self.detail_plots_layout.addWidget(self.US3)
        self.us3_plot =None
        '''

        self.DisplayLayout.addLayout(self.detail_plots_layout)
        #self.DisplayLayout.addSpacerItem(VerticalSpacerItem())
        self._layout.addLayout(self.DisplayLayout)
        self.centralwidget.setLayout(self._layout)
        self.setCentralWidget(self.centralwidget)
        self.create_menu()
        #self.create_status_bar()
        self.style_widgets()

    def closeEvent(self, QCloseEvent, *event):
        self.panelClosedSignal.emit()
        time.sleep(0.2)

    def insert_panel(self, panel):
        
        self.control_panels.append(panel)
        self.controls_grid_layout.addWidget(panel,self.grid_rows,0)
        self.grid_rows +=1
        
    

    def make_panel(self, title, panel_items, tasks):
        d = []
        for tag in panel_items:
            if tag in tasks:
                t = tasks[tag]
                t['tag']= tag
                d.append(t)
        return Panel(title, d)

    def keyPressEvent(self, e):
        event = None
        if e.key() == Qt.Key_Up:
            event = 'up'
        if e.key() == Qt.Key_Down:
            event = 'down'
        if event is not None:
            self.up_down_signal.emit(event)

    def create_status_bar(self):
        #sb = self.statusBar()
        self.AcqButtonLayout = QtWidgets.QHBoxLayout()
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setFixedHeight(15)
        self.pb_widget = QtWidgets.QWidget()
        self._pb_widget_layout = QtWidgets.QHBoxLayout()
        self._pb_widget_layout.addLayout(self.AcqButtonLayout)
        self._pb_widget_layout.addWidget(self.progress_bar)
        self._pb_widget_layout.setContentsMargins(0,0,0,0)
        self.pb_widget.setLayout(self._pb_widget_layout)
        self.DisplayLayout.addWidget(self.pb_widget)
        #sb.addWidget(self.pb_widget)

    

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
 

    def plot_waveform(self, x, y, text=''):
        if self.us1_plot is None:
            self.create_plots(x,y)
        else:
            self.us1_plot.setData(x,y)
            self.US1.setText(text,0)

            self.us2_plot.setData(x,y)
            #self.us3_plot.setData(x,y)

            #self.US2.refresh_cursor_optimum()
            #self.US3.refresh_cursor_optimum()


            

    def create_plots(self, x, y):
        fig = self.US1.fig
        #vr = fig.win.viewBox.viewRange()

        self.us1_plot = fig.add_line_plot(x,y,color=(0,255,255))
        
        xmin = min(x)
        r = (max(x)-min(x))

        rmin = min(x)+r*0.3
        rmax = rmin + r*0.07
        self.lr = pg.LinearRegionItem([rmin,rmax])
        self.lr.setZValue(-10)
        fig.win.addItem(self.lr)

        '''
        rmin2 = min(x)+r*0.6
        rmax2 = rmin2 + r*0.07
        self.lr2 = pg.LinearRegionItem([rmin2,rmax2])
        self.lr2.setZValue(-10)
        fig.win.addItem(self.lr2)
        '''

        fig2 = self.US2.fig
        self.us2_plot = fig2.add_line_plot(x,y, color=(0,255,255),Width = 1)
        self.lr.sigRegionChanged.connect(self.updatePlot2)
        fig2.win.sigXRangeChanged.connect(self.updateRegion2)
        self.updatePlot2()

        '''

        fig3 = self.US3.fig
        self.us3_plot = fig3.add_line_plot(x,y, color=(0,255,255),Width = 1)
        self.lr2.sigRegionChanged.connect(self.updatePlot3)
        fig3.win.sigXRangeChanged.connect(self.updateRegion3)
        self.updatePlot3()
        '''
    

    def updatePlot2(self):
        win2 = self.US2.fig
        win2.win.setXRange(*self.lr.getRegion(), padding=0)

    '''
    def updatePlot3(self):
        win3 = self.US3.fig
        win3.win.setXRange(*self.lr2.getRegion(), padding=0)

    '''

    def updateRegion2(self):
        self.lr.setRegion(self.us2_plot.getViewBox().viewRange()[0])


    '''
    def updateRegion3(self):
        self.lr2.setRegion(self.us3_plot.getViewBox().viewRange()[0])    
    '''
    def create_menu(self):

        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 793, 22))

        self.file_menu = self.menuBar.addMenu('File')

             
        self.file_save_hdf5_act = QtWidgets.QAction('Save to HDF5', self)    
        self.actionSave_next = QtWidgets.QAction("Save", self)
        #self.actionSave_next.setEnabled(False)
        self.actionSave_As = QtWidgets.QAction("Save as...", self)
        #self.actionSave_As.setEnabled(False)
        self.actionPreferences = QtWidgets.QAction("Preferences", self)

        self.actionBG = QtWidgets.QAction("Overlay", self)
        self.actionBGclose = QtWidgets.QAction("Close overlay", self)
        
        #self.file_menu.addAction(self.actionSave_next)
        self.file_menu.addAction(self.actionSave_As)    
        self.file_menu.addAction(self.actionPreferences)  
        self.file_menu.addAction(self.actionBG) 
        #self.file_menu.addAction(self.actionBGclose) 
        
        #self.file_menu.addAction(self.file_save_hdf5_act)

        '''
        self.file_exp_menu = QtWidgets.QMenu('Export', self)
        self.file_exp_data_act = QtWidgets.QAction('I(q)', self) 
        self.file_exp_menu.addAction(self.file_exp_data_act)
        self.file_exp_sf_act = QtWidgets.QAction('S(q)', self) 
        self.file_exp_menu.addAction(self.file_exp_sf_act)
        self.file_exp_pdf_act = QtWidgets.QAction('G(r)', self) 
        self.file_exp_menu.addAction(self.file_exp_pdf_act)
        self.file_exp_sf_inv_act = QtWidgets.QAction('Inverse Fourier-filtered S(q)', self) 
        self.file_exp_menu.addAction(self.file_exp_sf_inv_act)
        self.file_menu.addMenu(self.file_exp_menu)
        
        '''

        
        self.opts_menu = self.menuBar.addMenu('Arb')
        self.ActionRecallSetup = QtWidgets.QAction('Recall setup', self)        
        self.ActionSaveSetup = QtWidgets.QAction('Save setup', self)   
        self.ActionSetUserWaveform = QtWidgets.QAction('Edit user waveform', self)   
        #self.opts_menu.addAction(self.ActionRecallSetup)
        #self.opts_menu.addAction(self.ActionSaveSetup)
        self.opts_menu.addAction(self.ActionSetUserWaveform)
        '''

        self.tools_menu = self.menuBar.addMenu('Tools')
        self.tools_peaks_act = QtWidgets.QAction('Peak cutting', self)        
        self.tools_menu.addAction(self.tools_peaks_act)
        '''
        self.setMenuBar(self.menuBar)

    def preferences_module(self):
        self.preferences_signal.emit()

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        #self.raise_()  




