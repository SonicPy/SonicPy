# -*- coding: utf8 -*-
# Dioptas - GUI program for fast processing of 2D X-ray data
# Copyright (C) 2017  Clemens Prescher (clemens.prescher@gmail.com)
# Institute for Geology and Mineralogy, University of Cologne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtCore, QtWidgets, QtGui
import os
from um.widgets.CustomWidgets import FlatButton, CleanLooksComboBox 
import copy

#from .. import style_path

class selectDetectorDialog(QtWidgets.QDialog):
    """
    Dialog which is asking for Intensity Cutoff and minimum d-spacing when loading cif files.
    """

    def __init__(self,n_detectors=1):
        super().__init__()

        self.unit_opts = {'detector':
                                        ["Detector:",
                                        map(str, list(range(n_detectors))),
                                        "Select which detector to display.",
                                        '']
                                        }
        opts = self.unit_opts['detector']
        #self._parent = parent
        self._create_widgets(opts)
        self._layout_widgets()
        self._style_widgets()
        self._connect_widgets()

    def _create_widgets(self,opts):
        """
        Creates all necessary widgets.
        """
        self.detetor_lbl = QtWidgets.QLabel(opts[0])
        self.detetor_txt = CleanLooksComboBox()
        self.detetor_txt.addItems(opts[1])
        self.detetor_txt.setToolTip(opts[2])
        self.detetor_unit_lbl = QtWidgets.QLabel(opts[3])
        self.ok_btn = FlatButton("OK")

    def _layout_widgets(self):
        """
        Layouts the widgets into a gridlayout
        """
        self._layout = QtWidgets.QGridLayout()
        self._layout.addWidget(self.detetor_lbl, 0, 0)
        self._layout.addWidget(self.detetor_txt, 0, 1)
        self._layout.addWidget(self.detetor_unit_lbl, 0, 2)
        self._layout.addWidget(self.ok_btn, 2, 1, 1, 2)
        self.setLayout(self._layout)

    def _style_widgets(self):
        """
        Makes everything pretty and set Double validators for the line edits.
        """
        self.detetor_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        #self.detetor_txt.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.detetor_txt.setMaximumWidth(100)
        #self.detetor_txt.setValidator(QtGui.QIntValidator())
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def _connect_widgets(self):
        """
        Connecting actions to slots.
        """
        self.ok_btn.clicked.connect(self.button_press)

    def button_press(self, button):
        self.out = int(str(self.detetor_txt.currentText()))
        self.close()

    @classmethod
    def showDialog(cls,n_detectors):
        dialog = cls(n_detectors)
        dialog.exec_()
        out = copy.deepcopy(dialog.out)
        dialog.deleteLater()
        return out

