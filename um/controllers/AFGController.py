

from PyQt5.QtCore import pyqtSignal

from um.models.AFG3251 import AFG_AFG3251
from um.controllers.pv_controller import pvController

class AFGController(pvController):
    
    def __init__(self, parent, arb_controller, arb_filter_controller,  isMain = False, offline = False):

        visa_hostname='202'
        model = AFG_AFG3251(parent, visa_hostname=visa_hostname, offline = offline)
        super().__init__(parent, model, isMain)  

        self.arb_controller = arb_controller
        self.arb_filter_controller=arb_filter_controller

        self.panel_items =['instrument',
                      'function_shape',
                      'amplitude',
                      'duration',
                      'operating_mode',
                      'n_cycles',
                      'frequency',
                      'output_state',
                      'upload_user1_waveform',
                      'auto_upload_user1_waveform']

        self.init_panel("AFG", self.panel_items)

        
        
        if isMain:
            self.show_widget()

    '''def make_connections(self):
        # User waveform events
        self.arb_controller.waveformComputedSignal.connect(self.waveform_computed_callback)
        self.arb_filter_controller.waveformFilteredcallbackSignal.connect(self.waveform_filtered_callback)'''
     
    ####################################################
    ### Next is the User waveform handling
    ####################################################

    
     

