# -*- coding: utf8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" 
    Ross Hrubiak


"""

from functools import partial
from numpy import argmax, nan
from PyQt5 import QtWidgets, QtCore
import copy
import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor
from widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight, HorizontalLine
from widgets.PltWidget import CustomViewBox, PltWidget



class PopUpWidget(QtWidgets.QWidget):
    widget_closed = QtCore.pyqtSignal()
    
    def __init__(self, title=''):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout()  
        self.setWindowTitle(title)
        self.button_widget = QtWidgets.QWidget(self)
        self._button_layout = QtWidgets.QHBoxLayout()
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        self._button_layout.setSpacing(15)

        self.button_widget.setLayout(self._button_layout)
        self._layout.addWidget(self.button_widget)
        self._body_layout = QtWidgets.QHBoxLayout()
        self._layout.addWidget(HorizontalLine())
        self._layout.addLayout(self._body_layout)
        
        self.button_2_widget = QtWidgets.QWidget(self)
        self.button_2_widget.setObjectName('waveform_control_button_2_widget')
        self._button_2_layout = QtWidgets.QHBoxLayout()
        self._button_2_layout.setContentsMargins(0, 0, 0, 0)
        self._button_2_layout.setSpacing(6)
        self.button_2_widget.setLayout(self._button_2_layout)
        self._layout.addWidget(HorizontalLine())
        self._layout.addWidget(self.button_2_widget)
        self.setLayout(self._layout)
        self.style_widgets()

    def add_top_row_button(self, objectName, text):
        setattr(self, objectName, FlatButton(text))

        self._button_layout.addWidget(getattr(self,objectName))

    def add_bottom_row_button(self, objectName, text):
        setattr(self, objectName, FlatButton(text))
        self._button_2_layout.addWidget(getattr(self,objectName))
    
    def add_top_horizontal_spacer(self):
        self._button_layout.addSpacerItem(HorizontalSpacerItem())

    def add_bottom_horizontal_spacer(self):
        self._button_2_layout.addSpacerItem(HorizontalSpacerItem())
        
        
    def add_body_widget(self, widget):
        
        self._body_layout.addSpacerItem(VerticalSpacerItem())

    def style_widgets(self):
        
        self.setStyleSheet("""
            #rois_control_button_widget FlatButton {
                max-width: 70;
                min-width: 70;
            }
            #rois_control_button_2_widget FlatButton {
                max-width: 70;
                min-width: 70;
            }
        """)


    
    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.widget_closed.emit()
        
  


    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()


    
class plotWaveWindow(QtWidgets.QWidget):
    widget_closed = QtCore.Signal()
    def __init__(self):
        super().__init__()

        self._layout = QtWidgets.QVBoxLayout()  
        self._layout.setContentsMargins(0,0,0,0)
        self.setWindowTitle('E cut view')
        self.fitPlots = PltWidget(self)
        self.fitPlots.setLogMode(False,False)
        self.fitPlots.setMenuEnabled(enableMenu=False)
        self.viewBox = self.fitPlots.getViewBox() # Get the ViewBox of the widget
        self.viewBox.setMouseMode(self.viewBox.RectMode)
        self.viewBox.enableAutoRange(0, False)
        
        self.fitPlot = self.fitPlots.plot([],[], 
                        pen=(155,155,155), name="Fit", 
                        antialias=True)
        self.fitPlot2 = self.fitPlots.plot([],[], 
                        pen=(100,100,255), name="Fit", 
                        antialias=True, width=2)
        self.dataPlot = self.fitPlots.plot([],[], 
                        pen = None, symbolBrush=(255,0,0), 
                        symbolPen='k', name="Data",antialias=True)
        self.vLineRight = pg.InfiniteLine(angle=90, movable=True,pen=mkPen({'color': mkColor(0,180,180,120), 'width': 2}))
        self.vLineLeft = pg.InfiniteLine(angle=90, movable=True,pen=mkPen({'color': mkColor(0,180,180,120), 'width': 2}))
        self.vLineRight.setPos(nan)
        self.vLineLeft.setPos(nan)
        self.viewBox.addItem(self.vLineRight, ignoreBounds=True)
        self.viewBox.addItem(self.vLineLeft, ignoreBounds=True)
        #self.fitPlots.setLabel('left','counts')
        #self.fitPlots.setLabel('bottom', 'channel')

        self._layout.addWidget(self.fitPlots)
        self.setLayout(self._layout)
        self.resize(800,500)

    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.widget_closed.emit()

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()

    def set_data(self,x_fit=[],y_fit=[],label='',x=[],y=[], x1=[],y1=[],unit='',unit_='', r = None, roi_range=None):
        self.fitPlot.setData(x_fit,y_fit) 
        self.fitPlots.setTitle(label)
        self.dataPlot.setData(x,y)
        self.fitPlot2.setData(x1,y1)
        self.fitPlots.setLabel('bottom', unit+' ('+unit_+')')
        #self.fitPlots.getViewBox().enableAutoRange()
        if r != None:
            self.viewBox.enableAutoRange(0, False)
            self.viewBox.enableAutoRange(1, False)
            self.viewBox.setXRange(r[0][0], r[0][1], padding=0)
            self.viewBox.setYRange(r[1][0], r[1][1], padding=0)
        if roi_range != None:
            self.vLineRight.setPos(roi_range[0])
            self.vLineLeft.setPos(roi_range[1])
    

        
class ArbEditWidget(PopUpWidget):
    def __init__(self):
        super().__init__(title='Waveform control')
        self.add_top_row_button('plot_btn','Plot')
        self.add_top_horizontal_spacer()
        self.add_bottom_row_button('apply_btn','Apply')
        self.add_bottom_horizontal_spacer()
        self.add_body_widget(VerticalSpacerItem())
        
class ArbEditFilterWidget(PopUpWidget):
    def __init__(self):
        super().__init__(title='Filter control')
        self.plot_window = plotWaveWindow()
        self.add_top_row_button('plot_btn','Plot')
        self.add_top_horizontal_spacer()
        self.add_bottom_row_button('apply_btn','Apply')
        self.add_bottom_horizontal_spacer()
        self.add_body_widget(VerticalSpacerItem())
        self.make_connections()

    def make_connections(self):
        self.plot_btn.clicked.connect(self.plot_window.raise_widget)