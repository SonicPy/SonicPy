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

from models.ArbDefinitions import arb_waveforms
from models.FilterDefinitions import filters

class AfwGroupbox(QtWidgets.QWidget):
    param_edited_signal = QtCore.pyqtSignal(dict)
    awf_type_edited_signal = QtCore.pyqtSignal(dict)
    def __init__(self, title, definitions, default):
        super().__init__()
        self.arb_waveform = default
        self._layout = QtWidgets.QVBoxLayout()
        self.awf_gb = QtWidgets.QGroupBox("Waveform settings")
        self._awf_gb_layout = QtWidgets.QVBoxLayout()
        

        self.AFW_params = definitions
        self.AFW_widgets = {}
        


        self.txt_fields = {}
        self.scales = {}
        
        self.awf_type_cb = CleanLooksComboBox()
        self.awf_info = ''
        


        self.awf_types = list(self.AFW_params.keys())
        self.awf_type_cb.addItems(self.awf_types)
        self._awf_type_cb_layout = QtWidgets.QHBoxLayout()
        self._awf_type_cb_layout.addWidget(QtWidgets.QLabel('Form:'))
        self._awf_type_cb_layout.addWidget(self.awf_type_cb)
        self._awf_type_info_btn = QtWidgets.QPushButton('i')
        self._awf_type_cb_layout.addWidget(self._awf_type_info_btn)
        self._awf_type_info_btn.clicked.connect(self.show_awf_info)

        self._awf_gb_layout.addLayout(self._awf_type_cb_layout)

        
        for key in self.AFW_params:
            awf = self.AFW_params[key]['params']
            awf_widget = QtWidgets.QWidget()
            _awf_layout = QtWidgets.QGridLayout()
            
            row = 0
            txt_fields = {}
            for param_key in awf:
                if param_key == 'V_0':
                    continue
                param = awf[param_key]
                symbol = param['symbol']
                
                desc = param['desc']
                unit = param['unit']
                if unit == "Pa":
                    unit = "GPa"
                    self.scales[param_key]=1e9

                text_field =  NumberTextField()
                text_field.setText('0')
                txt_fields[param_key]=text_field
                self.add_field(_awf_layout, text_field, symbol+':', unit, row, 0)
                text_field.returnPressed.connect(partial(self.text_field_edited_callback, {'awf':key,'param_key':param_key}))
                
                row = row + 1
            self.txt_fields[key]=txt_fields
            awf_widget.setLayout(_awf_layout)    
            self.AFW_widgets[key] = awf_widget
            awf_widget.setStyleSheet("""
                    NumberTextField {
                        min-width: 60;
                    }
                """)
        
        self.awf_widget = self.AFW_widgets[self.arb_waveform]
        self._awf_gb_layout.addWidget(self.awf_widget)

        
            
        self.awf_type_cb.setCurrentText(self.arb_waveform)
        self.awf_gb.setLayout(self._awf_gb_layout)
        self._layout.addWidget(self.awf_gb)
        self.setLayout(self._layout)
        
        self.awf_type_cb.currentTextChanged.connect(self.awf_type_edited)

    
    def show_awf_info(self):
        QtWidgets.QMessageBox.about(None, "AFW description", self.get_current_awf_info() )

    def get_current_awf_info(self):
        selected_awf = self.awf_type_cb.currentText()
        awf_name = 'AFW: ' +self.AFW_params[selected_awf]['name']
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
        
        if key in self.AFW_widgets:
            self._change_awf_layout(key)
            if key in self.txt_fields:
                '''_txt_fields = self.txt_fields[key]
                d = self.dictionarize_fields(_txt_fields)
                '''
                d = {}
                d['arb_waveform']= key
                self.awf_type_edited_signal.emit(d)

    def _change_awf_layout(self, key):
        _widget = self.AFW_widgets[key]
        self._awf_gb_layout.removeWidget(self.awf_widget)
        self.awf_widget.setParent(None)
        self.awf_widget = _widget
        self._awf_gb_layout.addWidget(self.awf_widget)
            
    def dictionarize_fields(self, fields):
        d = {}
        for key in fields:
            field = fields[key]
            val = float(str(field.text()))
            if key in self.scales:
                val = float(str(val)) * self.scales[key]     
            d[key]= val
        return d

    def text_field_edited_callback(self, awf_param_key):
        key = awf_param_key['param_key']
        awf = awf_param_key['awf']
        self.arb_waveform = awf
        val = self.txt_fields[self.arb_waveform][key].text()
        if key in self.scales:
            val = float(str(val)) * self.scales[key]
        self.param_edited_signal.emit({key:val})


    def add_field(self, layout, widget, label_str, unit, x, y):
        layout.addWidget(LabelAlignRight(label_str), x, y)
        layout.addWidget(widget, x, y + 1)
        if unit:
            layout.addWidget(QtWidgets.QLabel(unit), x, y + 2)

    def setAFWparams(self, params):
        self.blockSignals(True)
        awf = params['arb_waveform']
        if self.arb_waveform != awf:
            if awf in self.AFW_widgets:
                self.awf_type_cb.setCurrentText(awf)
                self._change_awf_layout(awf)
            self.arb_waveform = awf

        fields = self.txt_fields[self.arb_waveform]
        for key in params:
            param = params[key]
            if key in fields:
                param = params[key]
                if key in self.scales:
                    param = param / self.scales[key]
                fields[key].setText(str(param))
        self.blockSignals(False)

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
    
class EditWidget(PopUpWidget):
    def __init__(self, title, definitions, default):
        super().__init__(title)
        self.plot_window = plotWaveWindow()

        self.add_top_row_button('plot_btn','Plot')
        self.add_top_horizontal_spacer()
        self.add_bottom_row_button('apply_btn','Apply')
        self.add_bottom_horizontal_spacer()
        
        self.afw_gb = AfwGroupbox(title=title, definitions=definitions, default=default)
        self.add_body_widget(self.afw_gb)
        
        self.make_connections()

    def make_connections(self):
        self.plot_btn.clicked.connect(self.plot_window.raise_widget)
        
