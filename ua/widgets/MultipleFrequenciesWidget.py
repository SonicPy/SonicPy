import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton

class MultipleFrequenciesWidget(QtWidgets.QWidget):
   
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
        

        self.frequency_sweep_widget = FrequencySweepWidget(self.mode_tab_widget)
       

        self.broadband_pulse_widget = BroadbandPulseWidget(self.mode_tab_widget)
       

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


class FrequencySweepWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None, ctrls = [],params=[]):
        super().__init__(parent = parent)  

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.frequency_sweep_widget_lbl = QtWidgets.QLabel('Frequency Sweep')
        self._layout.addWidget(self.frequency_sweep_widget_lbl)
        self.do_all_frequencies_btn = QtWidgets.QPushButton("Do all")
        self._layout.addWidget(self.do_all_frequencies_btn)


        self.setLayout(self._layout)


class BroadbandPulseWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None, ctrls = [],params=[]):
        super().__init__(parent = parent)  

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.frequency_sweep_widget_lbl = QtWidgets.QLabel('Broadband Pulse')
        self._layout.addWidget(self.frequency_sweep_widget_lbl)
        self.do_all_frequencies_btn = QtWidgets.QPushButton("Do all")
        self._layout.addWidget(self.do_all_frequencies_btn)


        self.setLayout(self._layout)