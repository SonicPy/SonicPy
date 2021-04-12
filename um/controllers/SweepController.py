

from PyQt5.QtCore import pyqtSignal
from um.models.sweep_model import SweepModel
from um.controllers.pv_controller import pvController
import time
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from um.models.pvServer import pvServer


class SweepController(pvController):
    
    scanDoneSignal = pyqtSignal()  
    scanStartRequestSignal = pyqtSignal()  
    
    def __init__(self, parent, scope_pvs, source_waveform_pvs, isMain = False):
        
        model = SweepModel(parent)
        super().__init__(parent, model, isMain)  
        self.pv_server = pvServer()
        
        self.model.setpointSweepThread.scope_pvs = scope_pvs
        self.model.setpointSweepThread.source_waveform_pvs = source_waveform_pvs

        panel_items =[  
                        #'positioner_set_channel',
                        #'positioner_read_channel',
                        #'det_trigger_channel',
                        #'det_run_state_channel',
                        #'save_data_set_channel',
                        #'save_data_read_channel',
                        'start_point',
                        'end_point',
                        'step',
                        'n',
                        'current_point',
                        'setpoint',
                        'scan_go']
        self.init_panel('Scan', panel_items)


        self.make_connections()



    def make_connections(self): 
        self.model.pvs['scan_go'].value_changed_signal.connect(self.run_state_changed_callback)

    def run_state_changed_callback(self, tag, data):
        state = data[0]
        if state:

            #temperary code to clear the waterfall plot before scanning
            #replace with better handling of growing waterfall data in the future
            waterfall_clear_pv = self.pv_server.get_pv('Waterfall:clear')
            waterfall_clear_pv.set(True)
            self.scanStartRequestSignal.emit()
        else:
            self.model.stop_scan()
            self.scanDoneSignal.emit()

    def start_sweep(self):
        # here we do the setpoint sweep
        self.model.start_sweep()
            
    def stop_sweep(self):
        self.model.clear_queue()
        



    ###########################################################
    ## other methods
    ###########################################################

    