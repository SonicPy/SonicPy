#!/usr/bin/env python


import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage, QWidget
from PyQt5.QtCore import QObject, pyqtSignal, Qt

import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton, DoubleSpinBoxAlignRight
import numpy as np

from functools import partial

from ua.widgets.WaterfallWidget import WaterfallWidget



        

class FolderListWidget(QWidget):
    
    list_changed_signal = pyqtSignal(list)
   
    panelClosedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Folder list')

        self.resize(200, 800)
        
        self.make_widget()


    def make_widget(self):
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(10, 10, 10, 10)
        
        self.buttons_widget_top = QtWidgets.QWidget()
        self._buttons_layout_top = QtWidgets.QHBoxLayout()
        self._buttons_layout_top.setContentsMargins(0, 0, 0, 0)

        # add top controls here
        self._up_btn = QtWidgets.QPushButton("Move up")
        self._down_btn = QtWidgets.QPushButton("Move down")

        self._up_btn.clicked.connect(self.move_selected_item_up)
        self._down_btn.clicked.connect(self.move_selected_item_down)

        self._buttons_layout_top.addWidget(self._up_btn)
        self._buttons_layout_top.addWidget(self._down_btn)

        self.buttons_widget_top.setLayout(self._buttons_layout_top)
        self._layout.addWidget(self.buttons_widget_top)

        self._folder_list = QtWidgets.QListWidget()
        self._folder_list.setDragDropMode(QtWidgets. QAbstractItemView.InternalMove)
        self._folder_list.itemChanged.connect(self.update_folders)
        self._folder_list.model().rowsMoved.connect(lambda: self.item_dragged_callback())

        self._layout.addWidget(self._folder_list)

        self.setLayout(self._layout)

    def update_folders(self):
        folders = self.get_folder_list()
        self.list_changed_signal.emit(folders)
        
    def get_folder_list(self):

        items = []
        for index in range(self._folder_list.count()):            
            items.append(self._folder_list.item(index).text())
        items.reverse()
        folders = items
        return folders

    def item_dragged_callback(self,*args,**kwargs):
        self.update_folders()

    def move_selected_item_up(self):
        currentRow = self._folder_list.currentRow()
        currentItem = self._folder_list.takeItem(currentRow)
        self._folder_list.insertItem(currentRow - 1, currentItem)
        self._folder_list.setCurrentRow(currentRow - 1)
        self.update_folders()

    def move_selected_item_down(self):
        currentRow = self._folder_list.currentRow()
        currentItem = self._folder_list.takeItem(currentRow)
        self._folder_list.insertItem(currentRow + 1, currentItem)
        self._folder_list.setCurrentRow(currentRow + 1)
        self.update_folders()

    def set_folders(self, fnames):
        local_fnames = copy.deepcopy(fnames)
        self. _folder_list.clear()
        local_fnames.reverse()
        for f in local_fnames:
            list_item = QtWidgets.QListWidgetItem(f)
            #list_item.setFlags(list_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            #list_item.setCheckState(QtCore.Qt.Checked)
            self._folder_list.addItem(list_item)

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()  



