import os.path, sys
import numpy as np
from scipy.signal import tukey

from models.tek_fileIO import *
from utilities.utilities import *
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import sys
from functools import partial
import json




def g_wave(t_array, A, f_0,sigma,x,c,f_min, f_max):

    psi = []
    integral_pts = 50
    rng = f_max - f_min
    step = rng / integral_pts
    f_0 = f_0 * 2*np.pi
    sigma = sigma * 2*np.pi
    for t in t_array:
        func =  partial(my_func,f_0,sigma,t,c,x)
        
        f_integral = []
        for i in range (integral_pts):
            f = i* step + f_min

            ff = func(f) * step
            f_integral.append(ff)
        s = sum(f_integral) / (sigma * np.pi)
        psi.append(s)

    return psi 


def my_func(f_0,sigma, t,c,x,f):
    f = np.sin(f*(t-x/c))*np.exp(-1*(f-f_0)**2/(2*sigma**2))

    return f

def make_wave(freq, total_time, points, symmetric=True, quarter_shift = False):
    period = 1/freq
    n_periods = total_time / period
    if quarter_shift:
        offset = np.pi/2
    else:
        offset = 0
    if symmetric:
        shift = np.pi*n_periods - offset
    else:
        shift = 0
    points_per_period = round(points/n_periods)
    delta_t = total_time/points
    range_points = np.asarray(range(points))
    time = range_points * delta_t
    wave = np.sin(2*np.pi*freq*time - shift)
    return time, wave, points_per_period, shift

def scale_waveform(waveform):
    fy = waveform[1]
    fmx = max(fy)
    fy_scaled=fy/fmx
    mn = min(fy_scaled)
    fy_scaled = fy_scaled -mn
    mx = max(fy_scaled)
    fy_scaled = fy_scaled/mx * 16000
    fy_scaled = fy_scaled.astype(int)
    return [waveform[0],waveform[1]]

def my_filter(t, y, pad, tukey_alpha,points_per_period, highcut):
    data_length = len(t)
    del_t = t[1]-t[0]
    mn = min(y)
    mx = max(y)
    av = (mn+mx)/2
    zero = [av]*int(data_length*pad)
    data = np.asarray(zero + list(y)+zero)
    tk = tukey(len(y), tukey_alpha)
    tk_data = np.asarray(zero + list(tk)+zero)
    t = np.asarray(range(len(data))) * del_t
    (t,fltrd) = zero_phase_lowpass_filter([t,data*tk_data], highcut, 1)
    mx = max(fltrd)
    mn = abs(min(fltrd))
    mx = max(mx,mn)
    fltrd = fltrd / mx
    return [t, data*tk_data], [t,fltrd],[t, data]



def main():
    points = 1000
    f = 15e6
    duration = 100e-9
    tukey_alpha = .2
    highcut = f * 1
    pad = 3
    symmetric = False
    quarter_shift = False

    app = QtGui.QApplication([])
    

    
    #mw = QtGui.QMainWindow()
    #mw.resize(800,800)

    win = pg.GraphicsLayoutWidget()
    win.resize(1000,600)
    win.setWindowTitle('burst_waveform')

    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)


    p2 = win.addPlot()
    p3 = win.addPlot()

    data = []

    print (f)

    for ind in range(50):
        fr = f + ind * 1e6
        t, y, points_per_period, shift = make_wave(fr,duration,points,symmetric,quarter_shift)
        highcut = fr * 3
        expanded, filtered, padded = my_filter(t, y, pad, tukey_alpha,points_per_period,  highcut)  
        #p2.plot(filtered[0],filtered[1], pen=(255,0,0))
        #p2.plot(expanded[0],expanded[1], pen=(0,255,0))
        #p2.plot(padded[0],padded[1], pen=(0,255,255))
        data.append(filtered[1])

    s = np.sum(data,axis = 0)


    t_0 = 0
    t_max = 180e-9
    pts = 1000
    step = (t_max-t_0)/pts
    t = np.asarray(range(pts)) * step + t_0
    ss = g_wave(t,1,45e6, 20e6,12e-4,5000,-1100e6,1100e6)


    ss_fft = fft_sig(t,ss)


    p2.plot(t,ss, pen=(0,255,0))
    p3.plot(ss_fft[0],ss_fft[1], pen=(0,255,255))


    
    for ind in range(10):
        fr = f + ind * 5e6
        sf = zero_phase_bandpass_filter([t,ss],fr-fr*0.05, fr+fr*0.05, 1)
        p2.plot(sf[0],sf[1], pen=(255,0,0))
    
    print(fr)
    data = np.asarray(data).T


    imv = pg.ImageView()
    win2 = QtGui.QMainWindow()
    win2.setCentralWidget(imv)
    win2.show()
    win2.setWindowTitle('pyqtgraph example: ImageView')

    imv.setImage(data )



    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    
    main()
   
    
        
