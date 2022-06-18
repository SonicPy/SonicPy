import numpy as np
from numpy.core.defchararray import asarray
import time, os, copy
from utilities.HelperModule import get_partial_index, get_partial_value

class WaterfallModel( ):
    ''' synchronous version of the waterfall model '''

    def __init__(self , common_value):
       
        self.common_value = common_value
        
        self.waveforms = {}
        self.settings = {'scale':1.0,
                         'clip':False}
        self.waterfall_out = {}

        self.echoes_p = {}
        self.echoes_s = {}
     

    def set_echoes(self, fname, wave_type, echoes_bounds):
        # echoes_bounds = list, [[0,0],[0,0]]
        # echoes_bounds[0]: P bounds
        # echoes_bounds[0]: S bounds

        fnames = list(self.waveforms.keys())
        if len(fnames):
            waveform = self.waveforms[fnames[0]]
            x_values = waveform[0]

            
            lb1 = int(get_partial_index(x_values,echoes_bounds[0][0]))
            rb1 = int(get_partial_index(x_values,echoes_bounds[0][1]))
            lb2 = int(get_partial_index(x_values,echoes_bounds[1][0]))
            rb2 = int(get_partial_index(x_values,echoes_bounds[1][1]))

            echoes_bounds_ind = [[lb1, rb1],[lb2, rb2]]

            if wave_type == 'P':
                self.echoes_p[fname] = echoes_bounds_ind

            elif wave_type == 'S':
                self.echoes_s[fname] = echoes_bounds_ind
        


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

        self.waveforms[fname]=wform


    def add_waveform(self, param):
        self.add_one_waveform(param)
        

    def set_scale(self, scale):
        self.settings['scale'] = scale
        

    def set_clip(self, clip):
        self.settings['clip'] = clip

    
        

    def get_rescaled_waveforms(self, caller = ''):
        print('get_rescaled_waveforms. caller: ' + caller)
        out = {}
        scale = self.settings['scale' ]
        offset = 1
        clip = self.settings['clip' ]
        

        fnames = list(self.waveforms.keys())+[" "," "] # pad the list with two empty items to have better scaling of the plot, there should be a better way to do it.
        
        if len(self.waterfall_out):
            if scale == self.waterfall_out['scale'] and clip == self.waterfall_out['clip'] \
                and fnames == self. waterfall_out['fnames']:
                #save time by not recalculating waterfall with same settings
                return self.waterfall_out
        
        if len(fnames):
            x = np.empty([0])
            y = np.empty([0])

            self.waveform_limits = {}

            start_time = time.time()
            for i, f in enumerate(fnames):
                
                key = f
                if key in self.waveforms:
                    waveform = self.waveforms[key]
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
                    'fnames':fnames,
                    'echoes_p':  copy.deepcopy(self.echoes_p),
                    'echoes_s':  copy.deepcopy(self.echoes_s)
                    }
                    
        self.waterfall_out = out


    def prepare_waveforms_for_plot(self, selected_fname):
        
        limits=[]
        selected = [[],[]] 
        echoe_p = [[],[]] 
        
        if len(selected_fname):
            fnames = list(self.waveforms.keys())
            if selected_fname in fnames:
                limits = self.waveform_limits[ selected_fname ]
        waterfall_waveform = self.waterfall_out['waveform']

        if len(limits):
            # blue part
            selected = [waterfall_waveform[0] [limits[0]:limits[1]],
                        waterfall_waveform[1] [limits[0]:limits[1]]]
            # yellow part
            waterfall_waveform = [ np.append(waterfall_waveform[0] [:limits[0]], waterfall_waveform[0] [limits[1]:]),
                                   np.append(waterfall_waveform[1] [:limits[0]], waterfall_waveform[1] [limits[1]:])]

        
            for fname in self.echoes_p:
                p_i = self.echoes_p[fname]
                echoe_p = [ np.append(  np.append( waterfall_waveform[0] [p_i[0][0]:p_i[0][1]], np.nan), waterfall_waveform[0] [p_i[1][0]:p_i[1][1]] ) ,
                              np.append(  np.append( waterfall_waveform[1] [p_i[0][0]:p_i[0][1]], np.nan), waterfall_waveform[1] [p_i[1][0]:p_i[1][1]] ) ]
                
            

            path = os.path.normpath(selected_fname)
            fldr = path.split(os.sep)[-2]
            file = path.split(os.sep)[-1]
            selected_name_out = os.path.join( fldr,file)
        else:
            selected = [[],[]] 
            echoe_p = [[],[]] 
            selected_name_out = ''
        return waterfall_waveform, selected, selected_name_out, echoe_p

    def clear(self):
        
        self.waveforms={}
        self.waterfall_out = self.waveforms
         
