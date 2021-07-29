
__version__ = "0.5.0"

import sys
import os


resources_path = os.path.join(os.path.dirname(__file__), 'resources')
calibrants_path = os.path.join(resources_path, 'calibrants')
icons_path = os.path.join(resources_path, 'icons')
data_path = os.path.join(resources_path, 'data')
style_path = os.path.join(resources_path, 'style')
env_path = os.path.join(resources_path, 'catch1d.env')
autosave_settings_path = os.path.join(resources_path, 'pv','autosave.json')
autosave_data_path = os.path.join(resources_path, 'pv','saved')

from pathlib import Path
home_path = str(Path.home())

import platform
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import pyqtgraph


def main(offline= True):
    from um.controllers.UltrasoundController import UltrasoundController
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    _platform = platform.system()
    Theme = 1
    app = QtWidgets.QApplication([])
    app.aboutToQuit.connect(app.deleteLater)
    controller = UltrasoundController(app, _platform, Theme, offline= offline )
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
    #del app
