from models.arb_waveforms import gaussian_wavelet

from models.pv_model import pvModel

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
'''
class g_wavelet(pvController):
    
    def __init__(self, parent, isMain = False):

        
        model = AFG_AFG3251(parent)
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
     

'''


class g_wavelet(arb_waveform):
    def __init__(self):
        self.name = 'g_wavelet'
        self.func = gaussian_wavelet
        self.param = {  'name': 'Gaussian wavelet',
                        'reference':'',
                        'comment':'',
                        'params':{ 
                        't_min':      {'symbol':u't<sub>0</sub>',
                                    'desc':u'Time min',
                                    'unit':u's',
                                    'val':0}, 
                        't_max':      {'symbol':u't<sub>max</sub>',
                                    'desc':u'Time max',
                                    'unit':u's',
                                    'val':120e-9},
                        'center_f': {'symbol':u'f<sub>0</sub>',
                                    'desc':u'Center frequency',
                                    'unit':u'Hz',
                                    'val':45e6}, 
                        'sigma': {'symbol':u'σ',
                                    'desc':u"Half-width-half-max of the signal in the frequency domain",
                                    'unit':u'Hz',
                                    'val':20e6},
                        'delay': {'symbol':u'del',
                                    'desc':u"",
                                    'unit':u'',
                                    'val':.5,
                                    'hidden':True},
                        'opt': {'symbol':u'opt',
                                    'desc':u"",
                                    'unit':u'Hz',
                                    'val':0,
                                    'hidden':True},
                        'pts': {'symbol':u'pts',
                                    'desc':u"",
                                    'unit':u'',
                                    'val':1000,
                                    'hidden':True}
                        }}


class gx2_wavelet(arb_waveform):
    def __init__(self):
        self.name = 'gx2_wavelet'
        self.param = {
                        'name': 'Double Gaussian wavelet',
                        'reference':'',
                        'comment':'',
                        'params':{ 
                        't_min':      {'symbol':u't<sub>0</sub>',
                                     'desc':u'Time min',
                                     'unit':u's',
                                     'val':0}, 
                        't_max':      {'symbol':u't<sub>max</sub>',
                                     'desc':u'Time max',
                                     'unit':u's',
                                     'val':120e-9},
                        'center_f': {'symbol':u'f<sub>0_1</sub>',
                                     'desc':u'Center 1 frequency',
                                     'unit':u'Hz',
                                     'val':20e6}, 
                        'center_f_2': {'symbol':u'f<sub>0_1</sub>',
                                     'desc':u'Center 2 frequency',
                                     'unit':u'Hz',
                                     'val':45e6},
                        'sigma1': {'symbol':u'σ<sub>1</sub>',
                                     'desc':u"Half-width-half-max of the signal in the frequency domain",
                                     'unit':u'Hz',
                                     'val':20e6},
                        'sigma2': {'symbol':u'σ<sub>2</sub>',
                                     'desc':u"Half-width-half-max of the signal in the frequency domain",
                                     'unit':u'Hz',
                                     'val':20e6}
                        }}



class burst_fixed_time(arb_waveform):
    def __init__(self):
        self.name = 'burst_fixed_time'
        self.param = {
                        'name': 'fixed-time burst',
                        'reference':'',
                        'comment':'',
                        'params':{ 
                        't_min':      {'symbol':u't<sub>0</sub>',
                                     'desc':u'Time min',
                                     'unit':u's',
                                     'val':0}, 
                        't_max':      {'symbol':u't<sub>max</sub>',
                                     'desc':u'Time max',
                                     'unit':u's',
                                     'val':120e-9},
                        'freq': {'symbol':u'f',
                                     'desc':u'Center frequency',
                                     'unit':u'Hz',
                                     'val':30e6}
                        }}

arb1 = g_wavelet()
arb2 = gx2_wavelet()

arb3 = burst_fixed_time()

arb_waveforms = {arb1.name:arb1, 
                arb2.name:arb2, 
                arb3.name:arb3}

