import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from um.widgets.PltWidget import SimpleDisplayWidget
import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
import numpy as np

class WaterfallWidget(QtWidgets.QWidget):
    panelClosedSignal = pyqtSignal()
    def __init__(self, ctrls = [],params=["Waterfall plot", 'Scan point', 'Time']):
        super().__init__()
        
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(5, 0, 5, 0)
        
        self.plot_widget = SimpleDisplayWidget(params)
        
        self.button_widget = QtWidgets.QWidget()
        
        self._button_layout = QtWidgets.QHBoxLayout()
        self._button_layout.setSpacing(10)
        self._button_layout.setContentsMargins(0, 5, 0, 5)
      
        self._status_layout = QtWidgets.QVBoxLayout()

        self.button_widget.setLayout(self._button_layout)

        self._layout.addWidget(self.button_widget)
        
        self._layout.addWidget(self.plot_widget)

        self.setLayout(self._layout)

        fig = self.plot_widget.fig.win 
        
        fig.create_plots([],[],[],[],'Time')
        fig.set_colors({'rois_color': '#7AE7FF'})
        self._CH1_plot = fig.plotForeground
        self._plot_selected = fig.plotRoi
      

        self.setStyleSheet("""
            #FlatButton {
                min-width: 120;
            }
            #pvQPushButton {
                min-width: 120;
            }
            
        """)

    def add_buttons(self, buttons):
        self.scope_controls = buttons
        for ctrl in self.scope_controls:
            if type(ctrl)== str:
                self._button_layout.addSpacerItem(HorizontalSpacerItem())
            else:
                self._button_layout.addWidget(ctrl)

    def plot(self, x,y,sel_x=[],sel_y=[],echoes_p_x=[],echoes_p_y=[],echoes_s_x=[],echoes_s_y=[], xLabel='Time', dataLabel=''):
        fig = self.plot_widget.fig.win 
        fig.plotData(x,y,sel_x,sel_y, echoes_p_x,echoes_p_y, echoes_s_x,echoes_s_y, xLabel, dataLabel)

    def clear_plot(self,):
        self.plot([],[])

    def set_selected_name (self, text):
        self. plot_widget.setText(text , 1)

    def set_name (self, text):
        self. plot_widget.setText(text , 0)

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        #self.raise_()  



