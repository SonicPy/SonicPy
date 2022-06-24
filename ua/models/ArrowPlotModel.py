
import os.path, sys
from ua.models.OverViewModel import Sort_Tuple
from utilities.utilities import *
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import numpy as np
from numpy import argmax, nan, greater,less, append, sort, array, argmin

from scipy import optimize
from scipy.signal import argrelextrema, tukey
from functools import partial
from um.models.tek_fileIO import *
from scipy import signal
import pyqtgraph as pg
from utilities.utilities import zero_phase_bandpass_filter
import json


class optima():
    def __init__(self, data, frequency, filename_waveform):
        self.filename_waveform = filename_waveform
        self.freq = frequency
        self.minima = data['minima']
        self.maxima = data['maxima']
        self.minima_t = data['minima_t']
        self.maxima_t = data['maxima_t']
        self.num_opt = {}
        self.all_optima = {}
        self.init_optima()
        
    def init_optima(self):
        self.center_opt={}
        self.other_opt={}
        self.center_opt['min'] = self.minima_t[argmin(self.minima)]
        self.center_opt['max'] = self.maxima_t[argmax(self.maxima)]
        self.num_opt['min'] = len(self.minima)
        self.num_opt['max'] = len(self.maxima)
        self.all_optima['max'] = self.maxima_t
        self.all_optima['min'] = self.minima_t

        other_min = []
        for mn in self.minima_t:
            if mn != self.center_opt['min']:
                other_min.append(mn)
        self.other_opt['min']=other_min  
        other_max = []
        for mx in self.maxima_t:
            if mx != self.center_opt['max']:
                other_max.append(mx)
        self.other_opt['max']=other_max

    def get_num_optima(self, opt):
        return self.num_opt[opt]
        
    def get_optimum(self, opt, ind):
        if self.center_opt[opt] is None:
            return None
        if ind == 0:
            return self.center_opt[opt]
        else:
            out = None
            if ind < 0:
                outs = sorted(i for i in self.other_opt[opt] if i < self.center_opt[opt])
                if abs(ind )<len(outs):
                    out = outs[ind]
            if ind > 0:
                outs = sorted(i for i in self.other_opt[opt] if i > self.center_opt[opt])
                if abs(ind )<len(outs):
                    out = outs[ind-1]
            return out

    def get_optimum_abs_ind(self, opt, ind):
        return self.all_optima[opt][ind]

    def reset_optimum(self):
        self.init_optima()

    

    def set_optimum(self, opt, t ):
        if t == self.center_opt[opt]:
            self.center_opt[opt] = None
            temp_other_opt = self.other_opt[opt]
            temp_other_opt.append(t)
            self.other_opt[opt] = sorted(temp_other_opt)
        else:
            temp_opt = self.center_opt[opt]
            if not temp_opt is None:
                temp_other_opt = self.other_opt[opt]
                other_opt_ind = np.argmin(abs(np.asarray(temp_other_opt)-t))
                self.other_opt[opt].pop(other_opt_ind)
                self.center_opt[opt]= t
                self.other_opt[opt].append(temp_opt)
                temp_other = self.other_opt[opt]
                self.other_opt[opt] = sorted(temp_other)
            else:
                self.center_opt[opt] = t
                temp_other_opt = self.other_opt[opt]
                other_opt_ind = np.argmin(abs(np.asarray(temp_other_opt)-t))
                self.other_opt[opt].pop(other_opt_ind)


