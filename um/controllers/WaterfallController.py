

from PyQt5.QtCore import pyqtSignal
from um.models.WaterfallModel import WaterfallModel
from um.controllers.pv_controller import pvController
import time
from PyQt5.QtCore import QThread, pyqtSignal, QObject



class WaterfallController(pvController):
    waterfallUpdated = pyqtSignal()  
    
    def __init__(self, parent, isMain = False):
        model = WaterfallModel(parent)
        super().__init__(parent, model, isMain)  
        panel_items =[ 'scale' ]
        self.init_panel('Waterfall', panel_items)
        self.make_connections()

    def make_connections(self): 
        pass

    '''
        self.model.pvs['waveform_in'].value_changed_signal.connect(self.waveform_added_callback)

    def waveform_added_callback(self, tag, data):
        waweform_dict = data[0]
        files = list(self.model.scans[0].keys())
        print(files)'''

    ###########################################################
    ## other methods
    ###########################################################


    