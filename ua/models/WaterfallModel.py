import numpy as np
from numpy.core.defchararray import asarray
import time, os

class WaterfallModel( ):
    ''' synchronous version of the waterfall model '''

    def __init__(self , common_value):
       
        self.common_value = common_value
        
        self.waveforms = [{}]
        self.settings = {'scale':1.0,
                         'clip':False}
        self.waterfall_out = {}

        self.echoes = {'P':{},'S':{}}
     

    def add_multiple_waveforms(self, params ):
        
        for d, p in enumerate(params):

            '''if d % 2 == 0:
                #update progress bar only every 10 files to save time
                progress_dialog.setValue(d)
                QtWidgets.QApplication.processEvents()'''
            self. add_waveform(params[p])

        

    def add_one_waveform(self, param:dict):
        # param is a dict {'filename': "./*.csv", 'waveform':[x1,x2, ..., yn], [y1, y2, ..., yn] }
        fname = param['filename']
        wform = param['waveform']
        x = wform[0]
        y = wform[1]
        if len(x)>100:
            x = x.reshape(-1, 4).mean(axis=1)
     
            y = y.reshape(-1, 4).mean(axis=1)
        wform = [x,y]

        self.waveforms[0][fname]=wform


    def add_waveform(self, param):
        self.add_one_waveform(param)
        

    def set_scale(self, scale):
        self.settings['scale'] = scale
        

    def set_clip(self, clip):
        self.settings['clip'] = clip
        

    def get_rescaled_waveforms(self):
        out = {}
        scale = self.settings['scale' ]
        offset = 1
        clip = self.settings['clip' ]

        fnames = list(self.waveforms[0].keys())+[" "," "] # pad the list with two empty items to have better scaling of the plot, there should be a better way to do it.
        
        if len(self.waterfall_out):
            if scale == self.waterfall_out['scale'] and clip == self.waterfall_out['clip'] and fnames == self. waterfall_out['fnames']:
                #save time by not recalculating waterfall with same settings
                return self.waterfall_out
        
        if len(fnames):
            x = np.empty([0])
            y = np.empty([0])

            self.waveform_limits = {}

            #first_num = int(fnames[0][-1*(len('.csv')+3):-1*len('.csv')])
            start_time = time.time()
            for i, f in enumerate(fnames):
                
                key = f
                if key in self.waveforms[0]:
                    waveform = self.waveforms[0][key]
                else:
                    waveform = [np.asarray([0]),np.asarray([0])]
                    
                x_next = waveform[0]
                y_next = waveform[1]*float(scale)
                if clip:
                    y_next[y_next>(offset/2* 0.9)] = offset/2 * 0.9
                    y_next[y_next<(-1*offset/2* 0.9)] = -1*offset/2 * 0.9
                y_next = y_next + i * float(offset)
                
                pos_pre = len(x)
                if len(x):
                    x = np.append(x,np.nan)
                    y = np.append(y,np.nan)
                
                x = np.append(x,x_next)
                y = np.append(y,y_next)
                pos_post = len(x)
                self.waveform_limits[f] = [pos_pre,pos_post]
                

            waveform = [x,y]
            out = {'waveform':waveform,
                    'scale':scale,
                    'clip':clip,
                    'fnames':fnames}
                    
        self.waterfall_out = out


    def prepare_waveforms_for_plot(self, selected_fname):
        waterfall = self
        limits=[]
        if len(selected_fname):
            fnames = list(waterfall.waveforms[0].keys())
            if selected_fname in fnames:
                limits = waterfall.waveform_limits[ selected_fname ]
        waterfall_waveform = waterfall.waterfall_out['waveform']

        if len(limits):
            selected = [waterfall_waveform[0] [limits[0]:limits[1]],
                        waterfall_waveform[1] [limits[0]:limits[1]]]
            waterfall_waveform = [ np.append(waterfall_waveform[0] [:limits[0]], waterfall_waveform[0] [limits[1]:]),
                                   np.append(waterfall_waveform[1] [:limits[0]], waterfall_waveform[1] [limits[1]:])]

            path = os.path.normpath(selected_fname)
            fldr = path.split(os.sep)[-2]
            file = path.split(os.sep)[-1]
            selected_name_out = os.path.join( fldr,file)
        else:
            selected = [[],[]]
            selected_name_out = ''
        return waterfall_waveform, selected, selected_name_out

    def clear(self):
        
        self.waveforms[0]={}
        self.waterfall_out = self.waveforms[0]
         