class ArrowPlotModel():
    def __init__(self):
        
        self.optima = {}


    def add_result_from_file(self, filename):
        data = self.read_result_file(filename)
        self.add_freq(data)

    def get_other_data_points(self, opt):
        optima = self.optima
        xData = []
        yData = []
        for freq in optima:
            pt  = optima[freq].other_opt[opt]
            for p in pt:
                xData.append(1/freq)
                yData.append(p)

        return xData, yData

    def get_opt_data_points(self, opt, ind=0):
        optima = self.optima
        xData = []
        yData = []
        for freq in optima:
            pt  = optima[freq].get_optimum(opt,ind)
            
            if pt is not None:
                xData.append(1/freq)
                yData.append(pt)
        return xData, yData

    def auto_sort_optima(self, opt):
        '''
        finds the line with the lowest slope, sets the points on that line as the center optima
        '''
        freqs = list(self.optima.keys())
        
        self.optima[freqs[0]].reset_optimum()
        t = self.optima[freqs[0]].get_optimum(opt,0)

        for freq in freqs:
            if not self.optima[freq].get_optimum(opt,0) is None:

                scan_range = range(self.optima[freq].get_num_optima(opt))
                actual_range = []
                next_t = []
                for i in scan_range:
                    o = self.optima[freq].get_optimum_abs_ind(opt,i)
                    if o is not None:
                        next_t.append(o)
                        actual_range.append(i)
                diff = abs(np.asarray(next_t)-t)
                min_diff_ind = np.argmin(diff)
                t = next_t[min_diff_ind]
                current_opt_t = self.optima[freq].get_optimum(opt, 0)
                if t != current_opt_t:
                    self.optima[freq].set_optimum(opt, t)
        
        lines_ind = [0,-1,1]
        line_slopes = []
        for line_ind in lines_ind:
            x, y, fit= self.get_line(opt,line_ind)
            line_slopes.append(fit[0])
        min_slope_ind = lines_ind[np.argmin(abs(np.asarray(line_slopes)))]
       
        if min_slope_ind != 0:
            for freq in freqs:
                best_opt = self.optima[freq].get_optimum(opt, min_slope_ind)
                self.optima[freq].set_optimum(opt, best_opt)


    def clear(self):
        self.__init__()


    def read_result_file(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)

        return data

    

    def get_line(self, opt, ind=0):
        '''
        opt: 'min' or 'max
        ind: -n to n, with 0 being the most horizontal line in the arrow plot
        '''
        xMax,yMax = self.get_opt_data_points(opt,ind)
        
        fit = self.fit_line(xMax,yMax)
        zero = fit[1]
        
        Xmax = max(1/np.asarray(list(self.optima)))
        Ymax = zero+Xmax*fit[0]
        Xmin = Xmax* -0.05
        Ymin = zero+Xmin*fit[0]
        X = [Xmin, Xmax]
        Y = [Ymin, Ymax]
        return X, Y, fit


    def set_optimum(self, opt, t, f_inv):
        
        keys = list(self.optima.keys())
        freqs = abs(np.asarray(keys) - 1/f_inv)
        ind = np.argmin(freqs)
        freq = keys[ind]
        self.optima[freq].set_optimum(opt, t)

    def fit_line(self, X, Y):
        fit = np.polyfit(X,Y,1)
        return fit

    def set_all_freqs(self, correlations):
        self.clear()
        freqs = []

        for correlation in correlations:
            freq = correlation['frequency']
            fname = correlation['filename_waveform']
            freqs.append((freq, correlation))
        
        freqs = Sort_Tuple(freqs, 0)
        for freq in freqs:
            correlation = freq[1]
        
            self.add_freq(correlation)

    
            
    def add_freq(self, data):
        freq = data['frequency']

        filename_waveform = data['filename_waveform']
        if 'correlation' in data:
            correlation_optima = data['correlation']
        else:
            correlation_optima = data
        data_pt = optima(correlation_optima, freq, filename_waveform)
        self.optima[freq]=data_pt
        

    '''def save_result(self, filename):
        
        data = {'frequency':self.freq,'minima_t':list(self.minima[0]),'minima':list(self.minima[1]), 
                            'maxima_t':list(self.maxima[0]),'maxima':list(self.maxima[1])}
        
        if filename.endswith('.json'):
            with open(filename, 'w') as json_file:
                json.dump(data, json_file,indent = 2)    '''

    
   

def index_of_nearest(values, value):
    items = []
    for ind, v in enumerate(values):
        diff = abs(v-value)
        item = (diff, v, ind)
        items.append(item)
    def getKey(item):
        return item[0]
    s = sorted(items, key=getKey)
    closest = s[0][1]
    closest_ind = s[0][2]
    return closest_ind


def get_optima(xData,yData, optima_type=None):
    f = None
    if optima_type == 'min':
        f = less
    elif optima_type == 'max':
        f = greater
    if f is not None:
        optima_ind = argrelextrema(yData, f)
        optima_x = xData[optima_ind]
        optima_y = yData[optima_ind]
        return optima_x, optima_y
    return ([],[])

def get_local_optimum(x, xData, yData, optima_type=None):

    if len(xData) and len(yData):
        pind = get_partial_index(xData,x)
        if pind is None:
            return None
        pind1 = int(pind-100)
        pind2 = int(pind +100)
        xr = xData#[pind1:pind2]
        
        yr = yData#[pind1:pind2]
        # for local maxima
        maxima_ind = argrelextrema(yr, greater)
        maxima_x = xr[maxima_ind]
        maxima_y = yr[maxima_ind]

        minima_ind = argrelextrema(yr, less)
        minima_x = xr[minima_ind]
        minima_y = yr[minima_ind]

        if optima_type == 'minimum':
            optima_pind = index_of_nearest(minima_x,x)
            optima_x = minima_x[optima_pind]
            optima_x = array([optima_x])
            optima_y = array([minima_y[optima_pind]])

        if optima_type == 'maximum':
            optima_pind = index_of_nearest(maxima_x,x)
            optima_x = maxima_x[optima_pind]
            optima_x = array([optima_x])
            optima_y = array([maxima_y[optima_pind]])
        
        if optima_type is None:
            optima_ind = sort(append(maxima_ind, minima_ind))
            optima_x = xr[optima_ind]
            optima_y = yr[optima_ind]
            optima_pind = int(round(get_partial_index(optima_x,x)))
            optima_x = optima_x[optima_pind]
            if optima_x in minima_x:
                optima_type='minimum'
            if optima_x in maxima_x:
                optima_type='maximum'
            optima_x = array([optima_x])
            optima_y = array([optima_y[optima_pind]])
        
       
        return (optima_x, optima_y), optima_type
