
__version__ = "0.5.0"

import sys
import os


resources_path = os.path.join(os.path.dirname(__file__), 'resources')
calibrants_path = os.path.join(resources_path, 'calibrants')
icons_path = os.path.join(resources_path, 'icons')
data_path = os.path.join(resources_path, 'data')
style_path = os.path.join(resources_path, 'style')


import platform
from PyQt5 import QtWidgets
from ua.controllers.UltrasoundAnalysisController import UltrasoundAnalysisController
from PyQt5.QtWidgets import QApplication



def main():

    _platform = platform.system()
    Theme = 1
    app = QApplication([])
    app.aboutToQuit.connect(app.deleteLater)
    controller = UltrasoundAnalysisController(app, _platform, Theme, offline= True)
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
    del app