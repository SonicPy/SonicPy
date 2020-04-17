

from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
from functools import partial
import time
from um.models.pv_model import PV
from PyQt5.QtWidgets import QWidget, QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox, QPushButton, QAction



class pvQWidget(QWidget):
    def __init__(self, myPV):
        #super().__init__(self)
        self.pv = myPV
        self.val = None
        self.pv_name = myPV._pv_name
        self.setToolTip(self.pv_name)
        
        if hasattr(self.pv,'_val_scale'):
            self.scale = self.pv._val_scale
        else:
            self.scale = 1
        if hasattr(self.pv,'get'):
            current_value = self.pv.get()
        else: current_value = None
        if current_value is not None:
            self.setValue( self.pv._pv_name, current_value)
        else:
            self.setValue( self.pv._pv_name, [myPV._val])
        enabled = myPV._set_enabled
        super().setEnabled(enabled) 
        self.pv.value_changed_signal.connect(self.setValue)
        self.setMinimumWidth( 150)
        

    def valueChangedCallback(self,value):
        if hasattr(self.pv,'set'):
            if self.scale !=1:
                value = value * self.scale
            self.pv.set(value)

    def setValue(self, tag, value):
        value = value[0]
        if self.scale !=1:
                value = value / self.scale
        self.val = value

class pvQLineEdit(QLineEdit, pvQWidget):
    def __init__(self, myPV):
        QLineEdit.__init__(self)
        pvQWidget.__init__(self, myPV)
        widget = self
        self.editingFinished.connect(lambda:self.valueChangedCallback(self.text()))
        

    def setValue(self, tag, value):
        pvQWidget.setValue(self, tag, value)
        value = self.val
        self.blockSignals(True)
        
        widget = self
        current_value = widget.text()
        if value != current_value:
            QLineEdit.setText(widget, str(value))
        self.blockSignals(False)

class pvQComboBox(QComboBox, pvQWidget):
    def __init__(self, myPV):
        QComboBox.__init__(self)
        pvQWidget.__init__(self, myPV)
        widget = self
        items = myPV._items
        for item in items:
            QComboBox.addItem(widget, item)
        self.currentTextChanged.connect(self.valueChangedCallback)

       

    def setValue(self, tag, value):
        pvQWidget.setValue(self, tag, value)
        value = self.val
        self.blockSignals(True)
       
        widget = self
        current_value = widget.currentText()
        if value != current_value:
            QComboBox.setCurrentText(widget, str(value))
        self.blockSignals(False)    

class pvQDoubleSpinBox(QDoubleSpinBox, pvQWidget):
    def __init__(self, myPV):
        QDoubleSpinBox.__init__(self)
        pvQWidget.__init__(self, myPV)
        

        widget = self
        QDoubleSpinBox.setGroupSeparatorShown(widget, True)
        minimum = myPV._min
        maximum = myPV._max
        
                    
        QDoubleSpinBox.setMinimum(widget, minimum)
        QDoubleSpinBox.setMaximum(widget, maximum)

        val = myPV._val            
       

        self.setValue(widget, [val])
        if myPV._type is int:
            QDoubleSpinBox.setDecimals(widget, 0)
        else:
            increment = myPV._increment
        
            QDoubleSpinBox.setDecimals(widget, 3)
            QDoubleSpinBox.setSingleStep(widget, increment) 
        QDoubleSpinBox.setKeyboardTracking(widget, False)
        self.valueChanged.connect(self.valueChangedCallbackPreTreat)

    def valueChangedCallbackPreTreat(self, val):
        val = round(val,5)
        
        self.valueChangedCallback(val )

    def setValue(self, tag, value):
        
        pvQWidget.setValue(self, tag, value)
        
        value = self.val 
        

        self.blockSignals(True)
        
        widget = self
        current_value = widget.value()
        if value != current_value:
            QDoubleSpinBox.setValue(widget, float(value))
        self.blockSignals(False)  

class pvQCheckBox(QCheckBox, pvQWidget):
    def __init__(self, myPV):
        desc = myPV._description.split(';')[1]
        
        QCheckBox.__init__(self)
        QCheckBox.setText(self, desc)
        pvQWidget.__init__(self, myPV)
        pvQWidget.setMinimumWidth(self, 90)
        widget = self
        value = myPV._val
        QCheckBox.setChecked(widget, value)
        self.clicked.connect(self.valueChangedCallback)

    def setValue(self, tag, value):
        pvQWidget.setValue(self, tag, value)
        value = self.val
        self.blockSignals(True)
       
        widget = self
        current_value = widget.isChecked()
        if value != current_value:
            QCheckBox.setChecked(widget, value)
        self.blockSignals(False)  

class pvQPushButton(QPushButton, pvQWidget):
    def __init__(self, myPV):
        desc = myPV._description.split(';')[1]
        
        QPushButton.__init__(self)
        
        
        QPushButton.setText(self, desc)
        pvQWidget.__init__(self, myPV)

        pvQWidget.setMinimumWidth(self, 90)
        widget = self
        QPushButton.setCheckable(widget, True)
        val = myPV._val
        QPushButton.setChecked(widget, val)
        self.clicked.connect(self.valueChangedCallback)

    def setValue(self, tag, value):
        widget = self
        
        pvQWidget.setValue(self, tag, value)
        value = self.val
        self.blockSignals(True)
        
        
        widget = self
        current_value = widget.isChecked()
        if value != current_value:
            QPushButton.setChecked(widget, value)
            
        self.blockSignals(False)  