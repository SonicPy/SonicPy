from um.models.arb_waveforms import gaussian_wavelet, burst_fixed_time
from PyQt5.QtCore import QThread, pyqtSignal
from um.models.pv_model import pvModel
from um.controllers.pv_controller import pvController



class g_wavelet_controller(pvController):
    def __init__(self, parent, isMain = False):
        model = g_wavelet_model(parent)
        super().__init__(parent, model, isMain)  
        self.panel_items =['t_min',
                      't_max',
                      'center_f',
                      'sigma',
                      'apply']
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
        self.tasks = {  'waveform':
                                {'desc': 'User waveform 1', 'val':{}, 
                                'methods':{'set':True, 'get':False}, 
                                'param':{'tag':'user1_waveform','type':'dict'}},
                        'apply':     
                                {'desc': ';Apply', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'apply','type':'b'}},
                        't_min': 
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
                                    'desc':u"HWHM in frequency domain",
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
                                'min':1,'max':10000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'i'}},
                        'delay': 
                                {'symbol':u'pts',
                                    'desc':u"",
                                    'unit':u'',
                                    'val':.5,
                                    'hidden':True ,
                                'increment':0.01,'min':0,'max':1 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}}
                                
                                }


        self.create_pvs(self.tasks)
        self.offline = True
        self.start()

    def compute_waveform(self):
        func = gaussian_wavelet
        settings = self.get_settings(['t_min',
                      't_max',
                      'center_f',
                      'sigma',
                      'opt',
                      'pts',
                      'delay'])[self.settings_file_tag]
        print(settings)
        ans = func(settings)
        self.pvs['waveform'].set(ans)
        #print (ans)

    def _set_apply(self, val):
        if val:
            self.compute_waveform()
            self.pvs['apply'].set(False)

class gx2_wavelet_controller(pvController):
    def __init__(self, parent, isMain = False):
        model = gx2_wavelet_model(parent)
        super().__init__(parent, model, isMain)  
        self.panel_items =['t_min',
                      't_max',
                      'center_f',
                      'center_f_2',
                      'sigma',
                      'sigma_2',
                      'apply']
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
        self.tasks = {  'waveform':
                                {'desc': 'User waveform 1', 'val':{}, 
                                'methods':{'set':True, 'get':False}, 
                                'param':{'tag':'user1_waveform','type':'dict'}},
                        'apply':     
                                {'desc': ';Apply', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'apply','type':'b'}},
                        't_min': 
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
                                {'symbol':u'f<sub>0_2</sub>',
                                     'desc':u'Center 2 frequency',
                                     'unit':u'Hz',
                                     'val':45e6, 
                                'increment':0.5,'min':0,'max':1e12 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'sigma': 
                                {'symbol':u'σ',
                                    'desc':u"HWHM in frequency domain",
                                    'unit':u'Hz',
                                    'val':20e6,
                                'increment':0.5,'min':0,'max':1e12 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'sigma_2': 
                                {'symbol':u'σ<sub>0_2</sub>',
                                    'desc':u"HWHM in frequency domain",
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
                                'param':{'tag':'t_min','type':'i'}}
                                
                                }

        self.create_pvs(self.tasks)
        self.offline = True
        self.start()

    def compute_waveform(self):
        func = gaussian_wavelet
        settings = self.get_settings(['t_min',
                      't_max',
                      'center_f',
                      'center_f_2',
                      'sigma',
                      'opt',
                      'pts',
                      'delay'])[self.settings_file_tag]
        print(settings)
        ans = func(settings)
        self.pvs['waveform'].set(ans)
        #print (ans)

    def _set_apply(self, val):
        if val:
            self.compute_waveform()
            self.pvs['apply'].set(False)


class burst_fixed_time_controller(pvController):
    def __init__(self, parent, isMain = False):
        model = burst_fixed_time_model(parent)
        super().__init__(parent, model, isMain)  
        self.panel_items =['duration',
                      'freq',
                      'apply']
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
        self.tasks = {  'waveform':
                                {'desc': 'User waveform 1', 'val':{}, 
                                'methods':{'set':True, 'get':False}, 
                                'param':{'tag':'user1_waveform','type':'dict'}},
                        'apply':     
                                {'desc': ';Apply', 'val':False, 
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'apply','type':'b'}},
                        'duration': 
                                {'symbol':u't<sub>d</sub>',
                                    'desc':u'Duration',
                                    'unit':u's',
                                    'val':120e-9,
                                'increment':0.5,'min':0,'max':1000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'freq': 
                                {'symbol':u'f',
                                     'desc':u'Frequency',
                                     'unit':u'Hz',
                                     'val':30e6, 
                                'increment':0.5,'min':0,'max':1e12 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'t_min','type':'f'}},
                        'pts': 
                                {'symbol':u'',
                                     'desc':u'',
                                     'unit':u'',
                                     'val':1000, 
                                'min':1,'max':10000 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'pts','type':'i'}},
                        'symmetric': 
                                {'symbol':u'',
                                    'desc':u'',
                                    'unit':u'',
                                    'val':0, 
                                'min':0,'max':1 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'symmetric','type':'i'}},
                        'quarter_shift': 
                                {'symbol':u'',
                                    'desc':u'',
                                    'unit':u'',
                                    'val':0, 
                                'min':0,'max':1 ,
                                'methods':{'set':True, 'get':True}, 
                                'param':{'tag':'quarter_shift','type':'i'}},
                                
                                }

                       

        self.create_pvs(self.tasks)
        self.offline = True
        self.start()

    def compute_waveform(self):
        func = burst_fixed_time
        settings = self.get_settings(['duration',
                      'freq',
                      'symmetric',
                      'quarter_shift',
                      'pts'])[self.settings_file_tag]
        
        ans = func(settings)
        self.pvs['waveform'].set(ans)

        #print (ans)

    def _set_apply(self, val):
        if val:
            self.compute_waveform()
            self.pvs['apply'].set(False)
