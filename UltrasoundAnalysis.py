
import numpy as np
from numpy import argmax, nan, greater,less, append, sort, array
import sys
from PyQt5 import QtWidgets
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from widgets.PltWidget import SimpleDisplayWidget, DetailDisplayWidget
from scipy import signal
import time
from utilities.utilities import *
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
from widgets.UtilityWidgets import open_file_dialog

from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QMessageBox, QErrorMessage
from models.tek_fileIO import *

from widgets.PltWidget import SimpleDisplayWidget, customWidget
from widgets.CustomWidgets import HorizontalSpacerItem

from scipy import optimize
from scipy.signal import argrelextrema
from functools import partial

initialized = False

def load_file():
    filename = open_file_dialog(None, "Load File(s).",filter='*.csv')
    if len(filename):
        t, spectrum = read_tek_csv(filename, subsample=4)
        t, spectrum = zero_phase_highpass_filter([t,spectrum],1e4,1)
        return t,spectrum
    else:
        return None, None

def make_widget():
    my_widget = QtWidgets.QWidget()
    _layout = QtWidgets.QVBoxLayout()
    _layout.setContentsMargins(10, 10, 10, 10)
    detail_widget = QtWidgets.QWidget()
    _detail_layout = QtWidgets.QHBoxLayout()
    _detail_layout.setContentsMargins(0, 0, 0, 0)
    buttons_widget_top = QtWidgets.QWidget()
    _buttons_layout_top = QtWidgets.QHBoxLayout()
    _buttons_layout_top.setContentsMargins(0, 0, 0, 0)
    buttons_widget_bottom = QtWidgets.QWidget()
    _buttons_layout_bottom = QtWidgets.QHBoxLayout()
    _buttons_layout_bottom.setContentsMargins(0, 0, 0, 0)
    open_btn = QtWidgets.QPushButton("Open")
    _buttons_layout_top.addWidget(open_btn)
    _buttons_layout_top.addSpacerItem(HorizontalSpacerItem())
    buttons_widget_top.setLayout(_buttons_layout_top)
    _layout.addWidget(buttons_widget_top)
    params = "Ultrasound echo analysis", 'Amplitude', 'Time'
    win = customWidget(params)
    _layout.addWidget(win)
    detail1 = "Ultrasound echo 1", 'Amplitude', 'Time'
    detail_win1 = customWidget(detail1)
    detail2 = "Ultrasound echo 2", 'Amplitude', 'Time'
    detail_win2 = customWidget(detail2)
    _detail_layout.addWidget(detail_win1)
    _detail_layout.addWidget(detail_win2)
    detail_widget.setLayout(_detail_layout)
    _layout.addWidget(detail_widget)
    calc_btn = QtWidgets.QPushButton('Correlate')
    _buttons_layout_bottom.addWidget(calc_btn)
    _buttons_layout_bottom.addWidget(QtWidgets.QLabel('2-way travel time:'))
    output_ebx = QtWidgets.QLineEdit('')
    _buttons_layout_bottom.addWidget(output_ebx)
    _buttons_layout_bottom.addSpacerItem(HorizontalSpacerItem())
    buttons_widget_bottom.setLayout(_buttons_layout_bottom)
    _layout.addWidget(buttons_widget_bottom)
    my_widget.setLayout(_layout)
    return my_widget, win, detail_win1, detail_win2, open_btn, calc_btn, output_ebx

def get_initial_lr_positions(t):
    mn = min(t)
    mx = max(t)
    r = mx-mn
    p1l = 0.25 * r
    p1r = 0.3 * r
    p2l = 0.7 * r
    p2r = 0.75 * r 
    return p1l, p1r, p2l, p2r

def updatePlot1(lr1, plot_win_detail1):
    lr1r = lr1.getRegion()
    plot_win_detail1.setXRange(*lr1r, padding=0)

def updateRegion1(lr1, detail_plot1):
    lr1.setRegion(detail_plot1.getViewBox().viewRange()[0])
    

def updatePlot2(lr2, plot_win_detail2):
    lr2r = lr2.getRegion()
    plot_win_detail2.setXRange(*lr2r, padding=0)

def updateRegion2(lr2, detail_plot2):
    lr2.setRegion(detail_plot2.getViewBox().viewRange()[0])

def init_region_items(t, lr1, lr2, plot_win, plot_win_detail1, plot_win_detail2, detail_plot1,detail_plot2):
    
    plot_win.addItem(lr1)
    plot_win.addItem(lr2) 
    p1l, p1r, p2l, p2r = get_initial_lr_positions(t)

    lr1.setRegion([p1l, p1r])
    lr2.setRegion([p2l, p2r])
    
    
    #updatePlot1(lr1, plot_win_detail1)
    lr1r = lr1.getRegion()
    plot_win_detail1.setXRange(*lr1r, padding=0)

    
    #updatePlot2(lr2, plot_win_detail2)
    lr2r = lr2.getRegion()
    plot_win_detail2.setXRange(*lr2r, padding=0)

    lr1.sigRegionChanged.connect(partial(updatePlot1,lr1, plot_win_detail1))
    plot_win_detail1.sigXRangeChanged.connect(partial(updateRegion1,lr1, detail_plot1))

    lr2.sigRegionChanged.connect(partial(updatePlot2,lr2, plot_win_detail2))
    plot_win_detail2.sigXRangeChanged.connect(partial(updateRegion2,lr2, detail_plot2))

    plot_win_detail1.setXRange(*lr1r, padding=0)
    plot_win_detail2.setXRange(*lr2r, padding=0)
    

