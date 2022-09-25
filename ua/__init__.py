# -*- coding: utf8 -*-
__version__ = "0.6.0"

import sys
import os
from pathlib import Path
import platform
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import pyqtgraph

theme = 1
autoload = True

resources_path = os.path.join(os.path.dirname(__file__), 'resources')
calibrants_path = os.path.join(resources_path, 'calibrants')
icons_path = os.path.join(resources_path, 'icons')
data_path = os.path.join(resources_path, 'data')
style_path = os.path.join(resources_path, 'style')
title = "SonicPy: Time-of-flight analysis. ver." + __version__ + "  © R. Hrubiak, 2022."
home_path = str(Path.home())

def main():
    from ua.controllers.UltrasoundAnalysisController import UltrasoundAnalysisController
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    _platform = platform.system()
    app = QtWidgets.QApplication([])
    controller = UltrasoundAnalysisController(app = app)
    controller.display_window.show()
    if _platform == "Darwin":    #macOs has a 'special' way of handling preferences menu
        window = controller.display_window
        pact = QtWidgets.QAction('Preferences', app)
        pact.triggered.connect(controller.preferences_module)
        pact.setMenuRole(QtWidgets.QAction.PreferencesRole)
        pmenu = QtWidgets.QMenu('Preferences')
        pmenu.addAction(pact)
    return app.exec_()


def TOF():
    from ua.controllers.TimeOfFlightController import TimeOfFlightController
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    _platform = platform.system()
    app = QtWidgets.QApplication([])
    controller = TimeOfFlightController(app = app)
    controller.show_window()

    if autoload:
        fname = ''
        mac_file = '/Users/ross/Globus/s16bmb-20210717-e244302-Aihaiti/sam3/US/myproject.bz'
        win_file = "C:\\Users\\hrubiak\\Desktop\\Ultrasound_XRD_datasets_for_dissemination\\Ultrasound_data_for_dissemination_June_2018_Exp4\\Gaussian\\myproject.bz"
        mac_file_2 = '/Users/hrubiak/Downloads/Ultrasound_XRD_datasets_for_dissemination/Ultrasound_data_for_dissemination_June_2018_Exp4/Gaussian/myproject.bz'
        possible_files = [mac_file,
                            win_file,
                            mac_file_2]
        for f in possible_files:
            if os.path.isfile(f):
                fname = f
                break
        if len(fname):
            if os.path.isfile(fname):
                controller._open_project(filename=fname)
    
    if _platform == "Darwin":    #macOs has a 'special' way of handling preferences menu
        window = controller.widget
        pact = QtWidgets.QAction('Preferences', app)
        pact.triggered.connect(controller.preferences_module)
        pact.setMenuRole(QtWidgets.QAction.PreferencesRole)
        pmenu = QtWidgets.QMenu('Preferences')
        pmenu.addAction(pact)
    return app.exec_()

