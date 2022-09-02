import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton

class MultipleFrequenciesWidget(QtWidgets.QWidget):
    panelClosedSignal = pyqtSignal()
    def __init__(self, ctrls = [],params=[]):
        super().__init__()
        
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(8, 0, 8, 0)


        
        self.lbl = QtWidgets.QLabel('MultipleFrequenciesWidget')

        self._layout.addWidget(self.lbl)

        condition_lbl = QtWidgets.QLabel('Selected condition:')
        self.condition_val = QtWidgets.QLabel()
        self._layout.addWidget(condition_lbl)
        self._layout.addWidget(self.condition_val)

        self.mode_tab_widget= QtWidgets.QTabWidget(self)
        self.mode_tab_widget.setObjectName("mode_tab_widget")
        

        self.frequency_sweep_widget = QtWidgets.QWidget(self.mode_tab_widget)
        self._frequency_sweep_widget_layout = QtWidgets.QVBoxLayout(self.frequency_sweep_widget)
        self._frequency_sweep_widget_layout.setContentsMargins(0,0,0,0)
        self.frequency_sweep_widget_lbl = QtWidgets.QLabel('Frequency Sweep')
        self._frequency_sweep_widget_layout.addWidget(self.frequency_sweep_widget_lbl)
        self.do_all_frequencies_btn = QtWidgets.QPushButton("Do all")
        self._frequency_sweep_widget_layout.addWidget(self.do_all_frequencies_btn)

        self.broadband_pulse_widget = QtWidgets.QWidget(self.mode_tab_widget)
        self._broadband_pulse_widget_layout = QtWidgets.QVBoxLayout(self.broadband_pulse_widget)
        self._broadband_pulse_widget_layout.setContentsMargins(0,0,0,0)
        self.broadband_pulse_widget_lbl = QtWidgets.QLabel('Broadband pulse')
        self._broadband_pulse_widget_layout.addWidget(self.broadband_pulse_widget_lbl)

        self.mode_tab_widget.addTab(self.frequency_sweep_widget, "Frequency sweep")
        self.mode_tab_widget.addTab(self.broadband_pulse_widget, "Broadband pulse")

        self._layout.addWidget(self.mode_tab_widget)

        

        self.setLayout(self._layout)


        self.setStyleSheet("""
            #FlatButton {
                min-width: 120;
            }
            #pvQPushButton {
                min-width: 120;
            }
            
        """)



    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        #self.raise_()  



