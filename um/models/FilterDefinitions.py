
from um.models.arb_filters import my_filter, no_filter, tukey_filter

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
        # supported types are float, int, bool, string, list of strings, dict
        self.tasks = {  'waveform_in':
                                {'desc': 'Waveform IN', 'val':{}, 
                                'methods':{'set':True, 'get':False}, 
                                'param':{'tag':'waveform_in','type':'dict'}},
                        'waveform_out':
                                {'desc': 'Waveform OUT', 'val':{}, 
                                'methods':{'set':True, 'get':False}, 
                                'param':{'tag':'waveform_out','type':'dict'}},
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
        #print (ans)
        self.pvs['waveform_out'].set(ans)
       

    def _set_apply(self, val):
        if val:
            self.compute_waveform()
            self.pvs['apply'].set(False)

class tukey_filter_controller(pvController):
    def __init__(self, parent, isMain = False):
        model = tukey_filter_model(parent)
        super().__init__(parent, model, isMain)  
        self.panel_items =['alpha',
                      'apply']
        self.init_panel("Tukey", self.panel_items)
        if isMain:
            self.show_widget()

class tukey_filter_model(pvModel):
    model_value_changed_signal = pyqtSignal(dict)
    def __init__(self, parent):
        super().__init__(parent)
        self.offline = True
        ## model speficic:
        self.instrument = 'tukey_filter'
        self.param = {  'name': 'Tukey filter',
                        'reference':'',
                        'comment':''}
        
        # Task description markup. Aarbitrary default values ('val') are for type recognition in panel widget constructor
        # supported types are float, int, bool, string, and list of strings
        self.tasks = {  'waveform_in':
                                {'desc': 'Waveform IN', 'val':{}, 
                                'methods':{'set':True, 'get':False}, 
                                'param':{'tag':'waveform_in','type':'dict'}},
                        'waveform_out':
                                {'desc': 'Waveform OUT', 'val':{}, 
                                'methods':{'set':True, 'get':False}, 
                                'param':{'tag':'waveform_out','type':'dict'}},
                        'alpha':{'symbol':u'α',
                                'desc':u'α',
                                'unit':u'',
                                'val':0.1, 
                                'increment':0.05,'min':0,'max':1 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'alpha','type':'f'}},
                        'apply':     
                                {'desc': ';Apply', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'apply','type':'b'}},
                                }

        self.create_pvs(self.tasks)
        
        self.start()

    def compute_waveform(self):
        func = tukey_filter
        settings = self.get_settings(['waveform_in','alpha'])[self.settings_file_tag]
        print(settings)
        ans = func(settings)
        #print(ans)
        self.pvs['waveform_out'].set(ans)
       

    def _set_apply(self, val):
        if val:
            self.compute_waveform()
            self.pvs['apply'].set(False)

