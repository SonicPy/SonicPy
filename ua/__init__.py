
__version__ = "0.5.9"

import sys
import os

theme = 1

autoload = True

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
    #app.aboutToQuit.connect(app.deleteLater)
    
    controller = TimeOfFlightController(app = app)
    controller.show_window()

    if autoload:
        folder = ''
        #mac_folder = '/Users/hrubiak/Desktop/Aihaiti-e244302/sam2/US'
        win_folder = 'C:\\Users\\hrubiak\\Desktop\\US\\US'
        mac_folder = '/Users/hrubiak/Downloads/Ultrasound_XRD_datasets_for_dissemination/Ultrasound_data_for_dissemination_June_2018_Exp4/US'
        if os.path.isdir(mac_folder):
            folder = mac_folder
        if os.path.isdir(win_folder):
            folder = win_folder
        if len(folder):
            if os.path.isdir(folder):
                controller.overview_controller.set_US_folder(folder=folder)
    
    

    if _platform == "Darwin":    #macOs has a 'special' way of handling preferences menu
        window = controller.widget
        pact = QtWidgets.QAction('Preferences', app)
        pact.triggered.connect(controller.preferences_module)
        pact.setMenuRole(QtWidgets.QAction.PreferencesRole)
        pmenu = QtWidgets.QMenu('Preferences')
        pmenu.addAction(pact)
        
      
    return app.exec_()

