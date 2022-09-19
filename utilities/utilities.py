
import numpy as np
from scipy import signal
from scipy import blackman, nanmean
from scipy.signal import hilbert
from scipy.fftpack import fft

import json
import os

import math
import compress_json


def write_data_dict_to_compressed_json(filename, data):
    
    
    compress_json.dump(data, filename)




def write_data_dict_to_json(filename, data):

    with open(filename, 'w') as json_file:
        json.dump(data, json_file,indent = 2)  
        json_file.close()  

def update_data_dict_json(filename, data):
    
    if os.path.isfile(filename):
        with open(filename, 'r') as json_file:
            old_data = json.load(json_file)
            for key in data:
                old_data[key] = data[key]
            new_data = old_data
            json_file.close()  
    else:
        new_data = data
    with open(filename, 'w') as json_file:
        
        json.dump(new_data, json_file,indent = 2)  
        json_file.close()  

def read_result_file( filename):
        with open(filename) as json_file:
            data = json.load(json_file)
            json_file.close()

        return data

def read_result_file_compressed( filename):
        data = compress_json.load(filename)

        return data


def butter_bandstop_filter(data, lowcut, highcut, order):
    x = data[0]
    x_interval = x[1]-x[0]
    if x_interval > 0:
        fs = 1/(x_interval)
        y = data[1]
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq

        i, u = signal.butter(order, [low, high], btype='bandstop')
        y = signal.lfilter(i, u, y)
        return x, y
    return None

def butter_lowpass_filter(data, lowcut,  order):
    x = data[0]
    x_interval = x[1]-x[0]
    if x_interval > 0:
        fs = 1/(x_interval)
        y = data[1]
        nyq = 0.5 * fs
        low = lowcut / nyq
        

        i, u = signal.butter(order, low, btype='low')
        y = signal.lfilter(i, u, y)
        return x, y
    return None

def zero_phase_lowpass_filter(data, lowcut, order):
    x = data[0]
    x_interval = x[1]-x[0]
    if x_interval > 0:
        fs = 1/(x_interval)
        y = data[1]
        nyq = 0.5 * fs
        low = lowcut / nyq
        

        i, u = signal.butter(order, low, btype='low')
        y = signal.filtfilt(i, u, y)
        return x, y
    return None

def zero_phase_highpass_filter(data, highcut, order):
    x = data[0]
    x_interval = x[1]-x[0]
    if x_interval > 0:
        fs = 1/(x_interval)
        y = data[1]
        nyq = 0.5 * fs
        high = highcut / nyq
        

        i, u = signal.butter(order, high, btype='high')
        y = signal.filtfilt(i, u, y)
        return x, y
    return None

def zero_phase_bandstop_filter(data, lowcut, highcut, order):
    x = data[0]
    x_interval = x[1]-x[0]
    if x_interval > 0:
        fs = 1/(x_interval)
        y = data[1]
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq

        i, u = signal.butter(order, [low, high], btype='bandstop')
        y = signal.filtfilt(i, u, y)
        return x, y
    return None

def zero_phase_bandpass_filter(data, lowcut, highcut, order):
    x = data[0]
    x_interval = x[1]-x[0]
    if x_interval > 0:
        fs = 1/(x_interval)
        y = data[1]
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq

        i, u = signal.butter(order, [low, high], btype='bandpass')
        y = signal.filtfilt(i, u, y)
        return x, y
    return None

def bessel_lowpass_filter(data, lowcut,  order):
    x = data[0]
    x_interval = x[1]-x[0]
    if x_interval > 0:
        fs = 1/(x_interval)
        y = data[1]
        nyq = 0.5 * fs
        low = lowcut / nyq
        

        i, u = signal.bessel(order, low, btype='low')
        y = signal.lfilter(i, u, y)
        return x, y
    return None


def signal_region_by_x(X, Y, xmin=None, xmax=None):
    if xmin == None:
        xmin = min(X)
    if xmax == None:
        xmax = max(X)
    mask = (X > xmin) * (X < xmax)
    x = X[mask]
    y = Y[mask]
    return x, y, mask

