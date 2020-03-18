

from PyQt5.QtCore import pyqtSignal

from um.models.AFG3251 import AFG_AFG3251
from um.controllers.pv_controller import pvController

class AFGController(pvController):
    
    def __init__(self, parent, isMain = False, offline = False):

        visa_hostname='202'
        model = AFG_AFG3251(parent, visa_hostname=visa_hostname, offline = offline)
        super().__init__(parent, model, isMain)  
        self.panel_items =['instrument',
                      'function_shape',
                      'amplitude',
                      'duration',
                      'operating_mode',
                      'n_cycles',
                      'frequency',
                      'output_state']

        self.init_panel("Function generator", self.panel_items)

        
        
        if isMain:
            self.show_widget()
     

