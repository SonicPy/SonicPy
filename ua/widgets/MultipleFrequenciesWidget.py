import os, os.path, sys, platform, copy
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from um.widgets.CustomWidgets import DoubleSpinBoxAlignRight, HorizontalSpacerItem, VerticalSpacerItem, FlatButton

class MultipleFrequenciesWidget(QtWidgets.QWidget):
   
    def __init__(self, ctrls = [],params=[]):
        super().__init__()
        
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(8, 0, 8, 0)


        
        '''self.lbl = QtWidgets.QLabel('MultipleFrequenciesWidget')

        self._layout.addWidget(self.lbl)

        condition_lbl = QtWidgets.QLabel('Selected condition:')
        self.condition_val = QtWidgets.QLabel()
        self._layout.addWidget(condition_lbl)
        self._layout.addWidget(self.condition_val)'''

        self.mode_tab_widget= QtWidgets.QTabWidget(self)
        self.mode_tab_widget.setObjectName("mode_tab_widget")
        

        self.frequency_sweep_widget = FrequencySweepWidget(self.mode_tab_widget)
       

        self.broadband_pulse_widget = BroadbandPulseWidget(self.mode_tab_widget)
       

        self.mode_tab_widget.addTab(self.frequency_sweep_widget, "Discrete 𝑓")
        self.mode_tab_widget.addTab(self.broadband_pulse_widget, "Broadband")

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
        self._layout.setSpacing(7)
        self._layout.setContentsMargins(5, 5, 5, 5)

        '''self.frequency_sweep_widget_lbl = QtWidgets.QLabel('Discrete 𝑓')
        self._layout.addWidget(self.frequency_sweep_widget_lbl)'''

        self.f_min_lbl = QtWidgets.QLabel("𝑓 min")
        self.f_min_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.f_min_bx = DoubleSpinBoxAlignRight()
        self.f_min_bx.setMinimum(0)
        self.f_min_bx.setMinimumWidth(70)
        self.f_min_bx.setSingleStep(1)
        self._layout.addWidget(self.f_min_lbl)
        self._layout.addWidget(self.f_min_bx)

        self.f_max_lbl = QtWidgets.QLabel('𝑓 max')
        self.f_max_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.f_max_bx = DoubleSpinBoxAlignRight()
        self.f_max_bx.setMinimum(0)
        self.f_max_bx.setMinimumWidth(70)
        self.f_max_bx.setSingleStep(1)
        self._layout.addWidget(self.f_max_lbl)
        self._layout.addWidget(self.f_max_bx)

        self.do_all_frequencies_btn = FlatButton("Go")
        self.do_all_frequencies_btn.setMinimumWidth(70)
        self._layout.addWidget(self.do_all_frequencies_btn)

        self._layout.addSpacerItem(HorizontalSpacerItem())


        self.setLayout(self._layout)

   
class BroadbandPulseWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None, ctrls = [],params=[]):
        super().__init__(parent = parent)  

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setSpacing(7)
        self._layout.setContentsMargins(5, 5, 5, 5)

        '''self.frequency_sweep_widget_lbl = QtWidgets.QLabel('Broadband')
        self._layout.addWidget(self.frequency_sweep_widget_lbl)'''

        self.f_min_lbl = QtWidgets.QLabel("𝑓 min")
        self.f_min_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.f_min_bx = DoubleSpinBoxAlignRight()
        self.f_min_bx.setMinimum(0)
        self.f_min_bx.setMinimumWidth(70)
        self.f_min_bx.setSingleStep(1)
        self._layout.addWidget(self.f_min_lbl)
        self._layout.addWidget(self.f_min_bx)

        self.f_max_lbl = QtWidgets.QLabel('𝑓 max')
        self.f_max_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.f_max_bx = DoubleSpinBoxAlignRight()
        self.f_max_bx.setMinimum(0)
        self.f_max_bx.setMinimumWidth(70)
        self.f_max_bx.setSingleStep(1)
        self._layout.addWidget(self.f_max_lbl)
        self._layout.addWidget(self.f_max_bx)

        self.f_step_lbl = QtWidgets.QLabel('𝑓 step')
        self.f_step_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.f_step_bx = DoubleSpinBoxAlignRight()
        self.f_step_bx.setMinimum(1)
        self.f_step_bx.setMinimumWidth(70)
        self.f_step_bx.setValue(2)
        self.f_step_bx.setSingleStep(1)
        self._layout.addWidget(self.f_step_lbl)
        self._layout.addWidget(self.f_step_bx)

        self.do_all_frequencies_btn = FlatButton("Go")
        self.do_all_frequencies_btn.setMinimumWidth(70)
        self._layout.addWidget(self.do_all_frequencies_btn)

        self._layout.addSpacerItem(HorizontalSpacerItem())


        self.setLayout(self._layout)
