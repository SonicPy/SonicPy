
from models.arb_filters import my_filter


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

fltr1 = fltr_none()
fltr2 = fltr_tukey()
fltr3 = fltr_lowpass()

filters = {fltr1.name:fltr1, 
            fltr2.name:fltr2, 
            fltr3.name:fltr3}
