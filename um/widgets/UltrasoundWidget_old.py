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

class UltrasoundWidget(QMainWindow):
    
    preferences_signal = pyqtSignal()
    up_down_signal = pyqtSignal(str)

    def __init__(self,app,_platform,Theme):
        super().__init__()
        self.setWindowTitle('sonicPy')
        self.Theme = Theme
        self.app = app  # app object
        self.resize(1236, 900)
        self.centralwidget = QtWidgets.QWidget()
        self._layout = QtWidgets.QHBoxLayout()
        self.controls_sidebar = QtWidgets.QWidget()
        self.controls_sidebar.setObjectName('controls_sidebar')
        self.controls_layout = QtWidgets.QVBoxLayout()
        self.controls_layout.setContentsMargins(1, 1, 1, 1)
        self.controls_layout.setSpacing(10)


        
        sweep_items = {   'Start (MHz)'    :['6',      True],
                          'Step (MHz)'     :['3',      True],
                          'Samples'        :['15',     True]}
        
                          
        scope_items = {   'Instrument'     :['DPO5104',False],
                          'Channel'        :['CH1',    False],
                          'Resolution'     :['100 ps', False],
                          'Accumulations'  :['4000',   True],
                          'Range (mV)'     :['100',    True]}

        
        self.control_panels = []
        
        self.controls_vertical_spacer = VerticalSpacerItem()
        self.controls_layout.addSpacerItem(self.controls_vertical_spacer)
        self.controls_sidebar.setLayout(self.controls_layout)
        self._layout.addWidget(self.controls_sidebar)
        self.DisplayLayout = QtWidgets.QVBoxLayout()
        self.DisplayLayout.setContentsMargins(0, 5, 0, 0)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMinimumHeight(180)
        self.tabWidget.setMaximumHeight(400)
        self.tab_1 = QtWidgets.QWidget()
        self._layout_tab_1 = QtWidgets.QVBoxLayout(self.tab_1)
        self._layout_tab_1.setContentsMargins(0, 1, 0, 0)
        self.tabWidget.addTab(self.tab_1, "Raw")
        self.tab_2 = QtWidgets.QWidget()
        self._layout_tab_2 = QtWidgets.QVBoxLayout(self.tab_2)
        self._layout_tab_2.setContentsMargins(0, 1, 0, 0)
        self.tabWidget.addTab(self.tab_2, "Demodulated")
        self.DisplayLayout.addWidget(self.tabWidget)
        self.win = pg.GraphicsLayoutWidget()
        self.win.setBackground(background=(20,20,20))
        self.win.setWindowTitle('Ultrasound echo view')
        # A plot area (ViewBox + axes) for displaying the image
        self.p1 = self.win.addPlot()
        self.p1.setLabel('left', text='Frequency')
        self.p1.setLabel('bottom', text='Time',units='s')
        a = self.p1.getAxis('bottom')
        a.setScale(0.2e-8)
        b = self.p1.getAxis('left')
        b.setStyle(showValues=False)
        self.img = pg.ImageItem()
        self.p1.addItem(self.img)
        self.hLine1 = pg.InfiniteLine(angle=0, movable=True,pen=mkPen({'color': '00CC00', 'width': 2}),hoverPen=mkPen({'color': '0000FF', 'width': 2}))
        self.hLine1.setPos(0)
        self.p1.addItem(self.hLine1, ignoreBounds=True)
        # Contrast/color control 
        self.hist = pg.HistogramLUTItem()
        self.gradient = self.hist.gradient
        d = {'mode': 'rgb', 'ticks':[(0.0, (19, 121, 255, 255)), 
                                    (1.0, (0, 255, 0, 255)), 
                                    (0.50, (0, 0, 0, 255))]}
        self.gradient.restoreState(d)
        self.hist.setImageItem(self.img)
        #self.hist.setLevels(-0.2, 0.2)
        self.win.addItem(self.hist)
        self.hist.setMaximumWidth(120)
        self.win.setMaximumHeight(450)
        self._layout_tab_1.addWidget(self.win)
        self.win2 = pg.GraphicsLayoutWidget()
        self.win2.setBackground(background=(20,20,20))
        self.p2 = self.win2.addPlot()
        self.p2.setLabel('left', text='Frequency')
        self.p2.setLabel('bottom', text='Time')
        self.img2 = pg.ImageItem()
        self.p2.addItem(self.img2)
        self.hLine2 = pg.InfiniteLine(angle=0, movable=True,pen=mkPen({'color': '00CC00', 'width': 2}),hoverPen=mkPen({'color': '0000FF', 'width': 2}))
        self.hLine2.setPos(0)
        self.p2.addItem(self.hLine2, ignoreBounds=True)
        # Contrast/color control
        self.hist2 = pg.HistogramLUTItem()
        self.gradient2 = self.hist2.gradient
        d2 = {'mode': 'rgb', 'ticks': [(0.0, (0, 0, 0, 255)), 
                                        (1.0, (0, 255, 255, 255))]}
        self.gradient2.restoreState(d2)
        self.hist2.setImageItem(self.img2)
        #self.hist2.setLevels(0, 0.2)
        self.win2.addItem(self.hist2)
        self.hist2.setMaximumWidth(120)
        self.win2.setMaximumHeight(450)
        self._layout_tab_2.addWidget(self.win2)

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

        self.detail_plots_layout = QtWidgets.QHBoxLayout()
        self.detail_plots_layout.setContentsMargins(0,0,0,0)
        self.detail_plots_layout.setSpacing(10)

        US2_fig_parameters = 'Signal Detail', 'Voltage','Time'
        self.US2 = SimpleDisplayWidget(US2_fig_parameters)
        self.US2.enable_cursors()
        win2 = self.US2.fig
        win2.win.setLabel('bottom', units='s')
        win2.win.setLabel('left', units='V')
        win2.setPlotMouseMode(0)
        self.US2.setMinimumHeight(200)
        self.detail_plots_layout.addWidget(self.US2)
        self.us2_plot =None

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

        self.DisplayLayout.addLayout(self.detail_plots_layout)

        self._layout.addLayout(self.DisplayLayout)
        self.centralwidget.setLayout(self._layout)
        self.setCentralWidget(self.centralwidget)
        self.make_menu_bar()
        self.create_status_bar()
        self.style_widgets()

    def insert_panel(self, panel):
        self.controls_layout.removeItem(self.controls_vertical_spacer)
        self.control_panels.append(panel)
        self.controls_layout.addWidget(panel)
        self.controls_layout.addSpacerItem(self.controls_vertical_spacer)

    

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
        self.start_btn = FlatButton("Run")
        self.stop_btn = FlatButton("Stop")
        self.apply_btn = FlatButton("Apply")
        self.AcqButtonLayout.addWidget(self.start_btn)
        self.AcqButtonLayout.addWidget(self.stop_btn)
        self.AcqButtonLayout.addWidget(self.apply_btn)
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
            FlatButton {
                min-width: 70;
                max-width: 70;
            }
            #controls_sidebar QLineEdit {
                min-width: 100;
                max-width: 100;
            }
            #controls_sidebar QLabel {
                min-width: 150;
                max-width: 150;
            }
            
        """)

    def closeEvent(self, QCloseEvent, *event):
        self.app.closeAllWindows()    

    def plot_waveform(self, x, y, text=''):
        if self.us1_plot is None:
            self.create_plots(x,y)
        else:
            self.us1_plot.setData(x,y)
            self.US1.setText(text,0)

            self.us2_plot.setData(x,y)
            self.us3_plot.setData(x,y)

            self.US2.refresh_cursor_optimum()
            self.US3.refresh_cursor_optimum()
            

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

        rmin2 = min(x)+r*0.6
        rmax2 = rmin2 + r*0.07
        self.lr2 = pg.LinearRegionItem([rmin2,rmax2])
        self.lr2.setZValue(-10)
        fig.win.addItem(self.lr2)

        fig2 = self.US2.fig
        self.us2_plot = fig2.add_line_plot(x,y, color=(0,255,255),Width = 1)
        self.lr.sigRegionChanged.connect(self.updatePlot2)
        fig2.win.sigXRangeChanged.connect(self.updateRegion2)
        self.updatePlot2()

        fig3 = self.US3.fig
        self.us3_plot = fig3.add_line_plot(x,y, color=(0,255,255),Width = 1)
        self.lr2.sigRegionChanged.connect(self.updatePlot3)
        fig3.win.sigXRangeChanged.connect(self.updateRegion3)
        self.updatePlot3()

    def update_3d_plots_raw(self, waveforms):
        data = waveforms.T
        
        self.img.setImage(data, autoLevels = False)
        self.hist.setLevels(-0.01, 0.01)
       # self.p1.autoRange()  

    def update_3d_plots_envelope(self, waveforms):
        data = waveforms.T
        
        self.img2.setImage(data, autoLevels = False)
        self.hist2.setLevels(0, 0.1)
        #self.p2.autoRange() 

    def updatePlot2(self):
        win2 = self.US2.fig
        win2.win.setXRange(*self.lr.getRegion(), padding=0)


    def updatePlot3(self):
        win3 = self.US3.fig
        win3.win.setXRange(*self.lr2.getRegion(), padding=0)

    

    def updateRegion2(self):
        self.lr.setRegion(self.us2_plot.getViewBox().viewRange()[0])

    def updateRegion3(self):
        self.lr2.setRegion(self.us3_plot.getViewBox().viewRange()[0])    

    

    def preferences_module(self):
        self.preferences_signal.emit()

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        #self.raise_()  