app = QApplication(sys.argv)
app.aboutToQuit.connect(app.deleteLater)
my_widget, win, detail_win1, detail_win2, open_btn, calc_btn, output_ebx = make_widget()
#t,spectrum = load_file()

### linear retions
plot_win = win.fig.win
plot_win_detail1 = detail_win1.fig.win
plot_win_detail2 = detail_win2.fig.win

main_plot = pg.PlotDataItem([], [], title="",
                antialias=True, pen=pg.mkPen(color=(255,255,0), width=1), connect="finite" )
plot_win.addItem(main_plot)




detail_plot1 = pg.PlotDataItem([],[], title="",
                antialias=True, pen=pg.mkPen(color=(255,255,0), width=1), connect="finite" )
detail_plot1_bg = pg.PlotDataItem([], [], title="",
                antialias=True, pen=pg.mkPen(color=(0,255,255), width=1), connect="finite" )


plot_win_detail1.addItem(detail_plot1)
plot_win_detail1.addItem(detail_plot1_bg)



detail_plot2 = pg.PlotDataItem([], [], title="",
                antialias=True, pen=pg.mkPen(color=(255,255,0), width=1), connect="finite" )
detail_plot2_bg = pg.PlotDataItem([], [], title="",
                antialias=True, pen=pg.mkPen(color=(0,255,255), width=1), connect="finite" )


plot_win_detail2.addItem(detail_plot2)
plot_win_detail2.addItem(detail_plot2_bg)

lr1 = pg.LinearRegionItem()
lr1.setZValue(-10)


lr2 = pg.LinearRegionItem()
lr2.setZValue(-10)


def update_data():
    global lr1, lr2, plot_win,plot_win_detail1, plot_win_detail2,detail_plot1,detail_plot2
    global t, spectrum, initialized
    t, spectrum = load_file()
    if t is not None and spectrum is not None:
        main_plot.setData(t, spectrum)
        detail_plot1.setData(t, spectrum)
        detail_plot2.setData(t, spectrum)
        

        if not initialized:

            init_region_items(t,lr1, lr2, plot_win,plot_win_detail1, plot_win_detail2,detail_plot1,detail_plot2)
            

def fit_func(x, a, b,c,d):
    return a * np.cos(b * x+c)+d


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

def snap_cursors_to_optimum(c1, c2, t, spectrum):
    
    cor_range = 50
    
    pilo1 = int(get_partial_index(t,c1))-int(cor_range/2)
    pihi1 = int(get_partial_index(t,c1))+int(cor_range/2)
    
    pilo2 = int(get_partial_index(t,c2))-int(cor_range/2)
    pihi2 = int(get_partial_index(t,c2))+int(cor_range/2)
    

    slice1 = np.asarray(spectrum)[pilo1:pihi1]
    #pg.plot(np.asarray(slice1), title="slice1")
    t1 = np.asarray(t)[pilo1:pihi1]
    slice2 = np.asarray(spectrum)[pilo2:pihi2]
    #pg.plot(np.asarray(slice1), title="slice1")
    t2 = np.asarray(t)[pilo2:pihi2]

    (optima_x_1, optima_y_1), optima_type_1 = get_local_optimum (c1, t1, slice1)
    (optima_x_2, optima_y_2), optima_type_2 = get_local_optimum (c2, t2, slice2)
    return optima_x_1, optima_x_2, optima_y_1, optima_y_2


def calculate_data():
    t_f, spectrum_f = zero_phase_lowpass_filter([t,spectrum],60e6,1)
    #pg.plot(np.asarray(spectrum_f), title="spectrum_f")
    
    c1 = plot_win_detail1.get_cursor_pos()
    c2 = plot_win_detail2.get_cursor_pos()

    optima_x_1, optima_x_2, optima_y_1, optima_y_2 = snap_cursors_to_optimum(c1, c2,t_f, spectrum_f)

    plot_win_detail1.set_cursor_pos(optima_x_1[0])
    plot_win_detail2.set_cursor_pos(optima_x_2[0])
    

    c1 = plot_win_detail1.get_cursor_pos()
    c2 = plot_win_detail2.get_cursor_pos()

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
    params, params_covariance = optimize.curve_fit(fit_func, n, y_data,p0=[.99,.011,.1, .1])
    fitted = fit_func(n, params[0], params[1], params[2], params[3])

    
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

    c_diff_optimized = c2-c1_new_pos


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
    plot1_overlay_t = t2 - c_diff_optimized
    plot2_overlay_t = t1 + c_diff_optimized
    detail_plot1_bg.setData(plot1_overlay_t, plot1_overlay)
    detail_plot2_bg.setData(plot2_overlay_t, plot2_overlay)
    
    output_ebx.setText('%.5e' % (c_diff_optimized))
    #print(c_shift)
    #plot_win_detail1.set_cursor_pos(c1_new_pos)
    


    
open_btn.clicked.connect(update_data)
calc_btn.clicked.connect(calculate_data)


my_widget.show()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
