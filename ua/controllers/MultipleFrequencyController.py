#!/usr/bin/env python

import os
from PyQt5.QtCore import QObject, pyqtSignal
from ua.models.MultipleFrequenciesModel import MultipleFrequenciesModel
from ua.models.EchoesResultsModel import EchoesResultsModel
from ua.widgets.MultipleFrequenciesWidget import MultipleFrequenciesWidget

############################################################

class MultipleFrequencyController(QObject):

    
    def __init__(self, app=None, results_model= EchoesResultsModel()):
        super().__init__()
        
        self.model = MultipleFrequenciesModel(results_model)

        self.widget = MultipleFrequenciesWidget()

        if app is not None:
            self.setStyle(app)
        
    def make_connections(self): 
        
        pass


    def setStyle(self, app):
        from .. import theme 
        from .. import style_path
        self.app = app
        if theme==1:
            WStyle = 'plastique'
            file = open(os.path.join(style_path, "stylesheet.qss"))
            stylesheet = file.read()
            self.app.setStyleSheet(stylesheet)
            file.close()
            self.app.setStyle(WStyle)
        else:
            WStyle = "windowsvista"
            self.app.setStyleSheet(" ")
            #self.app.setPalette(self.win_palette)
            self.app.setStyle(WStyle)