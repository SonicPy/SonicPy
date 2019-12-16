# -*- coding: utf8 -*-

# DISCLAIMER
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Principal author: R. Hrubiak (hrubiak@anl.gov)
# Copyright (C) 2018-2019 ANL, Lemont, USA

# Based on code from Dioptas - GUI program for fast processing of 2D X-ray diffraction data

""" Modifications:
    October 9, 2018 Ross Hrubiak
        - modified for use with MCA
        - support for energy dispersive mode
        - added 2th control
        - removed references to integration, pattern, calibration and possibly other stuff)
"""

from functools import partial

from PyQt5 import QtWidgets, QtCore

from widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight, HorizontalLine

class PhaseWidget(QtWidgets.QWidget):

    color_btn_clicked = QtCore.pyqtSignal(int, QtWidgets.QWidget)
    
    show_cb_state_changed = QtCore.pyqtSignal(int, bool)
    file_dragged_in = QtCore.pyqtSignal(list)

    vp_sb_value_changed = QtCore.Signal(int, float)
    vs_sb_value_changed = QtCore.Signal(int, float)
    d_sb_value_changed = QtCore.Signal(int, float)

    def __init__(self):
        super(PhaseWidget, self).__init__()
        
        self._layout = QtWidgets.QVBoxLayout()  
        self.setWindowTitle('Phase control')
        self.button_widget = QtWidgets.QWidget(self)
        self.button_widget.setObjectName('phase_control_button_widget')
        self._button_layout = QtWidgets.QHBoxLayout()
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        self._button_layout.setSpacing(6)

        self.add_btn = QtWidgets.QPushButton('Add')
        self.edit_btn = QtWidgets.QPushButton('Edit')
        self.delete_btn = QtWidgets.QPushButton('Delete')
        self.clear_btn = QtWidgets.QPushButton('Clear')
        #self.rois_btn = QtWidgets.QPushButton('Add ROIs')
        self.save_list_btn = QtWidgets.QPushButton('Save List')
        self.load_list_btn = QtWidgets.QPushButton('Load List')

        self._button_layout.addWidget(self.add_btn,0)
        #self._button_layout.addWidget(self.edit_btn,0)
        self._button_layout.addWidget(self.delete_btn,0)
        self._button_layout.addWidget(self.clear_btn,0)
        #self._button_layout.addWidget(self.rois_btn,0)
        self._button_layout.addWidget(VerticalLine())
        self._button_layout.addSpacerItem(HorizontalSpacerItem())
        self._button_layout.addWidget(VerticalLine())
        self._button_layout.addWidget(self.save_list_btn,0)
        self._button_layout.addWidget(self.load_list_btn,0)
        self.button_widget.setLayout(self._button_layout)
        self._layout.addWidget(self.button_widget)

        self.parameter_widget = QtWidgets.QWidget()

        self._parameter_layout = QtWidgets.QGridLayout()
        self.vp_sb = DoubleSpinBoxAlignRight()
        self.vs_sb = DoubleSpinBoxAlignRight()
        self.d_sb = DoubleSpinBoxAlignRight()
        self.vp_step_msb = DoubleMultiplySpinBoxAlignRight()
        self.vs_step_msb = DoubleMultiplySpinBoxAlignRight()
        self.d_step_msb = DoubleMultiplySpinBoxAlignRight()
        self.apply_to_all_cb = QtWidgets.QCheckBox('Apply to all phases')
        self.show_in_pattern_cb = QtWidgets.QCheckBox('Show in Pattern')        

        self._parameter_layout.addWidget(QtWidgets.QLabel('Parameter'), 0, 1)
        self._parameter_layout.addWidget(QtWidgets.QLabel('Step'), 0, 3)
        self._parameter_layout.addWidget(QtWidgets.QLabel('Vp:'), 1, 0)
        self._parameter_layout.addWidget(QtWidgets.QLabel('Vs:'), 2, 0)
        self._parameter_layout.addWidget(QtWidgets.QLabel('d:'), 3, 0)
        self._parameter_layout.addWidget(QtWidgets.QLabel('m/s'), 1, 2)
        self._parameter_layout.addWidget(QtWidgets.QLabel('m/s'), 2, 2)
        self._parameter_layout.addWidget(QtWidgets.QLabel('mm'), 3, 2)

        self._parameter_layout.addWidget(self.vp_sb, 1, 1)
        self._parameter_layout.addWidget(self.vp_step_msb, 1, 3)
        self._parameter_layout.addWidget(self.vs_sb, 2, 1)
        self._parameter_layout.addWidget(self.vs_step_msb, 2, 3)
        self._parameter_layout.addWidget(self.d_sb, 3, 1)
        self._parameter_layout.addWidget(self.d_step_msb, 3, 3)

        

        
        self.parameter_widget.setLayout(self._parameter_layout)

        self._body_layout = QtWidgets.QHBoxLayout()
        self.phase_tw = ListTableWidget(columns=6)
        self._body_layout.addWidget(self.phase_tw )
        self._body_layout.addWidget(self.parameter_widget, 0)


        self._layout.addLayout(self._body_layout)

        self.setLayout(self._layout)
        
        self.style_widgets()

        self.phase_show_cbs = []
        self.phase_color_btns = []
        #self.phase_roi_btns = [] #add ROIs (RH)
        self.show_parameter_in_pattern = True
        header_view = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, self.phase_tw)
        self.phase_tw.setHorizontalHeader(header_view)
        
        #header_view.setResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_view.setResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header_view.setResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header_view.setResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header_view.hide()
        self.phase_tw.setItemDelegate(NoRectDelegate())

        self.vp_sb.valueChanged.connect(self.vp_sb_changed)
        self.vs_sb.valueChanged.connect(self.vs_sb_changed)
        self.d_sb.valueChanged.connect(self.d_sb_changed)
     
        self.setAcceptDrops(True) 

    def vp_sb_changed(self):
        cur_ind = self.get_selected_phase_row()
        vp = self.vp_sb.value()
        self.vp_sb_value_changed.emit(cur_ind, vp)

    def vs_sb_changed(self):
        cur_ind = self.get_selected_phase_row()
        vs = self.vs_sb.value()
        self.vs_sb_value_changed.emit(cur_ind, vs)

    def d_sb_changed(self):
        cur_ind = self.get_selected_phase_row()
        d = self.d_sb.value()
        self.d_sb_value_changed.emit(cur_ind, d)

    def set_vp_sb(self, value):
        self.blockSignals(True)
        self.vp_sb.setValue(value)
        self.blockSignals(False)

    def set_vs_sb(self, value):
        self.blockSignals(True)
        self.vs_sb.setValue(value)
        self.blockSignals(False)

    def set_d_sb(self, value):
        self.blockSignals(True)
        self.d_sb.setValue(value)
        self.blockSignals(False)

    def style_widgets(self):
        self.phase_tw.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.parameter_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.phase_tw.setMinimumHeight(120)
        self.phase_tw.setMinimumWidth(500)

        self.vs_step_msb.setMaximumWidth(75)
        self.vp_step_msb.setMaximumWidth(75)
        self.d_step_msb.setMaximumWidth(75)
        
       
        self.vp_sb.setMinimumWidth(100)

        self.vp_sb.setMaximum(9999999)
        self.vp_sb.setMinimum(0)
        self.vp_sb.setValue(5000)

        self.vp_step_msb.setMaximum(1000.0)
        self.vp_step_msb.setMinimum(1.0)
        self.vp_step_msb.setValue(50)

        self.vs_sb.setMaximum(99999999)
        self.vs_sb.setMinimum(0)
        self.vs_sb.setValue(3000)

        self.vs_step_msb.setMaximum(1000.0)
        self.vs_step_msb.setMinimum(1.0)
        self.vs_step_msb.setValue(50)

        self.d_sb.setMaximum(1000)
        self.d_sb.setMinimum(0)
        self.d_sb.setValue(1)

        self.d_step_msb.setMaximum(1.0)
        self.d_step_msb.setMinimum(0.0001)
        self.d_step_msb.setValue(0.05)

        

        self.setStyleSheet("""
            #phase_control_button_widget QPushButton {
                min-width: 70;
            }
        """)

        self.apply_to_all_cb.setChecked(False)
        self.show_in_pattern_cb.setChecked(True)

    # ###############################################################################################
    # Now comes all the phase tw stuff
    ################################################################################################

    def add_phase(self, name, color):
        self.phase_tw.blockSignals(True)
        current_rows = self.phase_tw.rowCount()
        self.phase_tw.setRowCount(current_rows + 1)
        

        show_cb = QtWidgets.QCheckBox()
        show_cb.setChecked(True)
        show_cb.stateChanged.connect(partial(self.phase_show_cb_changed, show_cb))
        show_cb.setStyleSheet("background-color: transparent")
        self.phase_tw.setCellWidget(current_rows, 0, show_cb)
        self.phase_show_cbs.append(show_cb)

        

        color_button = FlatButton()
        color_button.setStyleSheet("background-color: " + color)
        color_button.clicked.connect(partial(self.phase_color_btn_click, color_button))
        self.phase_tw.setCellWidget(current_rows, 1, color_button)
        self.phase_color_btns.append(color_button)

        name_item = QtWidgets.QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
        name_item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.phase_tw.setItem(current_rows, 2, name_item)

        vp_item = QtWidgets.QTableWidgetItem('5000 m/s')
        vp_item.setFlags(vp_item.flags() & ~QtCore.Qt.ItemIsEditable)
        vp_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.phase_tw.setItem(current_rows, 3, vp_item)

        vs_item = QtWidgets.QTableWidgetItem('3000 m/s')
        vs_item.setFlags(vs_item.flags() & ~QtCore.Qt.ItemIsEditable)
        vs_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.phase_tw.setItem(current_rows, 4, vs_item)

        d_item = QtWidgets.QTableWidgetItem('10 mm')
        d_item.setFlags(d_item.flags() & ~QtCore.Qt.ItemIsEditable)
        d_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.phase_tw.setItem(current_rows, 5, d_item)

        self.phase_tw.setColumnWidth(0, 35)
        self.phase_tw.setColumnWidth(1, 25)
        self.phase_tw.setRowHeight(current_rows, 25)
        self.select_phase(current_rows)
        self.phase_tw.blockSignals(False)



    def select_phase(self, ind):
        self.phase_tw.selectRow(ind)

    def get_selected_phase_row(self):
        selected = self.phase_tw.selectionModel().selectedRows()
        try:
            row = selected[0].row()
        except IndexError:
            row = -1
        return row

    def get_phase(self):
        pass

    def del_phase(self, ind):
        self.phase_tw.blockSignals(True)
        self.phase_tw.removeRow(ind)
        self.phase_tw.blockSignals(False)
        del self.phase_show_cbs[ind]
        del self.phase_color_btns[ind]

        if self.phase_tw.rowCount() > ind:
            self.select_phase(ind)
        else:
            self.select_phase(self.phase_tw.rowCount() - 1)
    
    def rename_phase(self, ind, name):
        name_item = self.phase_tw.item(ind, 2)
        name_item.setText(name)

    def set_phase_vs(self, ind, vs):
        self.blockSignals(True)
        vs_item = self.phase_tw.item(ind, 4)
        try:
            vs_item.setText("{0:.2f} m/s".format(vs))
        except ValueError:
            vs_item.setText("{0} m/s".format(vs))
        self.blockSignals(False)

    def get_phase_vs(self, ind):
        vs_item = self.phase_tw.item(ind, 4)
        try:
            vs = float(str(vs_item.text()).split()[0])
        except:
            vs = None
        return vs

    def set_phase_vp(self, ind, vp):
        self.blockSignals(True)
        vp_item = self.phase_tw.item(ind, 3)
        try:
            vp_item.setText("{0:.2f} m/s".format(vp))
        except ValueError:
            vp_item.setText("{0} m/s".format(vp))
        self.blockSignals(False)

    def get_phase_vp(self, ind):
        vp_item = self.phase_tw.item(ind, 3)
        vp = float(str(vp_item.text()).split()[0])
        return vp

    def set_phase_d(self, ind, d):
        self.blockSignals(True)
        d_item = self.phase_tw.item(ind, 5)
        try:
            d_item.setText("{0:.4f} mm".format(d))
        except ValueError:
            d_item.setText("{0} mm".format(d))
        self.blockSignals(False)

    def get_phase_d(self, ind):
        d_item = self.phase_tw.item(ind, 5)
        try:
            d = float(str(d_item.text()).split()[0])
        except:
            d = None
        return d

    def phase_color_btn_click(self, button):
        self.color_btn_clicked.emit(self.phase_color_btns.index(button), button)
        
    def phase_show_cb_changed(self, checkbox):
        self.show_cb_state_changed.emit(self.phase_show_cbs.index(checkbox), checkbox.isChecked())

    def phase_show_cb_set_checked(self, ind, state):
        checkbox = self.phase_show_cbs[ind]
        checkbox.setChecked(state)

    def phase_show_cb_is_checked(self, ind):
        checkbox = self.phase_show_cbs[ind]
        return checkbox.isChecked()

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()


        ########################################################################################

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """
        Drop files directly onto the widget

        File locations are stored in fname
        :param e:
        :return:
        """
        if e.mimeData().hasUrls:
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            fnames = list()
            for url in e.mimeData().urls():
                fname = str(url.toLocalFile())  
                fnames.append(fname)
            self.file_dragged_in.emit(fnames)
        else:
            e.ignore() 