class xyPatternParametersDialog(QtWidgets.QDialog):
    """
    Dialog which is asking for Intensity Cutoff and minimum d-spacing when loading cif files.
    """

    def __init__(self,filename,unit,value):
        super().__init__()

        self.unit_opts = {'wavelength':
                                        ["X-ray Wavelength for "+filename+":",
                                        str(value),
                                        "Enter the x-ray wavelength corresponding to the file "+filename+".",
                                        f'\N{LATIN CAPITAL LETTER A WITH RING ABOVE}'],
                          'tth':
                                        ["Detector "+ f'2\N{GREEK SMALL LETTER THETA}'+" for "+filename+":",
                                        str(value),
                                        "Enter the detector "+f'2\N{GREEK SMALL LETTER THETA}'+" corresponding to the file "+filename+".",
                                        "degrees"]              }
        opts = self.unit_opts[unit]
        #self._parent = parent
        self._create_widgets(opts)
        self._layout_widgets()
        self._style_widgets()
        self._connect_widgets()

    def _create_widgets(self,opts):
        """
        Creates all necessary widgets.
        """
        self.xray_wavelength_lbl = QtWidgets.QLabel(opts[0])
        self.xray_wavelength_txt = QtWidgets.QLineEdit(opts[1])
        self.xray_wavelength_txt.setToolTip(opts[2])
        self.xray_wavelength_unit_lbl = QtWidgets.QLabel(opts[3])
        self.ok_btn = FlatButton("OK")

    def _layout_widgets(self):
        """
        Layouts the widgets into a gridlayout
        """
        self._layout = QtWidgets.QGridLayout()
        self._layout.addWidget(self.xray_wavelength_lbl, 0, 0)
        self._layout.addWidget(self.xray_wavelength_txt, 0, 1)
        self._layout.addWidget(self.xray_wavelength_unit_lbl, 0, 2)
        self._layout.addWidget(self.ok_btn, 2, 1, 1, 2)
        self.setLayout(self._layout)

    def _style_widgets(self):
        """
        Makes everything pretty and set Double validators for the line edits.
        """
        self.xray_wavelength_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.xray_wavelength_txt.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.xray_wavelength_txt.setMaximumWidth(100)
        self.xray_wavelength_txt.setValidator(QtGui.QDoubleValidator())
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def _connect_widgets(self):
        """
        Connecting actions to slots.
        """
        self.ok_btn.clicked.connect(self.button_press)

    def button_press(self, button):
        self.out = float(str(self.xray_wavelength_txt.text()))
        self.close()

    @classmethod
    def showDialog(cls,filename,unit,value):
        dialog = cls(filename,unit,value)
        dialog.exec_()
        out = copy.deepcopy(dialog.out)
        dialog.deleteLater()
        return out

class CifConversionParametersDialog(QtWidgets.QDialog):
    """
    Dialog which is asking for Intensity Cutoff and minimum d-spacing when loading cif files.
    """

    def __init__(self):
        super(CifConversionParametersDialog, self).__init__()

        #self._parent = parent
        self._create_widgets()
        self._layout_widgets()
        self._style_widgets()

        self._connect_widgets()

    def _create_widgets(self):
        """
        Creates all necessary widgets.
        """
        self.int_cutoff_lbl = QtWidgets.QLabel("Intensity Cutoff:")
        self.min_d_spacing_lbl = QtWidgets.QLabel("Minimum d-spacing:")

        self.int_cutoff_txt = QtWidgets.QLineEdit("0.5")
        self.int_cutoff_txt.setToolTip("Reflections with lower Intensity won't be considered.")
        self.min_d_spacing_txt = QtWidgets.QLineEdit("0.5")
        self.min_d_spacing_txt.setToolTip("Reflections with smaller d_spacing won't be considered.")

        self.int_cutoff_unit_lbl = QtWidgets.QLabel("%")
        self.min_d_spacing_unit_lbl = QtWidgets.QLabel("A")

        self.ok_btn = FlatButton("OK")

    def _layout_widgets(self):
        """
        Layouts the widgets into a gridlayout
        """
        self._layout = QtWidgets.QGridLayout()
        self._layout.addWidget(self.int_cutoff_lbl, 0, 0)
        self._layout.addWidget(self.int_cutoff_txt, 0, 1)
        self._layout.addWidget(self.int_cutoff_unit_lbl, 0, 2)
        self._layout.addWidget(self.min_d_spacing_lbl, 1, 0)
        self._layout.addWidget(self.min_d_spacing_txt, 1, 1)
        self._layout.addWidget(self.min_d_spacing_unit_lbl, 1, 2)
        self._layout.addWidget(self.ok_btn, 2, 1, 1, 2)

        self.setLayout(self._layout)

    def _style_widgets(self):
        """
        Makes everything pretty and set Double validators for the line edits.
        """
        self.int_cutoff_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.int_cutoff_txt.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.int_cutoff_txt.setMaximumWidth(40)
        self.min_d_spacing_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.min_d_spacing_txt.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.min_d_spacing_txt.setMaximumWidth(40)

        self.int_cutoff_txt.setValidator(QtGui.QDoubleValidator())
        self.min_d_spacing_txt.setValidator(QtGui.QDoubleValidator())

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        #file = open("stylesheet.qss")
        #stylesheet = file.read()
        #self.setStyleSheet(stylesheet)
        #file.close()

    def _connect_widgets(self):
        """
        Connecting actions to slots.
        """
        self.ok_btn.clicked.connect(self.accept)

    @property
    def int_cutoff(self):
        """
        Returns the intensity cutoff selected in the dialog.
        """
        return float(str(self.int_cutoff_txt.text()))

    @property
    def min_d_spacing(self):
        """
        Returns the minimum d-spacing selected in the dialog.
        """
        return float(str(self.min_d_spacing_txt.text()))

    def exec_(self):
        """
        Overwriting the dialog exec_ function to center the widget in the parent window before execution.
        """
        #parent_center = self._parent.window().mapToGlobal(self._parent.window().rect().center())
        #self.move(parent_center.x() - 101, parent_center.y() - 48)
        super(CifConversionParametersDialog, self).exec_()


class FileInfoWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(FileInfoWidget, self).__init__(parent)
        self.setWindowTitle("File Info")

        self.text_lbl = QtWidgets.QLabel()
        self.text_lbl.setWordWrap(True)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(5, 5, 5, 5)
        self._layout.addWidget(self.text_lbl)
        self._layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.setStyleSheet(
            """
            QWidget{
                background: rgb(0,0,0);
            }
            QLabel{
                color: #00DD00;
            }"""
        )
        self.setLayout(self._layout)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setAttribute(QtCore.Qt.WA_MacAlwaysShowToolWindow)

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()


class ErrorMessageBox(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(ErrorMessageBox, self).__init__(*args, **kwargs)
        self.setWindowTitle("OOOPS! An error occurred!")

        self.text_lbl = QtWidgets.QLabel()
        self.text_lbl.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.scroll_area = QtWidgets.QScrollArea()

        self.scroll_area.setWidget(self.text_lbl)
        self.scroll_area.setWidgetResizable(True)
        self.ok_btn = QtWidgets.QPushButton('OK')

        _layout = QtWidgets.QGridLayout()
        _layout.addWidget(self.scroll_area, 0, 0, 1, 10)
        _layout.addWidget(self.ok_btn, 1, 9)

        self.setLayout(_layout)
        self.ok_btn.clicked.connect(self.close)

    def setText(self, text_str):
        self.text_lbl.setText(text_str)


def open_file_dialog(parent_widget, caption, directory=None, filter=None):
    filename = QtWidgets.QFileDialog.getOpenFileName(parent_widget, caption=caption,
                                                     directory=directory,
                                                     filter=filter)
    if isinstance(filename, tuple):  # PyQt5 returns a tuple...
        return str(filename[0])
    return str(filename)


def open_files_dialog(parent_widget, caption, directory=None, filter=None):
    filenames = QtWidgets.QFileDialog.getOpenFileNames(parent_widget, caption=caption,
                                                       directory=directory,
                                                       filter=filter)
    if isinstance(filenames, tuple):  # PyQt5 returns a tuple...
        filenames = filenames[0]
    return filenames


def save_file_dialog(parent_widget, caption, directory=None, filter=None, warn_overwrite = True):
    if not warn_overwrite:
        opt = QtWidgets.QFileDialog.DontConfirmOverwrite
        filename = QtWidgets.QFileDialog.getSaveFileName(parent_widget, caption,
                                                     directory=directory,
                                                     filter=filter, options =opt)
    else: 
        
        filename = QtWidgets.QFileDialog.getSaveFileName(parent_widget, caption,
                                                     directory=directory,
                                                     filter=filter)
    if isinstance(filename, tuple):  # PyQt5 returns a tuple...
        return str(filename[0])
    return str(filename)
