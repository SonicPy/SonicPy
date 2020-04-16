from um.models.arb_waveforms import gaussian_wavelet, burst_fixed_time
from PyQt5.QtCore import QThread, pyqtSignal
from um.models.pv_model import pvModel
from um.controllers.pv_controller import pvController
from functools import partial
from um.models.pvServer import pvServer

class arb_function(pvController):
    def __init__(self, parent, isMain = False, title='', \
                    arb_name = '', arb_desc='', arb_ref='', \
                        arb_comment='', panel_items=[], arb_variables = {}, arb_function=None):
        
        model = arb_model(parent)
        model.instrument = arb_name
        model.arb_variables = arb_variables   
        model.param = {  'name': arb_desc,
                        'reference':arb_ref,
                        'comment':arb_comment}
        model.tasks = {**model.tasks , **arb_variables}
        model.create_pvs(model.tasks)
        model.create_compute_function(list(model.arb_variables.keys()),arb_function)
        

        super().__init__(parent, model, isMain)  
        panel_itmes = panel_items+['apply',
                                    'auto_process']
        self.panel_items = panel_itmes
        self.init_panel(title, self.panel_items)
        if isMain:
            self.show_widget()

class arb_model(pvModel):
    model_value_changed_signal = pyqtSignal(dict)
    def __init__(self, parent, arb_name = ''):
        super().__init__(parent)
        self.pv_server = pvServer()
        ## model speficic:
        self.offline = True
        self.instrument = arb_name
        
        # Task description markup. Aarbitrary default values ('val') are for type recognition in panel widget constructor
        # supported types are float, int, bool, string, and list of strings
        self.tasks = {  
                        'output_channel':     
                                {'desc': 'Output channel', 'val':None, 
                                'param':{ 'type':'s'}},
                        'apply':     
                                {'desc': ';Apply', 'val':False, 
                                'param':{ 'type':'b'}},
                        'auto_process':     
                                {'desc': ';Auto process', 'val':False, 
                                'param':{ 'type':'b'}}
        }

    def create_compute_function(self, settings_list, function):
        func = partial(self._compute,settings_list,function)
        setattr(self,'compute_waveform',func)

    def _compute(self, settings_list, func):
        settings = self.get_settings(settings_list)[self.settings_file_tag]
        ans = func(settings)
        output_channel = self.pv_server.get_pv(self.pvs['output_channel']._val)
        output_channel.set(ans)
     
    def _set_apply(self, val):
        if val:
            self.compute_waveform()
            self.pvs['apply'].set(False)

    def _set_auto_process(self, val):
        self.pvs['auto_process']._val = val
        arb_vars = list(self.arb_variables.keys())
        if val:
            self.set_autoprocess_connections(arb_vars)
        else:
            self.unset_autoprocess_connections(arb_vars)

    def set_autoprocess_connections(self, pv_names):
        for pv in pv_names:
            self.pvs[pv].value_changed_signal.connect(self._apply)

    def unset_autoprocess_connections(self, pv_names):
        for pv in pv_names:
            self.pvs[pv].value_changed_signal.disconnect(self._apply)

    def _apply(self):
        self.pvs['apply'].set(True)


class g_wavelet_controller(arb_function):
    def __init__(self, parent, isMain = False):
        panel_items =[
                      't_max',
                      'center_f',
                      'sigma']
        title = "Gaussian wavelet"
        arb_name = 'g_wavelet'
        arb_desc=title
        arb_ref=''
        arb_comment=''
        arb_variables = {'t_min': 
                                {'symbol':u't<sub>0</sub>',
                                    'desc':u'Time min',
                                    'unit':u'ns',
                                    'val':0, 
                                    'val_scale': 1e-9,
                                'increment':0.5,'min':0,'max':1000 ,
                                'param':{ 'type':'f'}},
                        't_max': 
                                {'symbol':u't<sub>max</sub>',
                                    'desc':u'Duration',
                                    'unit':u'ns',
                                    'val':120e-9,
                                    'val_scale': 1e-9,
                                'increment':0.5,'min':0,'max':1000 ,
                                'param':{ 'type':'f'}},
                        'center_f': 
                                {'symbol':u'f<sub>0</sub>',
                                    'desc':u'Center frequency',
                                    'unit':u'MHz',
                                    'val':45e6, 
                                    'val_scale': 1e6,
                                'increment':0.5,'min':0,'max':1e12 ,
                                'param':{ 'type':'f'}},
                        'sigma': 
                                {'symbol':u'σ',
                                    'desc':u"HWHM in frequency domain",
                                    'unit':u'MHz',
                                    'val':20e6,
                                    'val_scale': 1e6,
                                'increment':0.5,'min':0,'max':1e12 ,
                                'param':{ 'type':'f'}},
                        'opt':     
                                {'symbol':u'opt',
                                    'desc':u"",
                                    'unit':u'MHz',
                                    'val':0,
                                    'val_scale': 1e6,
                                    'hidden':True,
                                'increment':0.5,'min':0,'max':1000 ,
                                'param':{ 'type':'i'}},
                        'pts': 
                                {'symbol':u'pts',
                                    'desc':u"",
                                    'unit':u'',
                                    'val':1000,
                                    'hidden':True ,
                                'min':1,'max':10000 ,
                                'param':{ 'type':'i'}},
                        'delay': 
                                {'symbol':u'pts',
                                    'desc':u"",
                                    'unit':u'',
                                    'val':.5,
                                    'hidden':True ,
                                'increment':0.01,'min':0,'max':1 ,
                                'param':{ 'type':'f'}}
                                }
        arb_function = gaussian_wavelet

        super().__init__(parent,isMain,title,arb_name=arb_name, \
                        arb_desc=arb_desc,panel_items=panel_items,\
                            arb_variables=arb_variables,arb_function=arb_function,\
                                arb_ref=arb_ref, arb_comment=arb_comment ) 