class OverViewWidget(QWidget):
    
    preferences_signal = pyqtSignal()
    up_down_signal = pyqtSignal(str)
    panelClosedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.t = None
        self.spectrum = None


        self.setWindowTitle('Time-of-flight analysis')

        self.resize(800, 800)
        
        self.make_widget()

        self.freq_btns_list = []
        self.cond_btns_list = []


    def make_widget(self):
        
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(10, 10, 10, 10)
        
        self.buttons_widget_top = QtWidgets.QWidget()
        self._buttons_layout_top = QtWidgets.QHBoxLayout()
        self._buttons_layout_top.setContentsMargins(0, 0, 0, 0)
        
        
        self.open_btn = QtWidgets.QPushButton("Open folder")
        self.sort_btn = QtWidgets.QPushButton("Sort folders")
        '''self.fname_lbl = QtWidgets.QLineEdit('')
        self.fname_lbl.setMinimumWidth(300)'''
        self.scale_lbl = QtWidgets.QLabel('   Scale:')
        self.scale_ebx = DoubleSpinBoxAlignRight()
        self.scale_ebx.setMaximum(100)
        self.scale_ebx.setMinimum(1)
        self.scale_ebx.setValue(21)
        self.clip_cbx = QtWidgets.QCheckBox('Clip')
        self.clip_cbx.setChecked(True)
        self.save_btn = QtWidgets.QPushButton('Save result')
       
        self._buttons_layout_top.addWidget(self.open_btn)
        #self._buttons_layout_top.addWidget(self.sort_btn)
        self._buttons_layout_top.addWidget(self.scale_lbl)
        self._buttons_layout_top.addWidget(self.scale_ebx)
        self._buttons_layout_top.addWidget(self.clip_cbx)

        self._buttons_layout_top.addSpacerItem(HorizontalSpacerItem())

        self.freq_start = DoubleSpinBoxAlignRight(self.buttons_widget_top)
        self.freq_start.setMinimumWidth(70)
        self.freq_start.setMinimum(1e-9)
        self.freq_start.setSingleStep(1)
        self.freq_start.setValue(24)
        
        self.freq_step = DoubleSpinBoxAlignRight(self.buttons_widget_top)
        self.freq_step.setMinimumWidth(70)
        self.freq_step.setMinimum(1e-9)
        self.freq_step.setSingleStep(0.5)
        self.freq_step.setValue(2)

        self._buttons_layout_top.addWidget(QtWidgets.QLabel('𝑓 start [MHz]'))
        self._buttons_layout_top.addWidget(self.freq_start)
        self._buttons_layout_top.addWidget(QtWidgets.QLabel('𝑓 step [MHz]'))
        self._buttons_layout_top.addWidget(self.freq_step)

        self.buttons_widget_top.setLayout(self._buttons_layout_top)
        self._layout.addWidget(self.buttons_widget_top)


        self.plots_tab_widget= QtWidgets.QTabWidget(self)
        self.plots_tab_widget.setObjectName("plots_tab_widget")

        self.single_frequency_widget = QtWidgets.QWidget(self.plots_tab_widget)
        self._single_frequency_widget_layout = QtWidgets.QVBoxLayout(self.single_frequency_widget)
        self._single_frequency_widget_layout.setContentsMargins(0,0,0,0)
        params = ["Waterfall plot", 'P-T step', 'Time']
        self.single_frequency_waterfall = WaterfallWidget(params=params)
        self._single_frequency_widget_layout.addWidget(self.single_frequency_waterfall)
        self.frequency_lbl = QtWidgets.QLabel()
        #self._single_frequency_widget_layout.addWidget(self.frequency_lbl)
        self.plots_tab_widget.addTab(self.single_frequency_widget, 'Frequency')

        self.single_condition_widget = QtWidgets.QWidget(self.plots_tab_widget)
        self._single_condition_widget_layout = QtWidgets.QVBoxLayout(self.single_condition_widget)
        self._single_condition_widget_layout.setContentsMargins(0,0,0,0)
        params = ["Waterfall plot", 'Frequency step', 'Time']
        self.single_condition_waterfall = WaterfallWidget(params=params)
        self._single_condition_widget_layout.addWidget(self.single_condition_waterfall)
        self.condition_lbl = QtWidgets.QLabel()
        #self._single_condition_widget_layout.addWidget(self.condition_lbl)

        self.plots_tab_widget.addTab(self.single_condition_widget, 'P-T Step')

        self._layout.addWidget(self.plots_tab_widget)

        self.make_bottom_btn_widgets()
        self.make_bottom_combo_widgets()

        self.setLayout(self._layout)

    def make_bottom_combo_widgets(self):
        

        self.freq_scroll = QtWidgets.QScrollBar(orientation=Qt.Horizontal, parent=self.freqs_widget)
        self.freq_scroll.setMinimum(0)
        self.freq_scroll.setMaximum(17)
        self.freq_scroll.setSingleStep(1)
        self.freq_minus_btn = QtWidgets.QPushButton(str("-"))
        self.freq_minus_btn.setMaximumWidth(35)
        self.freq_minus_btn.setObjectName('freq_btn_first')
        self.freq_plus_btn = QtWidgets.QPushButton(str("+"))
        self.freq_plus_btn.setMaximumWidth(35)
        self.freq_plus_btn.setObjectName('freq_btn_last')
        self._freqs_widget_layout.addWidget(self.freq_minus_btn)
        self._freqs_widget_layout.addWidget(self.freq_scroll)
        self._freqs_widget_layout.addWidget(self.freq_plus_btn)
        
        
        self.cond_scroll = QtWidgets.QScrollBar(orientation=Qt.Horizontal, parent=self.conds_widget)
        self.cond_scroll.setMinimum(0)
        self.cond_scroll.setMaximum(17)
        self.cond_scroll.setSingleStep(1)
        self.cond_minus_btn = QtWidgets.QPushButton(str("-"))
        self.cond_minus_btn.setMaximumWidth(35)
        self.cond_minus_btn.setObjectName('cond_btn_first')
        self.cond_plus_btn = QtWidgets.QPushButton(str("+"))
        self.cond_plus_btn.setMaximumWidth(35)
        self.cond_plus_btn.setObjectName('cond_btn_last')
        self._conds_widget_layout.addWidget(self.cond_minus_btn)
        self._conds_widget_layout.addWidget(self.cond_scroll)
        self._conds_widget_layout.addWidget(self.cond_plus_btn)

    def make_bottom_btn_widgets(self):
        self.buttons_widget_bottom_single_frequency = QtWidgets.QWidget()
        self._buttons_layout_bottom_single_frequency = QtWidgets.QHBoxLayout()
        self._buttons_layout_bottom_single_frequency.setContentsMargins(0, 0, 0, 0)
        self.freqs_widget = QtWidgets.QWidget(self.buttons_widget_bottom_single_frequency)
        self._freqs_widget_layout = QtWidgets.QHBoxLayout(self.freqs_widget )
        self._freqs_widget_layout.setSpacing(0)
        #self.freq_btns = QtWidgets.QButtonGroup( self.freqs_widget)
        self.freqs_widget.setLayout(self._freqs_widget_layout)
        self._buttons_layout_bottom_single_frequency.addWidget(self.freqs_widget)
        self.buttons_widget_bottom_single_frequency.setLayout(self._buttons_layout_bottom_single_frequency)
        self._single_frequency_widget_layout.addWidget(self.buttons_widget_bottom_single_frequency)    

        self.buttons_widget_bottom_single_condition = QtWidgets.QWidget()
        self._buttons_layout_bottom_single_condition = QtWidgets.QHBoxLayout()
        self._buttons_layout_bottom_single_condition.setContentsMargins(0, 0, 0, 0)
        self.conds_widget = QtWidgets.QWidget(self.buttons_widget_bottom_single_condition)
        self._conds_widget_layout = QtWidgets.QHBoxLayout(self.conds_widget )
        self._conds_widget_layout.setSpacing(0)
        #self.cond_btns = QtWidgets.QButtonGroup( self.conds_widget)
        self.conds_widget.setLayout(self._conds_widget_layout)
        self._buttons_layout_bottom_single_condition.addWidget(self.conds_widget)
        self.buttons_widget_bottom_single_condition.setLayout(self._buttons_layout_bottom_single_condition)
        self._single_condition_widget_layout.addWidget(self.buttons_widget_bottom_single_condition)

    '''def set_freq_buttons(self, num):

        for b in self.freq_btns_list:
            self._freqs_widget_layout.removeWidget(b)
            self.freq_btns.removeButton(b)
            b.deleteLater()
            b= None
        self.freq_btns_list.clear()

        for f in range(num):
            btn = QtWidgets.QPushButton(str(f))
            btn.setObjectName('freq_btn')
            btn.setCheckable(True)
            self.freq_btns_list.append(btn)
            self.freq_btns.addButton(btn)
            #self._freqs_widget_layout.addWidget(btn)

        self.freq_btns_list[0].setObjectName('freq_btn_first')
        self.freq_btns_list[-1].setObjectName('freq_btn_last')'''
        
    def set_cond_buttons(self, num):

        for b in self.cond_btns_list:
            self._conds_widget_layout.removeWidget(b)
            self.cond_btns.removeButton(b)
            b.deleteLater()
            b= None
        self.cond_btns_list.clear()

        for f in range(num):
            btn = QtWidgets.QPushButton(str(f))
            btn.setObjectName('cond_btn')
            btn.setCheckable(True)
            self.cond_btns_list.append(btn)
            self.cond_btns.addButton(btn)
            #self._conds_widget_layout.addWidget(btn)

        self.cond_btns_list[0].setObjectName('cond_btn_first')
        self.cond_btns_list[-1].setObjectName('cond_btn_last')    
        

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()  




