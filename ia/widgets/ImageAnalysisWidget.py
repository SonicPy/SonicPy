#!/usr/bin/env python


import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt

import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from pyqtgraph.functions import pseudoScatter
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
import numpy as np

from um.widgets.PltWidget import SimpleDisplayWidget, customWidget
from functools import partial

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

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

        self.resize(1600, 1000)
        
        self.make_widget()


        self.setCentralWidget(self.my_widget)

        self.create_plots()
        self.create_menu()
        self.style_widgets()

    def create_plots(self):

        self.make_roi()
        self.make_edge_roi(self.plots[6])



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

        self.plot_grid = pg.GraphicsLayoutWidget(self.my_widget)
        self.plot_grid.setBackground((255,255,255))
        #self._plot_grid_layout = QtWidgets.QGridLayout(self.plot_grid)

        plots_labels = {'src':'img','roi absorbance':'img','roi sobel vertical mean':'plot',
                        'sobel vertical mean':'plot', 'roi canny':'img', 'roi background':'img', 
                        'frame cropped':'img','roi sobel y':'img','roi vertical mean':'plot',
                        'absorbance':'img', 'sobel y': 'img', 'base_surface':'img'}
        self.imgs = []
        
        self.plots = []
        col = 0
        for plot_label in plots_labels:
            
            if col >3:
                col = 0
                self.plot_grid.nextRow()

            plot_type = plots_labels[plot_label]
            if plot_type == 'img':
                plt = self.plot_grid.addPlot(title=plot_label)
                view = plt.getViewBox()
                #view.setAspectLocked(True)
                img = pg.ImageItem()
                plt.addItem(img)
                self.imgs.append(img)
                self.plots.append(plt)
            elif plot_type == 'plot':
                plt = self.plot_grid.addPlot(title=plot_label)
                
                self.imgs.append(None)
                self.plots.append(plt)
            col = col + 1
            


        self._layout.addWidget(self.plot_grid)
        
        calc_btn = QtWidgets.QPushButton('Correlate')
        #_buttons_layout_bottom.addWidget(calc_btn)
        #_buttons_layout_bottom.addWidget(QtWidgets.QLabel('2-way travel time:'))
        output_ebx = QtWidgets.QLineEdit('')
        #_buttons_layout_bottom.addWidget(output_ebx)
        self._buttons_layout_bottom.addSpacerItem(HorizontalSpacerItem())
        self.buttons_widget_bottom.setLayout(self._buttons_layout_bottom)
        self._layout.addWidget(self.buttons_widget_bottom)
        self.my_widget.setLayout(self._layout)

    

    def make_roi(self):
        # Custom ROI for selecting an image region
        self.crop_roi = pg.ROI([50, 200], [150, 100])
        self.crop_roi.addScaleHandle([0, 1], [1, 0])
        self.crop_roi.addScaleHandle([1, 0], [0, 1])
        self.crop_roi.setZValue(10)  # make sure ROI is drawn above image
        self.plots[0].addItem(self.crop_roi)

    def make_edge_roi(self, plot):
        # Custom ROI for selecting an image region
        self.edge_roi_1 = pg.ROI([5, 100], [100, 100])
        self.edge_roi_1.addScaleHandle([0, 1], [1, 0])
        self.edge_roi_1.addScaleHandle([1, 0], [0, 1])
        self.edge_roi_1.setZValue(10)  # make sure ROI is drawn above image
        plot.addItem(self.edge_roi_1)

        # Custom ROI for selecting an image region
        self.edge_roi_2 = pg.ROI([5, 800], [100, 100])
        self.edge_roi_2.addScaleHandle([0, 1], [1, 0])
        self.edge_roi_2.addScaleHandle([1, 0], [0, 1])
        self.edge_roi_2.setZValue(10)  # make sure ROI is drawn above image
        plot.addItem(self.edge_roi_2)


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




