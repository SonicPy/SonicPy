
from operator import sub
import os.path, sys, os

from posixpath import basename
from utilities.utilities import *
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import numpy as np
from numpy import argmax, nan, greater,less, append, sort, array

from scipy import optimize
from scipy.signal import argrelextrema, tukey
from functools import partial
from um.models.tek_fileIO import *
from scipy import signal
from scipy.signal import find_peaks
import pyqtgraph as pg
from utilities.utilities import zero_phase_bandpass_filter
import json
from utilities.CARSMath import fit_gaussian, polyfitw

from .. models.SelectedEchoesModel import SelectedEchoesModel


class UltrasoundAnalysisModel():
    def __init__(self):
        self.waveform = None
        self.envelope = None
        self.t = None
        self.spectrum = None
        self.plot1_bg=([],[])
        self.plot2_bg=([],[])
        self.c_diff_optimized = 0
        self.bounds = [[0,0],[0,0]]
        self.freq = 0
        self.wave_type = 'P' # or 'S'
        self.settings = {'tukey_alpha':0.2}

        self.minima = []
        self.maxima = []

    def fit_func(self, x, a, b,c,d):
        '''
        calculated a cosine function, can be used for regression
        '''
        return a * np.cos(b * x+c)+d

    def filter_echo(self, t, spectrum, l, r, freq, freq_range=0.1, order = 3, tukey_alpha=0.2):
        '''
        applies tuckey window and bandpass filter to an echo
        '''
        pilo = int(get_partial_index(t,l))
        pihi = int(get_partial_index(t,r))
        echo = np.asarray(spectrum)[pilo:pihi]
        tk = tukey(len(echo), tukey_alpha)
        echo_tk = echo*tk
        zero_pad = np.zeros(len(spectrum))
        zero_pad[pilo:pihi] = echo_tk
        filtered = zero_phase_bandpass_filter([t,zero_pad],freq-freq*(freq_range/2),freq+freq*(freq_range/2), order)
        return filtered
    
    def filter_echoes(self, l1, r1, l2, r2, freq):
        '''
        windows and filters selected echoes
        '''
        self.freq = freq
        self.bounds = [[l1, r1],[l2, r2]]
        t = self.t
        spectrum = self.spectrum
        tukey_alpha = self.settings['tukey_alpha']
        self.filtered1 = self.filter_echo(t,spectrum,l1,r1,freq,tukey_alpha)
        self.filtered2 = self.filter_echo(t,spectrum,l2,r2,freq,tukey_alpha)

    def find_echo_bounds(self, echo, echo_bounds_cutoff = 0.05):
        '''
        input: echo, windowed and filtered echo
        return: left bound (lb) and right bound (rb) for a region 
        the amplitude of the echo is more than echo_bounds_cutoff
        '''
        m = max(abs(echo))
        echo_norm = abs(echo/m)
        lb = np.argmax(echo_norm> echo_bounds_cutoff)
        rb = len(echo)- np.argmax(np.flip(echo_norm)>echo_bounds_cutoff)
        return lb, rb

    def cross_correlate(self):
        '''
        computes correlation values between 
        two echoes for diffeent values of shift
        '''
        echo1 = self.filtered1[1]
        echo2 = self.filtered2[1]
        max1_ind = np.argmax(echo1)
        max2_ind = np.argmax(echo2)
        lb1, rb1 = self.find_echo_bounds(echo1)
        lb2, rb2 = self.find_echo_bounds(echo2)
        echo1_sub = echo1[lb1:rb1]
        echo2_sub = echo2[lb2:rb2]
        distance = max(max1_ind, max2_ind) - min(max1_ind, max2_ind)

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
        '''
        extracts opitima from previusly computed 
        cross correlation between two echoes
        '''
        corr = self.cross_corr
        lag = self.cross_corr_shift

        self.minima = get_optima_peaks(lag,corr,optima_type='min')
        self.maxima = get_optima_peaks(lag,corr,optima_type='max')

    def save_result(self, fname):
        '''
        saves result of correlation between two echoes to file
        '''
        if len(self.minima):
            

            
            data = {'frequency':self.freq,
                        'correlation':{
                        'minima_t':list(np.around(self.minima[0],12)),
                        'minima':list(np.around(self.minima[1],12)), 
                        'maxima_t':list(np.around(self.maxima[0],12)),
                        'maxima':list(np.around(self.maxima[1],12))},
                        'filename_waveform':fname,
                        'echo_bounds':self.bounds,
                        'filter': {'tukey_alpha':self.settings['tukey_alpha']} ,
                        'wave_type':self.wave_type}
            
            saved = True
           
            
            return {'ok':True,'data':data}

        return {'ok': False,'data':{}}



def get_optima_peaks(xData, yData, optima_type = None):
    optima_x, optima_y = [],[]

    if optima_type == 'max':
        fit_yData = yData
      
    elif optima_type == 'min':
       fit_yData = -1*yData
    peaks = find_peaks(fit_yData,height=0)
    optima_ind = peaks[0]

    range_option = 5
        
    for opt_ind in optima_ind:
        if opt_ind > range_option and opt_ind < ((len(xData))+range_option-1):
            opt_x = xData[opt_ind]
            opt_y = yData[opt_ind]
            
            opt_x = get_fractional_max_x(xData,fit_yData,opt_ind, range_option)
            optima_x.append(opt_x)
            optima_y.append(opt_y)
    return (optima_x,optima_y)

def get_fractional_max_x( xData, yData, opt_ind, fit_range):
    near_x = xData[opt_ind]
    fit_x = xData[opt_ind-fit_range:opt_ind+fit_range+1]
    fit_y = yData[opt_ind-fit_range:opt_ind+fit_range+1]
    fit_y = fit_y / np.amax(fit_y) * 1000 # must be rescaled before fitting because looks like fig_gaussian clips values smaller than 1
    g = fit_gaussian(fit_x,fit_y)
    fract_x = g[1]
    if abs(fract_x - near_x)> abs(xData[1]-xData[0])*2:
        # this means the fit failed
        fract_x = near_x
    return fract_x


'''def index_of_nearest(values, value):
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
    return closest_ind'''


'''def get_optima(xData,yData, optima_type=None):
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
    return ([],[])'''

'''def get_local_optimum(x, xData, yData, optima_type=None):

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

        return (optima_x, optima_y), optima_type'''
