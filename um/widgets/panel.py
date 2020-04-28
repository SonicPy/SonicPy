

from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton

import time
from um.models.pv_model import PV
from um.widgets.pvWidgets import pvQCheckBox, pvQComboBox, pvQDoubleSpinBox, pvQLineEdit, pvQPushButton

from um.models.pvServer import pvServer
from um.widgets.pvWidgets import pvQWidgets

class Panel(QtWidgets.QGroupBox):

    panelClosedSignal = pyqtSignal()
    def __init__(self, title='',pvs=[], isMain = False):
        super().__init__()
        self.pv_server = pvServer()
        self.pv_widgets = pvQWidgets()
        self.isMain = isMain
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setSizePolicy(sizePolicy)
        self.setTitle(title)
        self.i = 0
        self._layout, self.widgets = self.make_widget_items(pvs)
        self.setLayout(self._layout)
        self.default_items = pvs
        

    def closeEvent(self, QCloseEvent, *event):
        self.panelClosedSignal.emit()
        time.sleep(0.1)


    def make_widget_items(self, pvs):
        

        _parameter_layout = QtWidgets.QVBoxLayout()
        self.controls = {}
        self._grid = QtWidgets.QGridLayout()
        self._grid.setContentsMargins(10, 10, 10, 10)
        self._grid.setSpacing(5)
        
        
        for i, pv in enumerate(pvs):
            if pv is not None:
                
                
                ctrl, label = self.pv_widgets.pvWidget(pv)
                    
                self.controls[pv] = ctrl

                if ctrl is not None:
                    self._grid.addWidget(label, i, 0)
                    self._grid.addWidget(ctrl, i, 1)
                self.i = i
        
        
        
        if self.isMain:
            self.i +=1
            self._grid.addWidget(self.save_btn, self.i,0)
            self._grid.addWidget(self.load_btn, self.i,1)
            
            
        return self._grid, self.controls

    

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        #self.raise_()  
