import os.path, sys
import numpy as np


from models.tek_fileIO import *
from utilities.utilities import *


from functools import partial
import json


def make_wave(freq, total_time, points):
    period = 1/freq
    n_periods = total_time / period
    points_per_period = round(points/n_periods)
    delta_t = total_time/points
    range_points = np.asarray(range(points))
    time = range_points * delta_t
    wave = np.sin(2*np.pi*freq*time)
    return time, wave




def get_arb():
    '''
    desc = read_file_TEKAFG3000('3pulse.tfw')
    data_length = desc['data_length']
    binary_waveform = desc['binary_waveform']
    '''
    time, binary_waveform = make_wave(69e6,50e-9,1000)


    #return binary_waveform
    #print(binary_waveform)
    period = int(data_length/3)
    m = int(max(binary_waveform)/2)
    zero = [m]*period
    data = zero + list(binary_waveform)+zero
    print(len(data))
    mx = max(data)
    data = np.asarray(data) / mx
    av = np.average(data)
    y = (data - av) * 2
    x = np.asarray(range(len(y))) * 1e-9

    
    filtered = zero_phase_lowpass_filter([x,y], 4000000, 1)
    fy = filtered[1]
    fmx = max(fy)
    fy_scaled=fy/fmx
    mn = min(fy_scaled)
    fy_scaled = fy_scaled -mn
    mx = max(fy_scaled)
    fy_scaled = fy_scaled/mx * 16000
    fy_scaled = fy_scaled.astype(int)
    

    return tuple(fy_scaled)


t, y = make_wave(30e6,50e-9,1000)

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsLayoutWidget()
win.resize(1000,600)
win.setWindowTitle('binary_waveform')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p2 = win.addPlot(title="Multiple curves")
p2.plot(t,y, pen=(255,0,0), name="Red curve")

win.show()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
