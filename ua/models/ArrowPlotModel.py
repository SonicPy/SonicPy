
import os.path, sys
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

class ArrowPlotModel():
    def __init__(self):
        self.frequencies = {}
        self.optima = {}


    def add_result_from_file(self, filename):
        data = self.read_result_file(filename)
        self.add_freq(data)

    def get_other_data_points(self, opt):
        optima = self.optima
        
        xData = []
        yData = []
        for freq in optima:
            pt  = optima[freq][opt]
            for p in pt:
                xData.append(1/freq)
                yData.append(p)

        return xData, yData

    def get_opt_data_points(self, opt):
        optima = self.optima
        xData = []
        yData = []
        for freq in optima:
            pt  = optima[freq][opt]
            
            xData.append(1/freq)
            yData.append(pt)

        return xData, yData

    def clear(self):
        self.__init__()


    def read_result_file(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)

        return data

    def get_max_line(self, opt):
        xMax,yMax = self.get_opt_data_points(opt)
        
        fit = self.fit_line(xMax,yMax)
        zero = fit[1]
        
        Xmax = max(1/np.asarray(list(self.optima)))
        Ymax = zero+Xmax*fit[0]
        X = [0, Xmax]
        Y = [zero, Ymax]
        return X, Y


    def set_optimum(self, opt, t, f_inv):
        
        keys = list(self.optima.keys())
        freqs = abs(np.asarray(keys) - 1/f_inv)
        ind = np.argmin(freqs)
        freq = keys[ind]
        temp_opt = self.optima[freq][opt]
        temp_other_opt = self.optima[freq]['other_'+opt]
        other_opt_ind = np.argmin(abs(np.asarray(temp_other_opt)-t))
        self.optima[freq]['other_'+opt].pop(other_opt_ind)


        self.optima[freq][opt]= t
        self.optima[freq]['other_'+opt].append(temp_opt)
        

        temp_other = self.optima[freq]['other_'+opt]
        self.optima[freq]['other_'+opt] = sorted(temp_other)

    def fit_line(self, X, Y):
        fit = np.polyfit(X,Y,1)
        return fit

                

    def add_freq(self, data):
        freq = data['frequency']
        
        minima = data['minima']
        maxima = data['maxima']
        minima_t = data['minima_t']
        maxima_t = data['maxima_t']

        min_min = minima_t[argmin(minima)]
        max_max = maxima_t[argmax(maxima)]
        self.optima[freq] = {'min': min_min, 'max': max_max}
        other_min = []
        for mn in minima_t:
            if mn != min_min:
                other_min.append(mn)
        other_max = []
        for mx in maxima_t:
            if mx != max_max:
                other_max.append(mx)
        self.optima[freq]['other_min']= other_min
        self.optima[freq]['other_max']= other_max


        self.frequencies[freq]= {'minima_t':data['minima_t'],
                                'minima':data['minima'],
                                'maxima_t':data['maxima_t'],
                                'maxima':data['maxima']}
        

    

    def save_result(self, filename):
        
        data = {'frequency':self.freq,'minima_t':list(self.minima[0]),'minima':list(self.minima[1]), 
                            'maxima_t':list(self.maxima[0]),'maxima':list(self.maxima[1])}
        
        if filename.endswith('.json'):
            with open(filename, 'w') as json_file:
                json.dump(data, json_file,indent = 2)    

    
   

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
        
        #print (optima_x)
        #print (optima_type)
        return (optima_x, optima_y), optima_type