import numpy as np
from scipy import signal
from scipy import blackman, nanmean
from scipy.signal import hilbert
from scipy.fftpack import rfft, irfft, fftfreq, fft
import scipy.fftpack
import csv
from um.models.tek_fileIO import read_tek_csv, read_tek_csv_files_2d, read_ascii_scope_files_2d
import math
from PyQt5 import QtCore, QtWidgets
import time, os

def read_multiple_spectra(filenames, subsample = 1):
    spectra = []
    f = filenames[0]
    X,Y = read_tek_csv(f, return_x=True, subsample=subsample)
    
    for f in filenames:
        Y = read_tek_csv(f, return_x=False, subsample=subsample)
        y = Y
        
        spectra.append(y)
    return spectra, X

def read_multiple_spectra_dict(filenames, subsample = 1 ):

    spectra = []
    f = filenames[0]
    X,Y = read_tek_csv(f, return_x=True, subsample=subsample)
    x = np.asarray(X)
    missing_couner = 1
    missing_waveform = [np.asarray([]),np.asarray([])]
    for d, f in enumerate(filenames):
        
        if f is not None and len(f):
            Y = read_tek_csv(f, return_x=False, subsample=subsample)
            y = np.asarray(Y)
            spectra.append({ 'filename':f,'waveform':[x, y]})
        else:
            spectra.append({ 'filename':'missing_file_'+str(missing_couner),'waveform':missing_waveform})
        
        
    return spectra

def read_2D_spectra_dict(filenames, subsample = 1 ):

    spectra = []
    
    file  = os.path.split(filenames[0])[-1]
    if '.' in file:
        ext = '.' + file.split('.')[-1]
    else:
        ext = ''

    if ext == '.csv':
        r = read_tek_csv_files_2d(filenames, subsample=subsample)
    elif ext == '':
        r = read_ascii_scope_files_2d(filenames, subsample = subsample)
    
    for d, f in enumerate(filenames):
        
       
        spectra.append({ 'filename':f,'waveform':[r['time'], r['voltage'][d]]})
        
        
    return spectra


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
    instantaneous_phase = np.unwrap(np.angle(analytic_signal))
    
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
    phase_shift = instantaneous_phase - offsetTerm 
    return amplitude_envelope, phase_shift, instantaneous_frequency

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