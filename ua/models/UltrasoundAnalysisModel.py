
import os.path, sys
from utilities.utilities import *
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import numpy as np
from numpy import argmax, nan, greater,less, append, sort, array

from scipy import optimize
from scipy.signal import argrelextrema
from functools import partial
from um.models.tek_fileIO import *
from scipy import signal

class UltrasoundAnalysisModel():
    def __init__(self):
        self.waveform = None
        self.envelope = None
        self.t = None
        self.spectrum = None
        self.plot1_bg=([],[])
        self.plot2_bg=([],[])
        self.c_diff_optimized = 0

    def fit_func(self, x, a, b,c,d):
        return a * np.cos(b * x+c)+d

    def calculate_data(self, c1, c2):
        t = self.t
        spectrum = self.spectrum
        cor_range = 250
        
        pilo1 = int(get_partial_index(t,c1))-int(cor_range/2)
        pihi1 = int(get_partial_index(t,c1))+int(cor_range/2)

        pilo2 = int(get_partial_index(t,c2))-int(cor_range/2)
        pihi2 = int(get_partial_index(t,c2))+int(cor_range/2)
        

        picenter2 = int(get_partial_index(t,c2))

        slice1 = np.asarray(spectrum)[pilo1:pihi1]
        slice2 = np.asarray(spectrum)[pilo2:pihi2]
        slice1_max = max(slice1)
        slice2_max = max(slice2)
        max_ratio = slice1_max/slice2_max
        

        #pg.plot(np.asarray(slice1), title="slice1")
        t1 = np.asarray(t)[pilo1:pihi1]
    
        shift_range = 30
        cross_corr = []
        for shift in range(shift_range):
            pilo2 = picenter2 - int(cor_range/2) + int((shift-shift_range/2))
            pihi2 = picenter2 + int(cor_range/2) + int((shift-shift_range/2))
            slice2 = np.asarray(spectrum)[pilo2:pihi2]
            c = np.correlate(slice1/slice1_max, slice2/slice2_max)[0]/cor_range
            cross_corr.append(c)

        #pg.plot(np.asarray(cross_corr), title="cross_corr")
        
        y_data=np.asarray(cross_corr)
        n = np.asarray(range(len(cross_corr)))
        params, params_covariance = optimize.curve_fit(self.fit_func, n, y_data,p0=[.99,.011,.1, .1])
        fitted = self.fit_func(n, params[0], params[1], params[2], params[3])

        
        #pg.plot(np.asarray(fitted), title="fit")

        #print (params)
        a = params[0]
        b = params[1]
        c = params[2]
        x_max = None
        neg_factor = 1
        max_found = False
        
        #print (params)
        if a >= 0:
            for n in range(15):
                x_max = (2*np.pi * (n-7) -c )/b
                if x_max >= 0 and x_max <= len(cross_corr):
                    #print(x_max)
                    #print(n)
                    max_found = True
                    break
            if max_found:
                p_val = x_max - shift_range/2
            else:
                for n in range(15):
                    x_max = (2*np.pi *(n-7) -c + np.pi)/b
                    if x_max >= 0 and x_max <= len(cross_corr):
                        #print(x_max)
                        #print(n)
                        neg_factor = -1
                        break
                p_val = x_max - shift_range/2

        else:
            for n in range(15):
                x_max = (2*np.pi *(n-7) -c + np.pi)/b
                if x_max >= 0 and x_max <= len(cross_corr):
                    #print(x_max)
                    #print(n)
                    max_found = True
                    break
            if max_found:
                p_val = x_max - shift_range/2
            else:
                for n in range(15):
                    x_max = (2*np.pi * (n-7) -c )/b
                    if x_max >= 0 and x_max <= len(cross_corr):
                        #print(x_max)
                        #print(n)
                        neg_factor = -1
                        break
                p_val = x_max - shift_range/2
            
        if not max_found:
            #print(x_max)
            #print(n)
            pass
        t_step = t[1]-t[2]
        t_max_shift = p_val * t_step

        c1_new_pos = c1+t_max_shift

        self.c_diff_optimized = c2-c1_new_pos


        pilo2 = picenter2 - int(cor_range/2) 
        pihi2 = picenter2 + int(cor_range/2) 
        slice2 = np.asarray(spectrum)[pilo2:pihi2]
        slice1_max = max(slice1)
        
        if neg_factor == -1: # invert?
            slice2 = slice2 * -1
        slice2_max = max(slice2)
        norm = slice1_max/slice2_max
        plot1_overlay = slice2 * norm
        plot2_overlay = slice1 * neg_factor /norm
        

        t2 = np.asarray(t)[pilo2:pihi2]
        plot1_overlay_t = t2 - self.c_diff_optimized
        plot2_overlay_t = t1 + self.c_diff_optimized

        self.plot1_bg = (plot1_overlay_t, plot1_overlay)
        self.plot2_bg = (plot2_overlay_t, plot2_overlay)

  


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


def get_local_optimum(x, xData, yData, optima_type=None):

    if len(xData) and len(yData):
        pind = get_partial_index(xData,x)
        if pind is None:
            return None
        pind1 = int(pind-100)
        pind2 = int(pind +100)
        xr = xData[pind1:pind2]
        
        yr = yData[pind1:pind2]
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