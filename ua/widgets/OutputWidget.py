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
        #self._layout.setSpacing(0)
        self._layout.setContentsMargins(8, 12, 0, 0)
        

        self.label = QtWidgets.QLabel("Results output")
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.label.setStyleSheet('''font-size: 18pt;''')
        self._layout.addWidget(self.label)

        self.header_lbls = ['Condition', 
                                        f'\N{GREEK SMALL LETTER TAU} P (ns)', 
                                        f'\N{GREEK SMALL LETTER TAU} P  \N{GREEK SMALL LETTER SIGMA} (ns)', 
                                        f'\N{GREEK SMALL LETTER TAU} S (ns)',
                                        f'\N{GREEK SMALL LETTER TAU} S \N{GREEK SMALL LETTER SIGMA} (ns)']
        self.output_tw = ListTableWidget(columns=len(self.header_lbls))
        self.set_up_tw(self.output_tw, self.header_lbls)

        self._layout.addWidget(self.output_tw)
        self.output_settings_widget = OutputMenuWidget()
        self._layout.addWidget(self.output_settings_widget)

        self.setLayout(self._layout)

    def clear_widget(self):
        self.clear_output()

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
        header_view.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        '''for col in range(len(header_lbls)-1):
            header_view.setResizeMode(col , QtWidgets.QHeaderView.ResizeToContents)'''
        header_view.setSectionResizeMode(len(header_lbls)-1, QtWidgets.QHeaderView.Stretch)
    
        tw.setItemDelegate(NoRectDelegate())

    def add_condition(self, name):
        self.output_tw.blockSignals(True)
        current_rows = self.output_tw.rowCount()
        self.output_tw.setRowCount(current_rows + 1)

        name_item = QtWidgets.QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
        name_item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.output_tw.setItem(current_rows, 0, name_item)

        tp_item = QtWidgets.QTableWidgetItem('')
        tp_item.setFlags(tp_item.flags() & ~QtCore.Qt.ItemIsEditable)
        tp_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.output_tw.setItem(current_rows, 1, tp_item)

        t_e_p_item = QtWidgets.QTableWidgetItem('')
        t_e_p_item.setFlags(t_e_p_item.flags() & ~QtCore.Qt.ItemIsEditable)
        t_e_p_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.output_tw.setItem(current_rows, 2, t_e_p_item)

        ts_item = QtWidgets.QTableWidgetItem('')
        ts_item.setFlags(ts_item.flags() & ~QtCore.Qt.ItemIsEditable)
        ts_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.output_tw.setItem(current_rows, 3, ts_item)

        t_e_s_item = QtWidgets.QTableWidgetItem('')
        t_e_s_item.setFlags(t_e_s_item.flags() & ~QtCore.Qt.ItemIsEditable)
        t_e_s_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.output_tw.setItem(current_rows, 4, t_e_s_item)



        self.output_tw.setRowHeight(current_rows, 25)
        self.select_output(current_rows)
        self.output_tw.blockSignals(False)

    def re_order_rows(self, sort_order):
        table_data = self.get_table_data()
        row_names = {}
        for row in table_data:
            row_names[row[0]] = row

        for i, name in enumerate(sort_order):
            row = row_names[name]
            self.set_row(i,row)
        
    def set_row(self, ind, row):

        self.set_name(ind, row[0])
        self.set_output_tp(ind, row[1])
        self.set_output_t_e_p(ind, row[2])
        self.set_output_ts(ind, row[3])
        self.set_output_t_e_s(ind, row[4])


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
        num_rows = self.output_tw.rowCount()
        for row in range(num_rows):
            self.del_output(0)
        num_rows = self.output_tw.rowCount()
    

    def del_output(self, ind):
        self.output_tw.blockSignals(True)
        self.output_tw.removeRow(ind)
        self.output_tw.blockSignals(False)
       

        if self.output_tw.rowCount() > ind:
            self.select_output(ind)
        else:
            self.select_output(self.output_tw.rowCount() - 1)
    
    def get_table_data(self):
        
        rows = self.output_tw.rowCount()
        lines=[]
        first_line = ['Condition', 
                    f't P (ns)', 
                    f't P st.dev (ns)', 
                    f't S (ns)',
                    f't S st.dev (ns)']
        lines.append(first_line)
        for row in range(rows):
            name = self.get_name(row)
            tp = self.get_output_tp(row)
            tep = self.get_output_t_e_p(row)
            ts = self.get_output_ts(row)
            tes = self.get_output_t_e_s(row)
            line = [name, tp, tep, ts, tes]
            lines.append(line)
        return lines
    
    def set_name(self, ind, name):
        name_item = self.output_tw.item(ind, 0)
        name_item.setText(name)

    def get_name(self, ind):
        name_item = self.output_tw.item(ind, 0).text()
        
        return name_item

    def set_output_tp(self, ind, tp):
        self.blockSignals(True)
        tp_item = self.output_tw.item(ind, 1)
        try:
            tp_item.setText("{0:.3f}   ".format(tp))
        except ValueError:
            tp_item.setText("{0}".format(tp))
        self.blockSignals(False)

        
    
    def get_output_tp(self, ind):
        tp_item = self.output_tw.item(ind, 1)
        tp = tp_item.text().rstrip().lstrip()
        if len(tp):
            out = float(tp)
        else:
            out = ''
        return out

    def set_output_t_e_p(self, ind, tep):
        self.blockSignals(True)
        tep_item = self.output_tw.item(ind, 2)
        try:
            tep_item.setText("{0:.3f}   ".format(tep))
        except ValueError:
            tep_item.setText("{0}".format(tep))
        self.blockSignals(False)

    def get_output_t_e_p(self, ind):
        tep_item = self.output_tw.item(ind, 2)
        tep = tep_item.text().rstrip().lstrip()
        if len(tep):
            out = float(tep)
        else:
            out = ''
        return out

    def set_output_ts(self, ind, ts):
        self.blockSignals(True)
        ts_item = self.output_tw.item(ind, 3)
        try:
            ts_item.setText("{0:.3f}   ".format(ts))
        except ValueError:
            ts_item.setText("{0}".format(ts))
        self.blockSignals(False)

    def get_output_ts(self, ind):
        ts_item = self.output_tw.item(ind, 3)
        ts = ts_item.text().rstrip().lstrip()
        if len(ts):
            out = float(ts)
        else:
            out = ''
        return out

    def set_output_t_e_s(self, ind, tes):
        self.blockSignals(True)
        tes_item = self.output_tw.item(ind, 4)
        try:
            tes_item.setText("{0:.3f}   ".format(tes))
        except ValueError:
            tes_item.setText("{0}".format(tes))
        self.blockSignals(False)

    def get_output_t_e_s(self, ind):
        tes_item = self.output_tw.item(ind, 4)
        tes = tes_item.text().rstrip().lstrip()
        if len(tes):
            out = float(tes)
        else:
            out = ''
        return out


       ########################################################################################


    

class OutputMenuWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None, ctrls = [],params=[]):
        super().__init__(parent = parent)  

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setSpacing(7)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.save_btn = QtWidgets.QPushButton('Export table')
        #self._layout.addWidget(self.save_btn)

    

        self._layout.addSpacerItem(HorizontalSpacerItem())


        self.setLayout(self._layout)