class burst_fixed_time_controller(arb_function):
    def __init__(self, parent, isMain = False):
        panel_items =['duration',
                      'freq']
        title = "Fixed-time burst"
        arb_name = 'burst_fixed_time'
        arb_desc=title
        arb_ref=''
        arb_comment=''
        arb_variables = {'duration': 
                                {'symbol':u't<sub>d</sub>',
                                    'desc':u'Duration',
                                    'unit':u'ns',
                                    'val':120e-9,
                                    'val_scale': 1e-9,
                                'increment':0.5,'min':0,'max':1000 ,
                                'param':{ 'type':'f'}},
                        'freq': 
                                {'symbol':u'f',
                                     'desc':u'Frequency',
                                     'unit':u'MHz',
                                     'val':30e6,
                                     'val_scale': 1e6,
                                'increment':0.5,'min':0.001,'max':10000 ,
                                'param':{ 'type':'f'}},
                        'pts': 
                                {'symbol':u'',
                                     'desc':u'',
                                     'unit':u'',
                                     'val':1000, 
                                'min':1,'max':10000 ,
                                'param':{ 'type':'i'}},
                        'symmetric': 
                                {'symbol':u'',
                                    'desc':u'',
                                    'unit':u'',
                                    'val':0, 
                                'min':0,'max':1 ,
                                'param':{ 'type':'i'}},
                        'quarter_shift': 
                                {'symbol':u'',
                                    'desc':u'',
                                    'unit':u'',
                                    'val':0, 
                                'min':0,'max':1 ,
                                'param':{ 'type':'i'}},
                                
                                }
        arb_function = burst_fixed_time

        

        super().__init__(parent,isMain,title,arb_name=arb_name, \
                        arb_desc=arb_desc,panel_items=panel_items,\
                            arb_variables=arb_variables,arb_function=arb_function,\
                                arb_ref=arb_ref, arb_comment=arb_comment ) 

        self.scan_pv = self.model.pvs['freq']

### not ready yet:

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
        self.tasks = {  
                        'output_channel':     
                                {'desc': 'Output channel', 'val':None, 
                                'param':{ 'type':'pv'}},
                        'apply':     
                                {'desc': ';Apply', 'val':False, 
                                'param':{ 'type':'b'}},
                        'auto_process':     
                                {'desc': ';Auto process', 'val':False, 
                                'param':{ 'type':'b'}},
                        't_min': 
                                {'symbol':u't<sub>0</sub>',
                                    'desc':u'Time min',
                                    'unit':u's',
                                    'val':0, 
                                'increment':0.5,'min':0,'max':1000 ,
                                'param':{ 'type':'f'}},
                        't_max': 
                                {'symbol':u't<sub>max</sub>',
                                    'desc':u'Time max',
                                    'unit':u's',
                                    'val':120e-9,
                                'increment':0.5,'min':0,'max':1000 ,
                                'param':{ 'type':'f'}},
                        'center_f': 
                                {'symbol':u'f<sub>0_1</sub>',
                                     'desc':u'Center 1 frequency',
                                     'unit':u'Hz',
                                     'val':20e6, 
                                'increment':0.5,'min':0,'max':1e12 ,
                                'param':{ 'type':'f'}},
                        'center_f_2': 
                                {'symbol':u'f<sub>0_2</sub>',
                                     'desc':u'Center 2 frequency',
                                     'unit':u'Hz',
                                     'val':45e6, 
                                'increment':0.5,'min':0,'max':1e12 ,
                                'param':{ 'type':'f'}},
                        'sigma': 
                                {'symbol':u'σ',
                                    'desc':u"HWHM in frequency domain",
                                    'unit':u'Hz',
                                    'val':20e6,
                                'increment':0.5,'min':0,'max':1e12 ,
                                'param':{ 'type':'f'}},
                        'sigma_2': 
                                {'symbol':u'σ<sub>0_2</sub>',
                                    'desc':u"HWHM in frequency domain",
                                    'unit':u'Hz',
                                    'val':20e6,
                                'increment':0.5,'min':0,'max':1e12 ,
                                'param':{ 'type':'f'}},
                        'opt':     
                                {'symbol':u'opt',
                                    'desc':u"",
                                    'unit':u'Hz',
                                    'val':0,
                                    'hidden':True,
                                'increment':0.5,'min':0,'max':1000 ,
                                'param':{ 'type':'i'}},
                        'pts': 
                                {'symbol':u'pts',
                                    'desc':u"",
                                    'unit':u'',
                                    'val':1000,
                                    'hidden':True ,
                                'increment':0.5,'min':0,'max':1000 ,
                                'param':{ 'type':'i'}}
                                
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
        output_channel = self.pvs['output_channel']._val
        print(output)
        output_channel.set(ans)
        #print (ans)

    def _set_apply(self, val):
        if val:
            self.compute_waveform()
            self.pvs['apply'].set(False)