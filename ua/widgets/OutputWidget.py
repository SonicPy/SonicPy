import imp
import os, os.path, sys, platform, copy
from functools import partial
from time import sleep
from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from um.widgets.CustomWidgets import DoubleSpinBoxAlignRight, HorizontalSpacerItem, VerticalSpacerItem, FlatButton, ListTableWidget, NoRectDelegate

class OutputWidget(QtWidgets.QWidget):
   
    def __init__(self, ctrls = [],params=[]):
        super().__init__()
        
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(8, 0, 8, 0)

        self.output_settings_widget = OutputSettingsWidget()
        self._layout.addWidget(self.output_settings_widget)

        self.header_lbls = ['Folder', 'tp', 'tp st. dev.', 'ts','ts st. dev.', '']
        self.output_tw = ListTableWidget(columns=len(self.header_lbls))
        self.set_up_tw(self.output_tw, self.header_lbls)

        self._layout.addWidget(self.output_tw)

        self.setLayout(self._layout)

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        #self.raise_()  

    ################################################################################################
    # Now comes all the tw stuff
    ################################################################################################        

    def set_up_tw(self, tw, header_lbls):
        header_view = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, tw)
        tw.setHorizontalHeader(header_view)
        tw.setHorizontalHeaderLabels(header_lbls)
        header_view.setResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        '''for col in range(len(header_lbls)-1):
            header_view.setResizeMode(col , QtWidgets.QHeaderView.ResizeToContents)'''
        header_view.setResizeMode(len(header_lbls)-1, QtWidgets.QHeaderView.Stretch)
    
        tw.setItemDelegate(NoRectDelegate())

    def add_condition(self, name):
        self.output_tw.blockSignals(True)
        current_rows = self.output_tw.rowCount()
        self.output_tw.setRowCount(current_rows + 1)

        name_item = QtWidgets.QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
        name_item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.output_tw.setItem(current_rows, 0, name_item)

        tp_item = QtWidgets.QTableWidgetItem(' '*8)
        tp_item.setFlags(tp_item.flags() & ~QtCore.Qt.ItemIsEditable)
        tp_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.output_tw.setItem(current_rows, 1, tp_item)

        t_e_p_item = QtWidgets.QTableWidgetItem(' '*8)
        t_e_p_item.setFlags(t_e_p_item.flags() & ~QtCore.Qt.ItemIsEditable)
        t_e_p_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.output_tw.setItem(current_rows, 2, t_e_p_item)

        ts_item = QtWidgets.QTableWidgetItem(' '*8)
        ts_item.setFlags(ts_item.flags() & ~QtCore.Qt.ItemIsEditable)
        ts_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.output_tw.setItem(current_rows, 3, ts_item)

        t_e_s_item = QtWidgets.QTableWidgetItem(' '*8)
        t_e_s_item.setFlags(t_e_s_item.flags() & ~QtCore.Qt.ItemIsEditable)
        t_e_s_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.output_tw.setItem(current_rows, 4, t_e_s_item)



        '''self.output_tw.setColumnWidth(1, 60)
        self.output_tw.setColumnWidth(2, 60)
        self.output_tw.setColumnWidth(3, 60)
        self.output_tw.setColumnWidth(4, 60)'''
        self.output_tw.setRowHeight(current_rows, 25)
        self.select_output(current_rows)
        self.output_tw.blockSignals(False)

    def select_output(self, ind):
        self.output_tw.blockSignals(True)
        self.output_tw.selectRow(ind)
        self.output_tw.blockSignals(False)

    def get_selected_output_row(self):
        selected = self.output_tw.selectionModel().selectedRows()
        try:
            row = selected[0].row()
        except IndexError:
            row = -1
        return row

    def get_output(self):
        pass

    def clear_output(self):
        for row in range(self.output_tw.rowCount()):
            self.del_output(-1)

    def del_output(self, ind):
        self.output_tw.blockSignals(True)
        self.output_tw.removeRow(ind)
        self.output_tw.blockSignals(False)
       

        if self.output_tw.rowCount() > ind:
            self.select_output(ind)
        else:
            self.select_output(self.output_tw.rowCount() - 1)
    
    def rename_output(self, ind, name):
        name_item = self.output_tw.item(ind, 0)
        name_item.setText(name)

    def set_output_tp(self, ind, tp):
        self.blockSignals(True)
        tp_item = self.output_tw.item(ind, 1)
        try:
            tp_item.setText("{0:.3f} ns".format(tp))
        except ValueError:
            tp_item.setText("{0} ns".format(tp))
        self.blockSignals(False)

        
    
    def get_output_tp(self, ind):
        tp_item = self.output_tw.item(ind, 1)
        tp = float(str(tp_item.text()).split()[0])
        return tp

    def set_output_t_e_p(self, ind, tep):
        self.blockSignals(True)
        tep_item = self.output_tw.item(ind, 2)
        try:
            tep_item.setText("{0:.3f} ns".format(tep))
        except ValueError:
            tep_item.setText("{0} ns".format(tep))
        self.blockSignals(False)

    def get_output_t_e_p(self, ind):
        tep_item = self.output_tw.item(ind, 2)
        tep = float(str(tep_item.text()).split()[0])
        return tep

    def set_output_ts(self, ind, ts):
        self.blockSignals(True)
        ts_item = self.output_tw.item(ind, 3)
        try:
            ts_item.setText("{0:.3f} ns".format(ts))
        except ValueError:
            ts_item.setText("{0} ns".format(ts))
        self.blockSignals(False)

    def get_output_ts(self, ind):
        ts_item = self.output_tw.item(ind, 3)
        try:
            ts = float(str(ts_item.text()).split()[0])
        except:
            ts = None
        return ts

    def set_output_t_e_s(self, ind, tes):
        self.blockSignals(True)
        tes_item = self.output_tw.item(ind, 4)
        try:
            tes_item.setText("{0:.3f} ns".format(tes))
        except ValueError:
            tes_item.setText("{0} ns".format(tes))
        self.blockSignals(False)

    def get_output_t_e_s(self, ind):
        tes_item = self.output_tw.item(ind, 4)
        try:
            tes = float(str(tes_item.text()).split()[0])
        except:
            tes = None
        return tes


       ########################################################################################


    

class OutputSettingsWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None, ctrls = [],params=[]):
        super().__init__(parent = parent)  

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setSpacing(7)
        self._layout.setContentsMargins(5, 5, 5, 5)

        self.output_widget_lbl = QtWidgets.QLabel('Output')
        self._layout.addWidget(self.output_widget_lbl)

        self.cond_min_lbl = QtWidgets.QLabel("min")
        self.cond_min_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.cond_min_bx = DoubleSpinBoxAlignRight()
        self.cond_min_bx.setMinimum(0)
        self.cond_min_bx.setMinimumWidth(70)
        self.cond_min_bx.setSingleStep(1)
        self._layout.addWidget(self.cond_min_lbl)
        self._layout.addWidget(self.cond_min_bx)

        self.cond_max_lbl = QtWidgets.QLabel('max')
        self.cond_max_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.cond_max_bx = DoubleSpinBoxAlignRight()
        self.cond_max_bx.setMinimum(0)
        self.cond_max_bx.setMinimumWidth(70)
        self.cond_max_bx.setSingleStep(1)
        self._layout.addWidget(self.cond_max_lbl)
        self._layout.addWidget(self.cond_max_bx)

        self.do_all_frequencies_btn = FlatButton("Go")
        self.do_all_frequencies_btn.setMinimumWidth(70)
        self._layout.addWidget(self.do_all_frequencies_btn)

        self._layout.addSpacerItem(HorizontalSpacerItem())


        self.setLayout(self._layout)


