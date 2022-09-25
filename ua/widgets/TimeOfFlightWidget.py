#!/usr/bin/env python


import os, os.path
from PyQt5 import uic, QtWidgets,QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton


from .. import style_path, icons_path, title

class TimeOfFlightWidget(QMainWindow):
    
    preferences_signal = pyqtSignal()
    up_down_signal = pyqtSignal(str)
    panelClosedSignal = pyqtSignal()

    def __init__(self, app, overview_widget, multiple_frequencies_widget, analysis_widget, arrow_plot_widget, output_widget):
        super().__init__()
        self.app = app
        self.overview_widget = overview_widget

        self.multiple_frequencies_widget = multiple_frequencies_widget
        self.analysis_widget = analysis_widget
        self.output_widget = output_widget
        self.arrow_plot_widget = arrow_plot_widget

        self.middle_widget = QtWidgets.QWidget()
        self._middle_widget_layout = QtWidgets.QVBoxLayout()
        self._middle_widget_layout.setContentsMargins(5,5,5,5)
        self._middle_widget_layout.addWidget(self.analysis_widget)
        self._middle_widget_layout.addWidget(self.multiple_frequencies_widget)
        self.middle_widget.setLayout(self._middle_widget_layout)

        self.right_widget = QtWidgets.QSplitter(Qt.Vertical)
        self.right_widget.addWidget(self.arrow_plot_widget)
        self.right_widget.addWidget(self.output_widget)
   
        

        self.setWindowTitle(title)

        self.resize(1440, 790)
        
        self.make_widget()

        self.setCentralWidget(self.my_widget)

        self.create_menu()
        self.style_widgets()

        self.key_control_pressed = False

    def clear_title(self):
        self.setWindowTitle(title)

    def create_menu(self):
        
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        file_menu = QtWidgets.QMenu("&File", self)
        menuBar.addMenu(file_menu)
        # Creating menus using a title


        self.proj_new_act = QtWidgets.QAction('&New project', self)        
        file_menu.addAction(self.proj_new_act)
        self.proj_open_act = QtWidgets.QAction('&Open project', self)        
        file_menu.addAction(self.proj_open_act)
        self.proj_save_act = QtWidgets.QAction('&Save project', self)  
        self.proj_save_act.setEnabled(False)     
        file_menu.addAction(self.proj_save_act)
        self.proj_save_as_act = QtWidgets.QAction('Save project &as...', self)  
        self.proj_save_as_act.setEnabled(False)
        file_menu.addAction(self.proj_save_as_act)
        self.proj_close_act = QtWidgets.QAction('&Close project', self)        
        file_menu.addAction(self.proj_close_act)
        self.proj_close_act.setEnabled(False)

        file_menu.addSeparator()

        self.import_menu_mnu = QtWidgets.QMenu("&Import ultrasound data", self)
        self.import_menu_mnu.setEnabled(False)
        file_menu.addMenu(self.import_menu_mnu)
        self.import_multiple_freq_act = QtWidgets.QAction('&Discrete 𝑓', self)        
        self.import_menu_mnu.addAction(self.import_multiple_freq_act)
        self.import_broadband_act = QtWidgets.QAction('&Broadband', self)        
        self.import_menu_mnu.addAction(self.import_broadband_act)
        self.sort_data_act = QtWidgets.QAction('&Sort data points', self)        
        file_menu.addAction(self.sort_data_act)
        self.sort_data_act.setEnabled(False)

        file_menu.addSeparator()

        self.export_menu_mnu = QtWidgets.QMenu("&Export", self)
        self.export_menu_mnu.setEnabled(False)
        file_menu.addMenu(self.export_menu_mnu)
        self.export_results_act = QtWidgets.QAction(f'\N{GREEK SMALL LETTER TAU} results', self)        
        self.export_menu_mnu.addAction(self.export_results_act)
        self.export_overview_mnu = QtWidgets.QMenu('&Overview', self)        
        self.export_menu_mnu.addMenu(self.export_overview_mnu)

        self.export_single_frequency_plot_act = QtWidgets.QAction('&Single 𝑓', self)        
        self.export_overview_mnu.addAction(self.export_single_frequency_plot_act)
        self.export_single_condition_plot_act = QtWidgets.QAction('&Single condition', self)        
        self.export_overview_mnu.addAction(self.export_single_condition_plot_act)

        self.export_correlation_mnu = QtWidgets.QMenu("&Correlation", self)  
        self.export_menu_mnu.addMenu(self.export_correlation_mnu)

        self.export_selected_waveform_plot_act = QtWidgets.QAction('&Selected waveform', self)        
        self.export_correlation_mnu.addAction(self.export_selected_waveform_plot_act)
        self.export_selected_ehcoes_plot_act = QtWidgets.QAction('&Selected echoes', self)        
        self.export_correlation_mnu.addAction(self.export_selected_ehcoes_plot_act)
        self.export_filtered_echoes_plot_act = QtWidgets.QAction('&Filtered', self)        
        self.export_correlation_mnu.addAction(self.export_filtered_echoes_plot_act)
        self.export_correlation_plot_act = QtWidgets.QAction('&Correlation', self)        
        self.export_correlation_mnu.addAction(self.export_correlation_plot_act)

        self.export_arrow_plot_act = QtWidgets.QAction('&Inverse 𝑓', self)        
        self.export_menu_mnu.addAction(self.export_arrow_plot_act)

    def keyPressEvent(self, e):
        
        if e.key() == Qt.Key_Control:
            pass
            
        elif e.key() == Qt.Key_Up:
            event = 'up'
        elif e.key() == Qt.Key_Down:
            event = 'down'

        else: 
            super().keyPressEvent(e)

    def keyReleaseEvent(self, e):
        
        if e.key() == Qt.Key_Control:
            pass
            
        else:
            super().keyReleaseEvent(e)


    def closeEvent(self, QCloseEvent, *event):
        self.app.closeAllWindows()
        self.panelClosedSignal.emit()

    def make_widget(self):
        self.my_widget = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.detail_widget = QtWidgets.QWidget()
        self._detail_layout = QtWidgets.QHBoxLayout()
        self._detail_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget_top = QtWidgets.QWidget()
        self._buttons_layout_top = QtWidgets.QHBoxLayout()
        self._buttons_layout_top.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget_bottom = QtWidgets.QWidget()
        
        self._buttons_layout_bottom = QtWidgets.QHBoxLayout()
        self._buttons_layout_bottom.setContentsMargins(0, 0, 0, 0)
        
        

        
        self._buttons_layout_top.addSpacerItem(HorizontalSpacerItem())
        
        self.buttons_widget_top.setLayout(self._buttons_layout_top)
        #self._layout.addWidget(self.buttons_widget_top)
        
        
        self.center_widget = QtWidgets.QWidget(self)
        self._center_widget_layout = QtWidgets.QHBoxLayout(self.center_widget)

        

        self.splitter_horizontal = QtWidgets.QSplitter(Qt.Horizontal)
        self.splitter_horizontal.addWidget(self.overview_widget)
        self.splitter_horizontal.addWidget(self.middle_widget)
        self.splitter_horizontal.addWidget(self.right_widget)
        self.splitter_horizontal.setSizes([600,600, 600])
        self._center_widget_layout.addWidget(self.splitter_horizontal)


        self.center_widget.setLayout(self._center_widget_layout)
        self._layout.addWidget(self.center_widget)

        
        calc_btn = QtWidgets.QPushButton('Correlate')
        #_buttons_layout_bottom.addWidget(calc_btn)
        #_buttons_layout_bottom.addWidget(QtWidgets.QLabel('2-way travel time:'))
        output_ebx = QtWidgets.QLineEdit('')
        #_buttons_layout_bottom.addWidget(output_ebx)
       
        
        self.buttons_widget_bottom.setLayout(self._buttons_layout_bottom)
        #self._layout.addWidget(self.buttons_widget_bottom)
        self.my_widget.setLayout(self._layout)

    

        


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

    
 
 
    def create_menu_strip(self, orientation = "horizontal"):

        self._menu_layout = None
        if orientation == 'horizontal':
            self._menu_layout = QtWidgets.QHBoxLayout()
            spacer = QtWidgets.QSpacerItem(30, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        elif orientation == 'vertical':
            self._menu_layout = QtWidgets.QVBoxLayout()
            spacer = QtWidgets.QSpacerItem(10, 30, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        if self._menu_layout !=None:

            self.save_as_btn = FlatButton()
            self.save_as_btn.setEnabled(False)
            self.save_btn = FlatButton()
            self.save_btn.setEnabled(False)
            self.load_btn = FlatButton()
            self.undo_btn = FlatButton()
            self.reset_btn = FlatButton()

            self._menu_layout.setContentsMargins(5, 0, 3, 0)
            self._menu_layout.setSpacing(5)

            self._menu_layout.addSpacerItem(spacer)
            self._menu_layout.addWidget(self.load_btn)
            self._menu_layout.addWidget(self.save_btn)
            self._menu_layout.addWidget(self.save_as_btn)
            self._menu_layout.addSpacerItem(spacer)
            self._menu_layout.addWidget(self.undo_btn)
            self._menu_layout.addWidget(self.reset_btn)
            self._menu_layout.addSpacerItem(spacer)

            self.style_menu_buttons()

    def style_menu_buttons(self):

            
        button_height = 32
        button_width = 32

        icon_size = QtCore.QSize(22, 22)
        self.save_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'save.ico')))
        self.save_btn.setIconSize(icon_size)
        self.save_btn.setMinimumHeight(button_height)
        self.save_btn.setMaximumHeight(button_height)
        self.save_btn.setMinimumWidth(button_width)
        self.save_btn.setMaximumWidth(button_width)

        self.save_as_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'save_as.ico')))
        self.save_as_btn.setIconSize(icon_size)
        self.save_as_btn.setMinimumHeight(button_height)
        self.save_as_btn.setMaximumHeight(button_height)
        self.save_as_btn.setMinimumWidth(button_width)
        self.save_as_btn.setMaximumWidth(button_width)

        self.load_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'open.ico')))
        self.load_btn.setIconSize(icon_size)
        self.load_btn.setMinimumHeight(button_height)
        self.load_btn.setMaximumHeight(button_height)
        self.load_btn.setMinimumWidth(button_width)
        self.load_btn.setMaximumWidth(button_width)

        self.undo_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'undo.ico')))
        self.undo_btn.setIconSize(icon_size)
        self.undo_btn.setMinimumHeight(button_height)
        self.undo_btn.setMaximumHeight(button_height)
        self.undo_btn.setMinimumWidth(button_width)
        self.undo_btn.setMaximumWidth(button_width)

        self.reset_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'restore.ico')))
        self.reset_btn.setIconSize(icon_size)
        self.reset_btn.setMinimumHeight(button_height)
        self.reset_btn.setMaximumHeight(button_height)
        self.reset_btn.setMinimumWidth(button_width)
        self.reset_btn.setMaximumWidth(button_width)

    def preferences_module(self):
        self.preferences_signal.emit()

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()  




