

from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton

import time
from um.models.pv_model import PV
from um.widgets.pvWidgets import pvQCheckBox, pvQComboBox, pvQDoubleSpinBox, pvQLineEdit, pvQPushButton


class Panel(QtWidgets.QGroupBox):

    panelClosedSignal = pyqtSignal()
    def __init__(self, title='',pvs={}, isMain = False):
        super().__init__()
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
                
                
                ctrl, label = self.make_pv_widget(pv)
                    
                self.controls[pv._pv_name] = ctrl

                if ctrl is not None:
                    self._grid.addWidget(label, i, 0)
                    self._grid.addWidget(ctrl, i, 1)
                self.i = i
        
        
        self.save_btn = QtWidgets.QPushButton('Save')
        self.load_btn = QtWidgets.QPushButton('Load')
        
        if self.isMain:
            self.i +=1
            self._grid.addWidget(self.save_btn, self.i,0)
            self._grid.addWidget(self.load_btn, self.i,1)
            
            
        return self._grid, self.controls

    def make_pv_widget(self, pv):
        ctrl = None
        desc = pv._description.split(';')[0]
        pv_type = pv._type
        
        if pv_type is list:
            ctrl = pvQComboBox(pv) 
        if pv_type is str:    
            ctrl = pvQLineEdit(pv)
        if pv_type is int or pv_type is float:
            ctrl = pvQDoubleSpinBox(pv)
            unit = pv._unit
            if unit != '':
                desc = desc + ' (' + pv._unit + ')'
        if pv_type is bool:
            ctrl = pvQPushButton(pv)
        label = QtWidgets.QLabel(desc)
        return ctrl, label

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        #self.raise_()  
