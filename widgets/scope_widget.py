import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from widgets.PltWidget import SimpleDisplayWidget, customWidget
import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
import numpy as np

class scopeWidget(QtWidgets.QWidget):
    panelClosedSignal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout()
        params = "plot title", 'Amplitude', 'Time'
        self.plot_widget = customWidget(params)
        #self.plot_widget.enable_cursors()

        
        self.button_widget = QtWidgets.QWidget()
        
        self._button_layout = QtWidgets.QHBoxLayout()
        self.start_stop_btn = QtWidgets.QPushButton("On")
        self.start_stop_btn.setCheckable(True)

        self.erase_btn = QtWidgets.QPushButton("Erase")
        self.save_btn = QtWidgets.QPushButton("Save")
        #self.save_btn.setDisabled(True)
        
        self._status_layout = QtWidgets.QVBoxLayout()

        self.status_lbl = QtWidgets.QLabel(' ')
        self._status_layout.addWidget(self.status_lbl)
        
        self._button_layout.addWidget(self.erase_btn)
        self._button_layout.addWidget(self.start_stop_btn)
        
        self._button_layout.addLayout(self._status_layout)
        
        self._button_layout.addSpacerItem(HorizontalSpacerItem())
        self._button_layout.addWidget(self.save_btn)
       
        self.button_widget.setLayout(self._button_layout)

        self._layout.addWidget(self.button_widget)
        
        self._layout.addWidget(self.plot_widget)

        self.setLayout(self._layout)

        fig = self.plot_widget.fig 
        self.CH1_plot = fig.add_line_plot([],[],color=(255,255,0))
        self.bg_plot = fig.add_line_plot([],[],color=(0,255,255))
        self.bg_plot_filtered = fig.add_line_plot([],[],color=(255,0,255))

    def plot(self,waveform):
        
        
        plot = self.CH1_plot
        
        if plot is not None:
            plot.setData(waveform[0], waveform[1])

    def plot_bg(self,waveform):
        
        plot = self.bg_plot
        if plot is not None:
            plot.setData(waveform[0], waveform[1])

    def plot_filtered(self, filtered):
        
        plot_filtered = self.bg_plot_filtered
        if plot_filtered is not None:
            
            plot_filtered.setData(filtered[0], filtered[1])


    def clear_plot(self,):
        
        self.CH1_plot.setData(np.asarray([]),np.asarray([]))
        self.status_lbl.setText(' ')

    def clear_plot_bg(self,):
        
        self.bg_plot.setData(np.asarray([]),np.asarray([]))
        

    

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        #self.raise_()  



