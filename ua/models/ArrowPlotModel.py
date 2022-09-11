
import os.path, sys
from this import d
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
from ua.models.EchoesResultsModel import EchoesResultsModel

class optima():
    def __init__(self, data, frequency, filename_waveform, wave_type, centers, init = True):
        
        self.filename_waveform = filename_waveform
        self.wave_type = wave_type
        self.freq = frequency
        self.minima = data['minima']
        self.maxima = data['maxima']
        self.minima_t = data['minima_t']
        self.maxima_t = data['maxima_t']

        self.num_opt = {}
        self.all_optima = {}
        self.center_opt = centers
        
        if init:
            self.init_optima()

    def package_for_saving(self):
        package = {} 
        package['filename_waveform'] = self.filename_waveform
        package['num_opt'] = self.num_opt
        package['all_optima'] = self.all_optima
        package['center_opt'] = self.center_opt
        package['freq']= self.freq
        return package

    def restore_from_package(self, package):
        self.num_opt = package['num_opt']
        self.all_optima = package['all_optima']
        self.center_opt = package['center_opt']
        
    def init_optima(self):
        
        self.other_opt={}
        if self.center_opt == {}:
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
        # ind = center optimum
        # ind < or > 0, index above or below the center optimum
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


class ArrowPlotsModel():
    def __init__(self, results_model: EchoesResultsModel):

        self.arrow_plot_models_p = {}
        self.arrow_plot_models_s = {}
        self.results_model = results_model
        self.package_p = {}
        self.package_s = {}
        
    def restore_tof_results(self, package):
        print(package)

    def get_arrow_plot(self, cond, wave_type):

        if wave_type == 'P':
            arrow_plot_models = self.arrow_plot_models_p
        elif wave_type == 'S':
            arrow_plot_models = self.arrow_plot_models_s
        if cond in arrow_plot_models:
            arrow_plot = arrow_plot_models[cond]
        else:
            arrow_plot = arrow_plot_models[cond] = ArrowPlot(self.results_model)
            arrow_plot.condition = cond

        return arrow_plot

    
    

    def refresh_all_freqs(self, condition,wave_type):
        arrow_plot = self.get_arrow_plot(condition, wave_type)

        echoes_by_condition = self.results_model.get_echoes_by_condition(condition, wave_type)
        freqs = []
        for correlation in echoes_by_condition:
            freq = correlation['frequency']
            fname = correlation['filename_waveform']
            freqs.append((freq, correlation))
        
        freqs = Sort_Tuple(freqs, 0)
        for freq in freqs:
            correlation = freq[1]
        
            arrow_plot.add_freq(correlation)

    

    def delete_optima(self, condition, wave_type, freq):
        arrow_plot = self.get_arrow_plot(condition, wave_type)

        if freq in arrow_plot.optima:
            del arrow_plot.optima[freq]

    def clear_condition(self, clear_info):

        wave_type = clear_info['wave_type']
        condition = clear_info['condition']

        arrow_plot = self.get_arrow_plot(condition, wave_type)

        freqs = list(arrow_plot.optima.keys())
        for freq in  freqs:
            del arrow_plot.optima[freq]
            

