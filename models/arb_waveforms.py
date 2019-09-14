import os.path, sys
import numpy as np


from models.tek_fileIO import *
from utilities.utilities import *


from functools import partial
import json


def get_arb():

    desc = read_file_TEKAFG3000('/Users/ross/OneDrive/Documents/VSCodeProjects/tek_visa/3pulse.tfw')
    data_length = desc['data_length']
    binary_waveform = desc['binary_waveform']

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

'''
y = get_arb()

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsLayoutWidget(show=True, title="binary_waveform")
win.resize(1000,600)
win.setWindowTitle('binary_waveform')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p2 = win.addPlot(title="Multiple curves")
p2.plot(y, pen=(255,0,0), name="Red curve")


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
'''