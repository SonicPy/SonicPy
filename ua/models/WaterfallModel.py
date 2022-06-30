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

        self.echoes_p_ind = {}
        self.echoes_s_ind = {}

        self.bin_size = 4

        

    def re_order_files(self, new_list):
        fnames = list(self.waveforms.keys())
        new_waveforms = {}
        for fname in new_list:
            if fname in fnames:
                new_waveforms[fname] = self.waveforms[fname]
        self.waveforms = new_waveforms

    def del_echoe(self, fname, wave_type):
        if wave_type == 'P':
            del self.echoes_p_ind[fname] 

        elif wave_type == 'S':
            del self.echoes_s_ind[fname] 

    def set_echoe(self, fname, wave_type, echoes_bounds):
        # echoes_bounds = list, [[0,0],[0,0]]
        # echoes_bounds[0]: P bounds
        # echoes_bounds[0]: S bounds

        fnames = list(self.waveforms.keys())
        if fname in fnames :

            # convert echo bounds seconds to index by looking up the horizontal axis
            waveform = self.waveforms[fnames[0]]
            x_values = waveform[0]
            lb1 = int(get_partial_index(x_values,echoes_bounds[0][0]))
            
            rb1 = int(get_partial_index(x_values,echoes_bounds[0][1]))
            lb2 = int(get_partial_index(x_values,echoes_bounds[1][0]))
            rb2 = int(get_partial_index(x_values,echoes_bounds[1][1]))
            echoes_bounds_ind = [[lb1, rb1],[lb2, rb2]]

            if wave_type == 'P':
                self.echoes_p_ind[fname] = echoes_bounds_ind

            elif wave_type == 'S':
                self.echoes_s_ind[fname] = echoes_bounds_ind

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
        x_size = len(x)
        if x_size>100:
            bin_size = self.bin_size
            if x_size>25000:
                bin_size = self.bin_size *2
            if x_size> 100000:
                bin_size = self.bin_size * 10

            x = x.reshape(-1, bin_size).mean(axis=1)
     
            y = y.reshape(-1, bin_size).mean(axis=1)
        wform = [x,y]

        self.waveforms[fname]=wform


    def add_waveform(self, param):
        self.add_one_waveform(param)
        

    def set_scale(self, scale):
        self.settings['scale'] = scale
        

    def set_clip(self, clip):
        self.settings['clip'] = clip

    def delete_section(self, x, y, echo_bound_ind):
        # deletes section and replaces with a np.nan
        # echoes_bounds_ind (ebi) = [[lb1, rb1],[lb2, rb2]]
        ebi = echo_bound_ind

        echo_x_1 = x[ebi[0][0]:ebi[0][1]+2]
        echo_x_2 = x[ebi[1][0]:ebi[1][1]+2]

        echo_x = np.append(np.append(echo_x_1, np.nan), echo_x_2)

        echo_y_1 = y[ebi[0][0]:ebi[0][1]+2]
        echo_y_2 = y[ebi[1][0]:ebi[1][1]+2]

        echo_y = np.append(np.append(echo_y_1, np.nan), echo_y_2)
        
        # delete right echo part first to not mess up the indeces
        x = np.delete(x, np.s_[ebi[1][0]+1:ebi[1][1]+1], )
        x = np.insert(x, ebi[1][0]+1, np.nan)
        x = np.delete(x, np.s_[ebi[0][0]+1:ebi[0][1]+1])
        x = np.insert(x, ebi[0][0]+1, np.nan)
        
        y = np.delete(y, np.s_[ebi[1][0]+1:ebi[1][1]+1])
        y = np.insert(y, ebi[1][0]+1, np.nan)
        y = np.delete(y, np.s_[ebi[0][0]+1:ebi[0][1]+1])
        y = np.insert(y, ebi[0][0]+1, np.nan)

        return x, y, echo_x, echo_y
        

    def get_rescaled_waveforms(self, caller = ''):
        
        out = {}
        scale = self.settings['scale' ]
        offset = 1
        clip = self.settings['clip' ]
        
        fnames = list(self.waveforms.keys())+[" "," "] # pad the list with two empty items to have better scaling of the plot, there should be a better way to do it.
        
        if len(self.waterfall_out):
            if scale == self.waterfall_out['scale'] and clip == self.waterfall_out['clip'] \
                and fnames == self. waterfall_out['fnames']:
                #print('get_rescaled_waveforms. reuse. caller: ' + caller)
                if self.echoes_p_ind == self. waterfall_out['echoes_p_ind'] and self.echoes_s_ind == self. waterfall_out['echoes_s_ind']:
                #save time by not recalculating waterfall with same settings
                    pass
                    return self.waterfall_out
        
        if len(fnames):
            #print('get_rescaled_waveforms. new. caller: ' + caller)

            x = np.empty([0])
            y = np.empty([0])

            x_echo_p = np.empty([0])
            y_echo_p = np.empty([0])

            x_echo_s = np.empty([0])
            y_echo_s = np.empty([0])

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

                if f in self.echoes_s_ind:
                    # echoes_bounds_ind (ebi) = [[lb1, rb1],[lb2, rb2]]
                    ebi = self.echoes_s_ind[f]
                    x_next, y_next, x_echo_s_next, y_echo_s_next = self. delete_section(x_next, y_next, ebi)
                    x_echo_s = np.append(x_echo_s,x_echo_s_next)
                    y_echo_s = np.append(y_echo_s,y_echo_s_next)
                    x_echo_s = np.append(x_echo_s,np.nan)
                    y_echo_s = np.append(y_echo_s,np.nan)

                # make gaps in x_next and y_next for where the echoes would be
                if f in self.echoes_p_ind:
                    # echoes_bounds_ind (ebi) = [[lb1, rb1],[lb2, rb2]]
                    ebi = self.echoes_p_ind[f]
                    x_next, y_next, x_echo_p_next, y_echo_p_next = self. delete_section(x_next, y_next, ebi)
                    x_echo_p = np.append(x_echo_p,x_echo_p_next)
                    y_echo_p = np.append(y_echo_p,y_echo_p_next)
                    x_echo_p = np.append(x_echo_p,np.nan)
                    y_echo_p = np.append(y_echo_p,np.nan)

                
                
                x = np.append(x,x_next)
                y = np.append(y,y_next)
                pos_post = len(x)

                self.waveform_limits[f] = [pos_pre,pos_post]

                
            waveform = [x,y]
            echoes_p = [x_echo_p, y_echo_p]
            echoes_s = [x_echo_s, y_echo_s]
            out = {'waveform':waveform,
                    'scale':scale,
                    'clip':clip,
                    'fnames':fnames,
                    'echoes_p':  echoes_p,
                    'echoes_s':  echoes_s,
                    'echoes_p_ind':  copy.deepcopy(self.echoes_p_ind),
                    'echoes_s_ind':  copy.deepcopy(self.echoes_s_ind)
                    }
                    
        self.waterfall_out = out


    def prepare_waveforms_for_plot(self, selected_fname):
        
        limits=[]
        selected = [[],[]] 
        echoe_p = [[],[]] 
        echoe_s = [[],[]] 
        
        if len(selected_fname):
            fnames = list(self.waveforms.keys())
            if selected_fname in fnames:
                limits = self.waveform_limits[ selected_fname ]
        waterfall_waveform = self.waterfall_out['waveform']
        echoe_p = self.waterfall_out['echoes_p']
        echoe_s = self.waterfall_out['echoes_s']

        if len(limits):
            # blue part
            selected = [waterfall_waveform[0] [limits[0]:limits[1]],
                        waterfall_waveform[1] [limits[0]:limits[1]]]
            # yellow part
            waterfall_waveform = [ np.append(waterfall_waveform[0] [:limits[0]], waterfall_waveform[0] [limits[1]:]),
                                   np.append(waterfall_waveform[1] [:limits[0]], waterfall_waveform[1] [limits[1]:])]

        
            

            path = os.path.normpath(selected_fname)
            fldr = path.split(os.sep)[-2]
            file = path.split(os.sep)[-1]
            selected_name_out = os.path.join( fldr,file)
        else:
            selected = [[],[]] 
            
            selected_name_out = ''
        return waterfall_waveform, selected, selected_name_out, echoe_p, echoe_s

   