import platform, os

from PyQt5.QtWidgets import QApplication

from controllers.ScopeController import ScopeController

_platform = platform.system()



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

    controller = ScopeController(None,isMain=True)
    controller.show_widget()
    app.exec_()
    del app


if __name__ == '__main__':
    main()