class ArrowPlot():
    def __init__(self,results_model: EchoesResultsModel):

        self.results_model = results_model
        self.condition = ''

        self.optima = {}
        self.line_plots = {}
        self.result = {}

        self.package = {}

    def clear(self):
        self.__init__(self.results_model)

    def package_optima(self):
        package = {}
        _optima = {}
        for opt in self.optima:
            _optima [opt ]= self.optima[opt].package_for_saving()

        package['condition'] = self.condition
        package['optima']=_optima

        output_line_plots = {}
        for key in self.line_plots:
            plot = self.line_plots[key]

            line_plots_x = plot[0].tolist()
            # every third element is a NaN, remove NaNs before packaging
            del line_plots_x[3-1::3]
            line_plots_y = plot[1].tolist()
            # every third element is a NaN, remove NaNs before packaging
            del line_plots_y[3-1::3]
            output_line_plots[key] = [line_plots_x, line_plots_y]
        package['line_plots']= output_line_plots
        package['result']=self.result
        
        return package

    def restore_optima(self, package):
        self.condition = package['condition']
        _optima= package['optima']

        
        restored_plots = {}
        for key in package['line_plots']:
            plot = package['line_plots'][key]
            line_plots_x = plot[0] 
            line_plots_y = plot[1]
            lp_len = len(line_plots_x)
            nan_list_x = [np.nan]*lp_len
            nan_list_y = [np.nan]*lp_len

            line_plots_x = interleave_lists(line_plots_x, nan_list_x)
            line_plots_y = interleave_lists(line_plots_y, nan_list_y)

            plots = [np.asarray(line_plots_x), np.asarray(line_plots_y)]

            restored_plots[key] = plots

        self.line_plots = restored_plots
        self.result = package['result']
        for opt in _optima:
            self.optima[opt].restore_from_package(_optima[opt])

            
    def add_freq(self, data):
        freq = data['frequency']

        filename_waveform = data['filename_waveform']
        wave_type = data['wave_type']
        correlation_optima = data['correlation']
        centers_in_data = 'centers' in data
        if centers_in_data:
            centers = data['centers']
        else:
            centers = {}

        if not freq in self.optima:
            data_pt = optima(correlation_optima, freq, filename_waveform, wave_type, centers)
            self.optima[freq]=data_pt
        else:
            data_pt = self.optima[freq]
            stored_filename_waveform = data_pt.filename_waveform
            stored_wave_type = data_pt.wave_type
            stored_centers = data_pt.center_opt
            
            same = stored_filename_waveform == filename_waveform and \
                           stored_wave_type == wave_type and \
                           self.compare_optima(correlation_optima, data_pt) and \
                            centers == stored_centers
            if not same:
                data_pt = optima(correlation_optima, freq, filename_waveform, wave_type, centers)
                self.optima[freq]=data_pt

    def compare_optima(self, opt1, opt2):
        '''comparison between a dict and an 'optima' object based on stored values
        used in order to decide if to create a new object or reuse existing'''
        equal = opt1['minima'] ==   opt2.minima and \
                opt1['maxima'] ==   opt2.maxima and \
                opt1['minima_t'] == opt2.minima_t and \
                opt1['maxima_t'] == opt2.maxima_t 
        return equal

    def delete_optima(self, cond, freq):
        del self.optima[freq]

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


    def set_optimum(self, opt, t, f_inv):
        
        keys = list(self.optima.keys())
        freqs = abs(np.asarray(keys) - 1/f_inv)
        ind = np.argmin(freqs)
        freq = keys[ind]
        self.optima[freq].set_optimum(opt, t)

    def auto_sort_optima(self, opt):
        '''
        finds the line with the lowest slope, sets the points on that line as the center optima
        '''
        freqs = list(self.optima.keys())
        
        self.optima[freqs[0]] .reset_optimum() 

        # use for loop to find lowest frequency with a selected optimum, 
        # frequencies with all optima deselected will return t as None
        # then use that frequency as the starting t 
        for ind in range(len(freqs)):
            t = self.optima[freqs[ind]].get_optimum(opt,0)
            if t != None:
                break

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

    def calculate_lines(self, opt = 'max'):
        arrow_plot = self
        
        num_pts = len(arrow_plot.optima)
        if num_pts > 2:
            
            indexes = [-2,-1,0,1,2]
            X = []
            Y = []
            fits = []
            for i in indexes:
                x, y, fit = arrow_plot.get_line(opt,i)
                fits.append(fit[1])
                X = X +x
                Y = Y+y
                X = X +[np.nan]
                Y = Y+[np.nan]
            self.line_plots[opt] = (np.asarray(X),np.asarray(Y))
            
            s = np.std(np.asarray(fits))

            time_delay = round(sum(np.asarray(fits))/len(fits)*1e6,5)
            time_delay_std = round(s*1e6,5)

            result = {'time_delay':time_delay, 'time_delay_std':time_delay_std}

            
            self.result[opt] = result

            self.package = self.package_optima()
        else:
            self.error_not_enough_datapoints()

    

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


    def fit_line(self, X, Y):
        fit = np.polyfit(X,Y,1)
        return fit

    def error_not_enough_datapoints(self):
        pass
   
def interleave_lists(a_list, b_list):
    result = []
    while a_list and b_list:
        result.append(a_list.pop(0))
        result.append(a_list.pop(0))
        result.append(b_list.pop(0))
    result.extend(a_list)
    result.extend(b_list)
    return result
    

def read_result_file( filename):
        with open(filename) as json_file:
            data = json.load(json_file)

        return data



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
