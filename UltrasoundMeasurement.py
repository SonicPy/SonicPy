#TODO arb waveforms


import sys, platform
from PyQt5 import QtWidgets
from controllers.UltrasoundController import UltrasoundController
from PyQt5.QtWidgets import QApplication

_platform = platform.system()
Theme = 1

def main():
    app = QApplication([])
    app.aboutToQuit.connect(app.deleteLater)
    controller = UltrasoundController(app, _platform, Theme)
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

if __name__ == '__main__':
    main()