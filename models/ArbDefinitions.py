from models.arb_waveforms import gaussian_wavelet
from PyQt5.QtCore import QThread, pyqtSignal
from models.pv_model import pvModel
from controllers.pv_controller import pvController


class arb_waveform():
    def __init__(self):
        self.name = ''
        self.param = {  }
        self.func = None

    def get_arb(self):
        func_param = {}
        for p in self.param['params']:
            val = self.param['params'][p]['val']
            func_param[p] = val

        if self.func is not None:

            ans = self.func(func_param)
            return ans 

    def get_params(self):
        return self.param

class g_wavelet_controller(pvController):
    def __init__(self, parent, isMain = False):
        model = g_wavelet_model(parent)
        super().__init__(parent, model, isMain)  
        self.panel_items =['t_min',
                      't_max',
                      'center_f',
                      'sigma']
        self.init_panel("Gaussian wavelet", self.panel_items)
        if isMain:
            self.show_widget()



     
class g_wavelet_model(pvModel):
    model_value_changed_signal = pyqtSignal(dict)
    def __init__(self, parent):
        super().__init__(parent)

        ## model speficic:
        self.instrument = 'g_wavelet'
        self.param = {  'name': 'Gaussian wavelet',
                        'reference':'',
                        'comment':''}
        
        # Task description markup. Aarbitrary default values ('val') are for type recognition in panel widget constructor
        # supported types are float, int, bool, string, and list of strings
        self.tasks = {  't_min': 
                                {'symbol':u't<sub>0</sub>',
                                    'desc':u'Time min',
                                    'unit':u's',
                                    'val':0, 
                                'increment':0.5,'min':0,'max':1000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        't_max': 
                                {'symbol':u't<sub>max</sub>',
                                    'desc':u'Time max',
                                    'unit':u's',
                                    'val':120e-9,
                                'increment':0.5,'min':0,'max':1000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'center_f': 
                                {'symbol':u'f<sub>0</sub>',
                                    'desc':u'Center frequency',
                                    'unit':u'Hz',
                                    'val':45e6, 
                                'increment':0.5,'min':0,'max':1e12 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'sigma': 
                                {'symbol':u'σ',
                                    'desc':u"Half-width-half-max of the signal in the frequency domain",
                                    'unit':u'Hz',
                                    'val':20e6,
                                'increment':0.5,'min':0,'max':1e12 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'opt':     
                                {'symbol':u'opt',
                                    'desc':u"",
                                    'unit':u'Hz',
                                    'val':0,
                                    'hidden':True,
                                'increment':0.5,'min':0,'max':1000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'i'}},
                        'pts': 
                                {'symbol':u'pts',
                                    'desc':u"",
                                    'unit':u'',
                                    'val':1000,
                                    'hidden':True ,
                                'increment':0.5,'min':0,'max':1000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'i'}},
                                
                                }

        self.create_pvs(self.tasks)
        self.offline = True
        self.start()



class gx2_wavelet_controller(pvController):
    def __init__(self, parent, isMain = False):
        model = gx2_wavelet_model(parent)
        super().__init__(parent, model, isMain)  
        self.panel_items =['t_min',
                      't_max',
                      'center_f',
                      'center_f_2',
                      'sigma']
        self.init_panel("Double Gaussian wavelet", self.panel_items)
        if isMain:
            self.show_widget()
     
class gx2_wavelet_model(pvModel):
    model_value_changed_signal = pyqtSignal(dict)
    def __init__(self, parent):
        super().__init__(parent)

        ## model speficic:
        self.instrument = 'gx2_wavelet'
        self.param = {  'name': 'Double Gaussian wavelet',
                        'reference':'',
                        'comment':''}
        
        # Task description markup. Aarbitrary default values ('val') are for type recognition in panel widget constructor
        # supported types are float, int, bool, string, and list of strings
        self.tasks = {  't_min': 
                                {'symbol':u't<sub>0</sub>',
                                    'desc':u'Time min',
                                    'unit':u's',
                                    'val':0, 
                                'increment':0.5,'min':0,'max':1000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        't_max': 
                                {'symbol':u't<sub>max</sub>',
                                    'desc':u'Time max',
                                    'unit':u's',
                                    'val':120e-9,
                                'increment':0.5,'min':0,'max':1000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'center_f': 
                                {'symbol':u'f<sub>0_1</sub>',
                                     'desc':u'Center 1 frequency',
                                     'unit':u'Hz',
                                     'val':20e6, 
                                'increment':0.5,'min':0,'max':1e12 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'center_f_2': 
                                {'symbol':u'f<sub>0_1</sub>',
                                     'desc':u'Center 2 frequency',
                                     'unit':u'Hz',
                                     'val':45e6, 
                                'increment':0.5,'min':0,'max':1e12 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'sigma': 
                                {'symbol':u'σ',
                                    'desc':u"Half-width-half-max of the signal in the frequency domain",
                                    'unit':u'Hz',
                                    'val':20e6,
                                'increment':0.5,'min':0,'max':1e12 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'opt':     
                                {'symbol':u'opt',
                                    'desc':u"",
                                    'unit':u'Hz',
                                    'val':0,
                                    'hidden':True,
                                'increment':0.5,'min':0,'max':1000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'i'}},
                        'pts': 
                                {'symbol':u'pts',
                                    'desc':u"",
                                    'unit':u'',
                                    'val':1000,
                                    'hidden':True ,
                                'increment':0.5,'min':0,'max':1000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'i'}},
                                
                                }

        self.create_pvs(self.tasks)
        self.offline = True
        self.start()


class burst_fixed_time_controller(pvController):
    def __init__(self, parent, isMain = False):
        model = burst_fixed_time_model(parent)
        super().__init__(parent, model, isMain)  
        self.panel_items =['t_min',
                      't_max',
                      'freq']
        self.init_panel("fixed-time burst", self.panel_items)
        if isMain:
            self.show_widget()
     
class burst_fixed_time_model(pvModel):
    model_value_changed_signal = pyqtSignal(dict)
    def __init__(self, parent):
        super().__init__(parent)

        ## model speficic:
        self.instrument = 'burst_fixed_time'
        self.param = {  'name': 'fixed-time burst',
                        'reference':'',
                        'comment':''}
        
        # Task description markup. Aarbitrary default values ('val') are for type recognition in panel widget constructor
        # supported types are float, int, bool, string, and list of strings
        self.tasks = {  't_min': 
                                {'symbol':u't<sub>0</sub>',
                                    'desc':u'Time min',
                                    'unit':u's',
                                    'val':0, 
                                'increment':0.5,'min':0,'max':1000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        't_max': 
                                {'symbol':u't<sub>max</sub>',
                                    'desc':u'Time max',
                                    'unit':u's',
                                    'val':120e-9,
                                'increment':0.5,'min':0,'max':1000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'freq': 
                                {'symbol':u'f',
                                     'desc':u'Center frequency',
                                     'unit':u'Hz',
                                     'val':30e6, 
                                'increment':0.5,'min':0,'max':1e12 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}}
                                
                                }

        self.create_pvs(self.tasks)
        self.offline = True
        self.start()


