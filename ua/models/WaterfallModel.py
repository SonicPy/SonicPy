import numpy as np
from numpy.core.defchararray import asarray
import time

class WaterfallModel( ):
    ''' synchronous version of the waterfall model '''

    def __init__(self , common_value):
       
        self.common_value = common_value
        
        self.scans = [{}]
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

        self.scans[0][fname]=wform


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

        fnames = list(self.scans[0].keys())+[" "," "] # pad the list with two empty items to have better scaling of the plot, there should be a better way to do it.
        
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
                if key in self.scans[0]:
                    waveform = self.scans[0][key]
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
            #print("waterfall composed from  " + str(len(fnames)) + " files in %s seconds." % (time.time() - start_time))
        self.waterfall_out = out


    def clear(self):
        
        self.scans[0]={}
        self.waterfall_out = self.scans[0]
         