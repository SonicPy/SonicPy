
import numpy as np


import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from widgets.PltWidget import SimpleDisplayWidget, DetailDisplayWidget

import time
from utilities.utilities import *
from utilities.HelperModule import move_window_relative_to_screen_center

import visa
from models.PyTektronixScope import TektronixScope

freq = 30.00
width=10  # data bin width to speed up calculations


if True:
    rm = visa.ResourceManager()
    resources = rm.list_resources()
    res = 'TCPIP0::hpcat143.xray.aps.anl.gov::inst0::INSTR'
    visa_resource_name = resources[0]
    print(visa_resource_name)
    scope = rm.open_resource(res)
    status = scope.ask('*IDN?')
    print(status)
    scope = TektronixScope(scope)
    for u in range(1):
        start = time.time()
        x, y = scope.read_data_one_channel('CH1', data_start=1, data_stop=100000,x_axis_out=True)
        end = time.time()
        print ('data read time: ' + str(end - start)) 
    #np.save('wave_X_1.npy', X)
    #np.save('wave_Y_1.npy', Y)
else:
    pass
    '''
    X = np.load('wave_X.npy')
    Y = np.load('wave_Y.npy')
    '''
    X, Y = read_tek_csv('resources/4000psi-300K_+30MHz000.csv')    


 


xmin = None
xmax = None
xmin = 2.50e-6
#xmax = 5.2e-6
#x, y, _ = signal_region_by_x(X,Y,xmin,xmax)

x = rebin(x,width)
y = rebin(y,width)
sig = y
'''
ave = np.mean(y)
y = y-ave
m = max(y)
y = y / m
del_x = (x[2]-x[1])
xsource, source = generate_source(del_x, freq, N=6, window=True)
  #*w
corr = cross_correlate_sig(sig, source)
m = max(corr)
corr=corr/m
amplitude_envelope, phase_shift, instanteneous_frequency = demodulate(x,corr, freq)
f_W, f_sig = fft_sig(x,corr)
'''
#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])

US1_fig_parameters = 'Signal', 'Amplitude','Time'
US1 = SimpleDisplayWidget(US1_fig_parameters)
win = US1.fig
win.setPlotMouseMode(0)
p1 = win.add_line_plot(x,sig,color=(0,150,150))
xmin = min(x)
#p1.plot(xsource+xmin,source, pen=(226,226,0), name="Red curve")
#p1.plot(x,corr, pen=(226,0,0), name="Red curve")
r = (max(x)-min(x))
rmin = min(x)+r*0.4
rmax = rmin + r*0.07
lr = pg.LinearRegionItem([rmin,rmax])
lr.setZValue(-10)
win.win.addItem(lr)
move_window_relative_to_screen_center(US1,0,-400)
US1.raise_widget()

US2_fig_parameters = 'De-modulation', 'Amplitude','Time'
US2 = DetailDisplayWidget(US2_fig_parameters)
US2.enable_cursors()
win2 = US2.fig
win2.setPlotMouseMode(0)
p2a = win2.add_line_plot(x,sig, color=(0,150,150),Width = 1)
#p2b = win2.add_line_plot(x,corr, color=(250,0,0))
#p2c = win2.add_line_plot(x,amplitude_envelope, color=(250,0,150),Width = 1)
#p2d = win2.add_line_plot(x,amplitude_envelope*-1, color=(250,0,150),Width = 1)


def updatePlot2():
    win2.win.setXRange(*lr.getRegion(), padding=0)
def updateRegion2():
    lr.setRegion(p2a.getViewBox().viewRange()[0])
lr.sigRegionChanged.connect(updatePlot2)
win2.win.sigXRangeChanged.connect(updateRegion2)
updatePlot2()
move_window_relative_to_screen_center(US2,0,0)
US2.raise_widget()


'''
win3 = plotWindow(title='de-modulation')
win3.setPlotMouseMode(0)
p3a = win3.add_line_plot(x,sig, color=(0,150,150),Width = 1)
#p2b = win2.add_line_plot(x,corr, color=(250,0,0))
p3c = win3.add_line_plot(x,amplitude_envelope, color=(250,0,50),Width = 1)
p3d = win3.add_line_plot(x,amplitude_envelope*-1, color=(250,0,50),Width = 1)
def updatePlot3():
    win3.win.setXRange(*lr.getRegion(), padding=0)
def updateRegion3():
    lr.setRegion(p3a.getViewBox().viewRange()[0])

lr.sigRegionChanged.connect(updatePlot3)
win3.win.sigXRangeChanged.connect(updateRegion3)
updatePlot3()
win3.raise_widget()

'''


'''
win.nextRow()
p3 = win.addPlot(title="env")
p3.plot(x,corr, pen=(0,226,226), name="Red curve")
p3.plot(x,amplitude_envelope, pen=(226,226,0), name="Red curve")
p3.plot(x,amplitude_envelope*-1, pen=(226,226,0), name="Red curve")
win.nextRow()
p4 = win.addPlot(title="freq")
p4.plot(x,phase_shift/(2*np.pi), pen=(0,226,226), name="Red curve")
#p4.plot(x[:-1],instanteneous_frequency*10e-6+freq, pen=(0,226,226), name="Red curve")
'''
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.exec_()

'''
x2 = np.linspace(-100, 100, 1000)
data2 = np.sin(x2) / x2
p8 = win.addPlot(title="Region Selection")
p8.plot(data2, pen=(255,255,255,200))
lr = pg.LinearRegionItem([400,700])
lr.setZValue(-10)
p8.addItem(lr)

p9 = win.addPlot(title="Zoom on selected region")
p9.plot(data2)
def updatePlot():
    p9.setXRange(*lr.getRegion(), padding=0)
def updateRegion():
    lr.setRegion(p9.getViewBox().viewRange()[0])
lr.sigRegionChanged.connect(updatePlot)
p9.sigXRangeChanged.connect(updateRegion)
updatePlot()

'''
