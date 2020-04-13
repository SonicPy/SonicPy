

from PyQt5.QtCore import pyqtSignal
from um.models.sweep_model import SweepModel
from um.controllers.pv_controller import pvController
import time
from PyQt5.QtCore import QThread, pyqtSignal, QObject



class SweepController(pvController):
    
    pointDoneSignal = pyqtSignal()  
    pointStartRequestSignal = pyqtSignal()  
    
    def __init__(self, parent, scope_pvs, source_waveform_pvs, isMain = False):
        
        model = SweepModel(parent)
        super().__init__(parent, model, isMain)  

        
        self.model.setpointSweepThread.scope_pvs = scope_pvs
        self.model.setpointSweepThread.source_waveform_pvs = source_waveform_pvs

        panel_items =[  'start_point',
                        'end_point',
                        'step',
                        'n',
                        'run_state']
        self.init_panel('Scan', panel_items)
        self.make_connections()

    def make_connections(self): 
        self.model.pvs['run_state'].value_changed_signal.connect(self.run_state_changed_callback)

    def run_state_changed_callback(self, tag, data):
        state = data[0]
        if state:
            self.pointStartRequestSignal.emit()
        else:
            
            self.pointDoneSignal.emit()

    def start_sweep(self):
        # here we do the setpoint sweep
        self.model.start_sweep()
            
    def stop_sweep(self):
        self.model.clear_queue()
        


    def received_sweep_data_callback(self, data):
        step = data['step']
        samples = data['n']
        point = data['point']
        waveform = data['waveform']
        self.model.add_waveform(waveform[0],waveform[1],point)
        #self.update_3d_plots()
        #self.show_latest_waveform()
        d_time = data['time']
        #print('step: ' + str(step) + ' samples: ' + str(samples) +' point: ' + str(point) + ' time: ' + str(d_time))
        progress = (int(step)+1)/int(samples) * 100
        self.progress_bar.setValue(progress)

    ###########################################################
    ## other methods
    ###########################################################

    def get_waveform(self):
        self.model.get_waveform(0)

    