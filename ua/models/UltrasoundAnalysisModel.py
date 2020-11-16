
import os.path, sys
from utilities.utilities import *
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import numpy as np
from numpy import argmax, nan, greater,less, append, sort, array

from scipy import optimize
from scipy.signal import argrelextrema, tukey
from functools import partial
from um.models.tek_fileIO import *
from scipy import signal
import pyqtgraph as pg
from utilities.utilities import zero_phase_bandpass_filter
import json

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

    def filter_echoes(self, l1, r1, l2, r2, freq):
        self.freq = freq
        t = self.t
        spectrum = self.spectrum
        
        tukey_alpha = 0.2
        
            
        # get partial indeces lo and hi for echo 1 and 2  
        pilo1 = int(get_partial_index(t,l1))
        pihi1 = int(get_partial_index(t,r1))

        pilo2 = int(get_partial_index(t,l2))
        pihi2 = int(get_partial_index(t,r2))

        echo1 = np.asarray(spectrum)[pilo1:pihi1]
        echo2 = np.asarray(spectrum)[pilo2:pihi2]

        echo1_max = max(echo1)
        echo2_max = max(echo2)
        max_ratio = echo1_max/echo2_max

        tk1 = tukey(len(echo1), tukey_alpha)
        tk2 = tukey(len(echo2), tukey_alpha)

        echo1_tk = echo1*tk1
        echo2_tk = echo2*tk2

        zero_pad1 = np.zeros(int(len(spectrum)))
        zero_pad2 = np.zeros(int(len(spectrum)))

        zero_pad1[pilo1:pihi1] = echo1_tk
        zero_pad2[pilo2:pihi2] = echo2_tk

        [_,filtered1] = zero_phase_bandpass_filter([t,zero_pad1],freq-freq*0.1,freq+freq*0.05, 1)
        [_,filtered2] = zero_phase_bandpass_filter([t,zero_pad2],freq-freq*0.1,freq+freq*0.05, 1)

        self.filtered1 = (t, filtered1)
        self.filtered2 = (t, filtered2)
        


        '''shift_range = len(t1)
        cross_corr = []
        for shift in range(shift_range):
            
            echo2_shifted = filtered2[pilo2-int(shift_range/2)+shift:pihi2-int(shift_range/2)+shift]*tk2
            c = np.correlate(echo1_filtered, echo2_shifted)[0]
            cross_corr.append(c)'''

    def find_echo_bounds(self, echo):
        m = max(abs(echo))
        echo_norm = abs(echo/m)
        lb = np.argmax(echo_norm> 0.05)
        rb = len(echo)- np.argmax(np.flip(echo_norm)>0.05)
        return lb, rb

    def cross_correlate(self):
        echo1 = self.filtered1[1]
        echo2 = self.filtered2[1]
        max1_ind = np.argmax(echo1)
        max2_ind = np.argmax(echo2)
        lb1, rb1 = self.find_echo_bounds(echo1)
        lb2, rb2 = self.find_echo_bounds(echo2)
        echo1_sub = echo1[lb1:rb1]
        echo2_sub = echo2[lb2:rb2]
        distance = max(max1_ind, max2_ind) - min(max1_ind, max2_ind)
        #print(distance)


        shift_range = int((rb1-lb1)/2)*2
        cross_corr = []
        shifts =[]
        for shift in range(shift_range):
            distance_shifted = int(distance-int(shift_range/2))+shift
            echo2_sub_shifted = echo2[distance_shifted+lb1:distance_shifted+rb1]
            c = np.correlate(echo1_sub, echo2_sub_shifted)[0]
            cross_corr.append(c)
            shifts.append(distance_shifted)
        self.cross_corr = np.asarray(cross_corr)
        dt = self.t[1]-self.t[0]
        self.cross_corr_shift = np.asarray(shifts) * dt

    def exract_optima(self):
        corr = self.cross_corr
        lag = self.cross_corr_shift

        self.minima = get_optima(lag,corr,optima_type='min')
        self.maxima = get_optima(lag,corr,optima_type='max')

    def save_result(self, filename):
        
        data = {'frequency':self.freq,'minima_t':list(self.minima[0]),'minima':list(self.minima[1]), 
                            'maxima_t':list(self.maxima[0]),'maxima':list(self.maxima[1])}
        
        if filename.endswith('.json'):
            with open(filename, 'w') as json_file:
                json.dump(data, json_file,indent = 2)    

    def calculate_data_bkp(self, c1, c2):
        
        
        if t is not None and spectrum is not None:
            
            cor_range = 250
            
            pilo1 = int(get_partial_index(t,c1))-int(cor_range/2)
            pihi1 = int(get_partial_index(t,c1))+int(cor_range/2)

            pilo2 = int(get_partial_index(t,c2))-int(cor_range/2)
            pihi2 = int(get_partial_index(t,c2))+int(cor_range/2)
            

            picenter2 = int(get_partial_index(t,c2))

            echo1 = np.asarray(spectrum)[pilo1:pihi1]
            echo2 = np.asarray(spectrum)[pilo2:pihi2]
            echo1_max = max(echo1)
            echo2_max = max(echo2)
            max_ratio = echo1_max/echo2_max
            

            pg.plot(np.asarray(echo1), title="echo1")
            t1 = np.asarray(t)[pilo1:pihi1]
        
            shift_range = 30
            cross_corr = []
            for shift in range(shift_range):
                pilo2 = picenter2 - int(cor_range/2) + int((shift-shift_range/2))
                pihi2 = picenter2 + int(cor_range/2) + int((shift-shift_range/2))
                echo2 = np.asarray(spectrum)[pilo2:pihi2]
                c = np.correlate(echo1/echo1_max, echo2/echo2_max)[0]/cor_range
                cross_corr.append(c)

            pg.plot(np.asarray(cross_corr), title="cross_corr")
            
            y_data=np.asarray(cross_corr)
            n = np.asarray(range(len(cross_corr)))
            params, params_covariance = optimize.curve_fit(self.fit_func, n, y_data,p0=[.99,.011,.1, .1])
            fitted = self.fit_func(n, params[0], params[1], params[2], params[3])

            
            pg.plot(np.asarray(fitted), title="fit")

            print (params)
            a = params[0]
            b = params[1]
            c = params[2]
            x_max = None
            neg_factor = 1
            max_found = False
            
            
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
            echo2 = np.asarray(spectrum)[pilo2:pihi2]
            echo1_max = max(echo1)
            
            if neg_factor == -1: # invert?
                echo2 = echo2 * -1
            echo2_max = max(echo2)
            norm = echo1_max/echo2_max
            plot1_overlay = echo2 * norm
            plot2_overlay = echo1 * neg_factor /norm
            

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