def rebin(data, width):

    
    x = data
   
    R = width

    pad_size = math.ceil(float(x.size)/R)*R - x.size

    x_padded = np.append(x, np.zeros(pad_size)*np.NaN)
    x = x_padded

    x = x.reshape(-1, R)
    x = nanmean(x.reshape(-1,R), axis=1)
 

    
    return x

def generate_source(del_x, freq, N=6, window=True):
    period = 1/(freq*1e+6)
    p6 = period *N
    samples = int(p6 / del_x)
    xsource = np.arange(samples) * del_x
    if window:
        shift = 0.25
    else:
        shift = -0.25
    source = np.sin(2*np.pi*(freq*1e+6 * xsource + shift))
    if window:
        
        w = blackman(samples)
        source = source * w
    return xsource, source

def demodulate(x,y, freq=None, carrier_known=False):

    
    analytic_signal = hilbert(y)
    amplitude_envelope = np.abs(analytic_signal)
    '''instantaneous_phase = np.unwrap(np.angle(analytic_signal))
    
    if freq == None:
        instantaneous_frequency = None
    else: 
        instantaneous_frequency = (np.diff(instantaneous_phase) / (2.0*np.pi) *  10e6)
    receiverKnowsCarrier = carrier_known

    t=x
    beta = 0 #constant carrier phase offset
    #If receiver don't know the carrier, estimate the subtraction term
    if receiverKnowsCarrier:
        offsetTerm = 2*np.pi*freq*1e6*t+beta; #if carrier frequency & phase offset is known
    else:
        p = np.poly1d(np.polyfit(t,instantaneous_phase,1)) #linearly fit the instaneous phase
        estimated = p(t) #re-evaluate the offset term using the fitted values
        offsetTerm = estimated             
    phase_shift = instantaneous_phase - offsetTerm '''
    return amplitude_envelope #, phase_shift, instantaneous_frequency

def fft_sig(X, Y):
    # Number of samplepoints
    N = len(X)*2
    # sample spacing
    T = X[1]-X[0]
    x = X/ (2*np.pi)
    y = Y
    yf = fft(y,n = N)
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    xfr = 2.0/N * np.abs(yf[0:N//2])
    return xf, xfr

def cross_correlate_sig(sig, source):
    length = len(source)
    corr = signal.correlate(sig, source, mode='same') / length
    return corr


def save_dict_to_hdf5(dic, filename):
    """
    https://codereview.stackexchange.com/questions/120802/recursively-save-python-dictionaries-to-hdf5-files-using-h5py
    """
    with h5py.File(filename, 'a') as h5file:
        recursively_save_dict_contents_to_group(h5file, '/', dic)

def recursively_save_dict_contents_to_group(h5file, path, dic):
    """
    https://codereview.stackexchange.com/questions/120802/recursively-save-python-dictionaries-to-hdf5-files-using-h5py
    """
    for key, item in dic.items():
        if isinstance(item, (float,int)):
            item = np.float64(item)
        if isinstance(item,(list)):
            item = np.asarray(item, dtype=np.float64)
        if isinstance(item, (np.ndarray, np.int64, np.float64, str, bytes)):
            h5file[path + key] = item
        elif isinstance(item, dict):
            recursively_save_dict_contents_to_group(h5file, path + key + '/', item)
        else:
            print(item)
            raise ValueError('Cannot save %s type'%type(item))

def load_dict_from_hdf5(filename):
    """
    https://codereview.stackexchange.com/questions/120802/recursively-save-python-dictionaries-to-hdf5-files-using-h5py
    """
    with h5py.File(filename, 'r') as h5file:
        return recursively_load_dict_contents_from_group(h5file, '/')

def recursively_load_dict_contents_from_group(h5file, path):
    """
    https://codereview.stackexchange.com/questions/120802/recursively-save-python-dictionaries-to-hdf5-files-using-h5py
    """
    ans = {}
    for key, item in h5file[path].items():
        if isinstance(item, h5py._hl.dataset.Dataset):
            val = item[()]
            if isinstance(val,(np.ndarray)):
                val = list(val)
            ans[key] = val
        elif isinstance(item, h5py._hl.group.Group):
            ans[key] = recursively_load_dict_contents_from_group(h5file, path + key + '/')
    return ans