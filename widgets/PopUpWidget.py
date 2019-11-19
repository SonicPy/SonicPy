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
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight, HorizontalLine, \
        CleanLooksComboBox, NumberTextField, LabelAlignRight
from widgets.PltWidget import CustomViewBox, PltWidget


class AfwGroupbox(QtWidgets.QWidget):
    param_edited_signal = QtCore.pyqtSignal(dict)
    panel_selection_edited_signal = QtCore.pyqtSignal(str)
    def __init__(self, title):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.awf_type_cb = CleanLooksComboBox()    
        self._layout.addWidget(self.awf_type_cb)
        self._awf_type_info_btn = QtWidgets.QPushButton('i')
        self.panels = {}
        self.selected_panel = None
        self.panel = QtWidgets.QWidget()
        self._panel_layout = QtWidgets.QVBoxLayout()
        self._panel_layout.setContentsMargins(0, 0, 0, 0)
        self.panel.setLayout(self._panel_layout)
        self._layout.addWidget(self.panel)
        self.setLayout(self._layout)
        self.awf_type_cb.currentTextChanged.connect(self.awf_type_edited)

    def add_panel(self, name, panel):
        self.panels[name] = panel
        self.awf_type_cb.addItem(name)

    def select_panel(self, name):
        if self.selected_panel is not None:
            self._panel_layout.removeWidget(self.selected_panel)
            self.selected_panel.setParent(None)
        _widget = self.panels[name]
        self.selected_panel = _widget
        self._panel_layout.addWidget(self.selected_panel)
        self.awf_type_cb.blockSignals(True)
        self.awf_type_cb.setCurrentText(name)
        self.awf_type_cb.blockSignals(False)

    def show_awf_info(self):
        QtWidgets.QMessageBox.about(None, "Description", self.get_current_awf_info() )

    def get_current_awf_info(self):
        display_name = self.awf_type_cb.currentText()
        selected_awf = self.displayName2name[display_name]
        awf_name = self.AFW_params[selected_awf]['name']
        ref = self.AFW_params[selected_awf]['reference']
        awf = self.AFW_params[selected_awf]['params']
        desc = awf_name + '<br><br>'
        for key in awf:
            param = awf[key]
            s = param['symbol'] + ': ' + param['desc'] + '<br>'
            desc = desc + s
        if ref != '':
            desc = desc +'<br>Reference:<br>' +ref 
        return desc

    def awf_type_edited(self, key):
        self.panel_selection_edited_signal.emit(key)


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

    def add_body_spacer(self):
        self._body_layout.addSpacerItem(VerticalSpacerItem())
        
    def add_body_widget(self, widget):
        self._body_layout.addWidget(widget)

    

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
        self.setWindowTitle('Waveform plot')
        self.fitPlots = PltWidget(self)
        self.fitPlots.setLogMode(False,False)
        self.fitPlots.setMenuEnabled(enableMenu=False)
        self.viewBox = self.fitPlots.getViewBox() # Get the ViewBox of the widget
        self.viewBox.setMouseMode(self.viewBox.RectMode)
        self.viewBox.enableAutoRange(True)
        
        self.fitPlot = self.fitPlots.plot([],[], 
                        pen=(0,122,122), name="Fit", 
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
    
class EditWidget(PopUpWidget):
    applyClickedSignal = QtCore.pyqtSignal(str)
    controller_selection_edited_signal = QtCore.pyqtSignal(str)
    widget_closed = QtCore.Signal()
    def __init__(self, title ):
        super().__init__(title)
        self.plot_window = plotWaveWindow()

        self.add_top_row_button('plot_btn','Plot')
        self.add_top_horizontal_spacer()
        #self.add_bottom_row_button('apply_btn','Apply')
        self.add_bottom_horizontal_spacer()
        
        self.afw_gb = AfwGroupbox(title=title)
        
        self.add_body_widget(self.afw_gb)
        
        self.make_connections()

    def add_panel(self, name, panel):
        self.afw_gb.add_panel(name, panel)

    def select_panel(self, name):
        self.afw_gb.select_panel(name)

    def set_selected_choice(self, selection):
        
        self.afw_gb.awf_type_cb.setCurrentText(selection)
    
    def panel_selection_edited_signal_callback(self, key):
        self.controller_selection_edited_signal.emit(key)

    def get_selected_choice(self):
        display_name = self.afw_gb.awf_type_cb.currentText()
        return display_name

    #def get_apply_btn(self):
    #    return getattr(self,'apply_btn')

    def make_connections(self):
        self.plot_btn.clicked.connect(self.plot_window.raise_widget)
        self.afw_gb.panel_selection_edited_signal.connect(self.panel_selection_edited_signal_callback)

    def awf_type_edited_callback(self, d):
        selection_key = d['arb_waveform']
        self.applyClickedSignal.emit(selection_key)

    def update_plot(self, data):
        self.plot_window.set_data(data[0],data[1])
        
    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.plot_window.close()
        self.widget_closed.emit()

    def hideEvent(self, event):
        self.plot_window.close()
        self.widget_closed.emit()