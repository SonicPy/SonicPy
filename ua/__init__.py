
__version__ = "0.5.0"

import sys
import os

theme = 1

resources_path = os.path.join(os.path.dirname(__file__), 'resources')
calibrants_path = os.path.join(resources_path, 'calibrants')
icons_path = os.path.join(resources_path, 'icons')
data_path = os.path.join(resources_path, 'data')
style_path = os.path.join(resources_path, 'style')
from pathlib import Path
home_path = str(Path.home())

import platform
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import pyqtgraph

def main():
    from ua.controllers.UltrasoundAnalysisController import UltrasoundAnalysisController
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    _platform = platform.system()

    app = QtWidgets.QApplication([])
    app.aboutToQuit.connect(app.deleteLater)
    
    controller = UltrasoundAnalysisController(app = app, offline= True)
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
    
    return app.exec_()

    '''def arrow_plot():
    from ua.controllers.ArrowPlotController import ArrowPlotController
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    _platform = platform.system()

    app = QtWidgets.QApplication([])
    app.aboutToQuit.connect(app.deleteLater)
    
    controller = ArrowPlotController(app = app)
    controller.show_window()'''
    '''
    controller.update_data( filenames=
                            ['resources/ultrasonic/4000psi-300K_+15MHz000.csv.json',
                            'resources/ultrasonic/4000psi-300K_+18MHz000.csv.json',
                            'resources/ultrasonic/4000psi-300K_+20MHz000.csv.json',
                            'resources/ultrasonic/4000psi-300K_+21MHz000.csv.json',
                            'resources/ultrasonic/4000psi-300K_+24MHz000.csv.json',
                            'resources/ultrasonic/4000psi-300K_+25MHz000.csv.json',
                            'resources/ultrasonic/4000psi-300K_+27MHz000.csv.json',
                            'resources/ultrasonic/4000psi-300K_+30MHz000.csv.json',
                            'resources/ultrasonic/4000psi-300K_+33MHz000.csv.json',
                            'resources/ultrasonic/4000psi-300K_+36MHz000.csv.json',
                            'resources/ultrasonic/4000psi-300K_+39MHz000.csv.json',
                            'resources/ultrasonic/4000psi-300K_+42MHz000.csv.json']
                            )                            
    
    
    return app.exec_()
    '''