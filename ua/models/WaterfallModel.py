import numpy as np


class WaterfallModel( ):
    ''' synchronous version of the waterfall model '''

    def __init__(self ):
       
     
        self.scans = [{}]
        self.settings = {'scale':1.0,
                         'clip':False}

    def add_multiple_waveforms(self, params ):
        for p in params:
            self. add_waveform(p)

        

    def add_one_waveform(self, param:dict):
        # param is a dict {'filename': "./*.csv", 'waveform':[x1,x2, ..., yn], [y1, y2, ..., yn] }
        fname = param['filename']
        wform = param['waveform']
        x = wform[0].reshape(-1, 4).mean(axis=1)
     
        y = wform[1].reshape(-1, 4).mean(axis=1)
        wform = [x,y]
        self.scans[0][fname]=wform


    def add_waveform(self, param):
        self.add_one_waveform(param)
        

    def set_scale(self, scale):
        self.settings['scale'] = scale
        

    def set_clip(self, clip):
        self.settings['clip'] = clip
        

    def rescale_waveforms(self):
        out = {}
        scale = self.settings['scale' ]
        offset = 1
        clip = self.settings['clip' ]

        fnames = list(self.scans[0].keys())
        
        
        if len(fnames):
            x = np.empty([0])
            y = np.empty([0])
            
            for i, f in enumerate(fnames):
                
                key = f
                waveform = self.scans[0][key]
                
                x_next = waveform[0]
                y_next = waveform[1]*float(scale)
                if clip:
                    y_next[y_next>(offset/2* 0.9)] = offset/2 * 0.9
                    y_next[y_next<(-1*offset/2* 0.9)] = -1*offset/2 * 0.9
                y_next = y_next + i * float(offset)
                
                
                if len(x):
                    x = np.append(x,np.nan)
                    y = np.append(y,np.nan)
                
                x = np.append(x,x_next)
                y = np.append(y,y_next)
            waveform = [x,y]
            out = {'waveform':waveform}
          
        self.waterfall_out = out


    def clear(self):
        
        self.scans[0]={}
        self.waterfall_out = self.scans[0]
         