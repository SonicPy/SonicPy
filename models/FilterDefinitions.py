filters = {       'none':{
                        'name': 'No filter',
                        'reference':'',
                        'comment':'',
                        'params':{ 
                        }},
                  'tukey':{
                        'name': 'Tukey, cosine-tapered window',
                        'reference':'',
                        'comment':u'The Tukey window, also known as the cosine-tapered window, can be regarded as a cosine lobe of width α(N + 1)/2 that is convolved with a rectangular window of width (1 − α/2)(N + 1)',
                        'params':{ 
                        'alpha':      {'symbol':u'α',
                                     'desc':u'At α = 0 it becomes rectangular, and at α = 1 it becomes a Hann window',
                                     'unit':'',
                                     'default':.1}
                        }},
                  'lowpass':{
                        'name': 'Lowpass',
                        'reference':'',
                        'comment':u'',
                        'params':{ 
                        'f_lowcut':  {'symbol':u'f<sub>L</sub>',
                                     'desc':u'Low-cut frequency',
                                     'unit':'Hz',
                                     'default':30e6}
                        }}
}