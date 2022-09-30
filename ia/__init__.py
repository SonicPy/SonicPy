# -*- coding: utf8 -*-
#
__version__ = "0.6.0"

import os
from pathlib import Path
import platform
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import pyqtgraph
import cv2

theme = 1

resources_path = os.path.join(os.path.dirname(__file__), 'resources')
calibrants_path = os.path.join(resources_path, 'calibrants')
icons_path = os.path.join(resources_path, 'icons')
data_path = os.path.join(resources_path, 'data')
style_path = os.path.join(resources_path, 'style')
title = "SonicPy: Travel-distance analysis. ver." + __version__ + "  © R. Hrubiak, 2022."
home_path = str(Path.home())



def main():
    from ia.controllers.ImageAnalysisController import ImageAnalysisController
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    _platform = platform.system()

    app = QtWidgets.QApplication([])
    #app.aboutToQuit.connect(app.deleteLater)
    
    controller = ImageAnalysisController(app = app, offline= True)
    controller.show_window()

    if _platform == "Darwin":    #macOs has a 'special' way of handling preferences menu
        window = controller.display_window
        pact = QtWidgets.QAction('Preferences', app)
        pact.triggered.connect(controller.preferences_module)
        pact.setMenuRole(QtWidgets.QAction.PreferencesRole)
        pmenu = QtWidgets.QMenu('Preferences')
        pmenu.addAction(pact)
        menu = window.menuBar
        menu.addMenu(pmenu)
    
    app.exec_()

