
from PyQt5.QtWidgets import QApplication
import os, os.path, sys, platform, copy
from controllers.AFGController import AFGController

_platform = platform.system()
Theme = 1

def main():
    app = QApplication([])
    app.aboutToQuit.connect(app.deleteLater)
    Theme = 1
    if Theme ==1:
        WStyle = 'plastique'
        file = open(os.path.join('resources', "stylesheet.qss"))
        stylesheet = file.read()
        app.setStyleSheet(stylesheet)
        file.close()
        app.setStyle(WStyle)
    else:
        WStyle = "windowsvista"
        app.setStyleSheet(" ")
        app.setStyle(WStyle)
    isMain = True
    controller = AFGController(None,isMain)
    
    app.exec_()
    del app

if __name__ == '__main__':
    main()