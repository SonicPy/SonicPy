
from um.models.arb_filters import my_filter, no_filter

from PyQt5.QtCore import QThread, pyqtSignal
from um.models.pv_model import pvModel
from um.controllers.pv_controller import pvController

class no_filter_controller(pvController):
    def __init__(self, parent, isMain = False):
        model = no_filter_model(parent)
        super().__init__(parent, model, isMain)  
        self.panel_items =[
                      'apply']
        self.init_panel("No filter", self.panel_items)
        if isMain:
            self.show_widget()

class no_filter_model(pvModel):
    model_value_changed_signal = pyqtSignal(dict)
    def __init__(self, parent):
        super().__init__(parent)
        self.offline = True
        ## model speficic:
        self.instrument = 'no_filter'
        self.param = {  'name': 'No filter',
                        'reference':'',
                        'comment':''}
        
        # Task description markup. Aarbitrary default values ('val') are for type recognition in panel widget constructor
        # supported types are float, int, bool, string, and list of strings
        self.tasks = {  'waveform_in':
                                {'desc': 'Waveform IN', 'val':{}, 
                                'methods':{'set':True, 'get':False}, 
                                'param':{'tag':'user1_waveform','type':'dict'}},
                        'waveform_out':
                                {'desc': 'Waveform OUT', 'val':{}, 
                                'methods':{'set':True, 'get':False}, 
                                'param':{'tag':'user1_waveform','type':'dict'}},
                        'apply':     
                                {'desc': ';Apply', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'apply','type':'b'}},
                                }

        self.create_pvs(self.tasks)
        
        self.start()

    def compute_waveform(self):
        func = no_filter
        settings = self.get_settings(['waveform_in'])[self.settings_file_tag]
        print(settings)
        ans = func(settings)
        self.pvs['waveform_out'].set(ans)
       

    def _set_apply(self, val):
        if val:
            self.compute_waveform()
            self.pvs['apply'].set(False)


class arb_filter():
      def __init__(self):
            self.name = ''
            self.param = {  }
            self.func = None

      def get_params(self):
            return self.param



class fltr_none(arb_filter):
      def __init__(self):
            self.name = 'none'
            self.func = lambda x: x 
            self.param = {
                        'name': 'No filter',
                        'reference':'',
                        'comment':'',
                        'params':{ 
                        }}

class fltr_tukey(arb_filter):
      def __init__(self):
            self.name = 'fltr_tukey'
            self.func = my_filter
            self.param = {
                        'name': 'Tukey',
                        'reference':'',
                        'comment':u'The Tukey window, also known as the cosine-tapered window, can be regarded as a cosine lobe of width α(N + 1)/2 that is convolved with a rectangular window of width (1 − α/2)(N + 1)',
                        'params':{ 
                        'alpha':      {'symbol':u'α',
                                     'desc':u'At α = 0 it becomes rectangular, and at α = 1 it becomes a Hann window',
                                     'unit':'',
                                     'val':.1}
                        }}

class fltr_lowpass(arb_filter):
      def __init__(self):
            self.name = 'fltr_lowpass'
            self.func = my_filter
            self.param = {
                        'name': 'Lowpass',
                        'reference':'',
                        'comment':u'',
                        'params':{ 
                        'f_lowcut':  {'symbol':u'f<sub>L</sub>',
                                     'desc':u'Low-cut frequency',
                                     'unit':'Hz',
                                     'val':30e6}
                        }}

