
import numpy as np
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

def load_file():
    filename = open_file_dialog(None, "Load File(s).", None) 
    t, spectrum = read_tek_csv(filename, subsample=1)
    return t,spectrum

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

app = QApplication(sys.argv)
app.aboutToQuit.connect(app.deleteLater)
my_widget, win, detail_win1, detail_win2, open_btn, calc_btn, output_ebx = make_widget()
t,spectrum = load_file()

### linear retions
plot_win = win.fig.win
plot_win_detail1 = detail_win1.fig.win
plot_win_detail2 = detail_win2.fig.win
x2 = t
data2 = spectrum
main_plot = pg.PlotDataItem(t, spectrum, title="",
                antialias=True, pen=pg.mkPen(color=(255,255,0), width=1), connect="finite" )
plot_win.addItem(main_plot)

p1l, p1r, p2l, p2r = get_initial_lr_positions(t)

lr1 = pg.LinearRegionItem([p1l,p1r])
lr1.setZValue(-10)
plot_win.addItem(lr1)

lr2 = pg.LinearRegionItem([p2l,p2r])
lr2.setZValue(-10)
plot_win.addItem(lr2)

detail_plot1 = pg.PlotDataItem(t, spectrum, title="",
                antialias=True, pen=pg.mkPen(color=(255,255,0), width=1), connect="finite" )
plot_win_detail1.addItem(detail_plot1)
def updatePlot1():
    plot_win_detail1.setXRange(*lr1.getRegion(), padding=0)
def updateRegion1():
    lr1.setRegion(detail_plot1.getViewBox().viewRange()[0])
lr1.sigRegionChanged.connect(updatePlot1)
plot_win_detail1.sigXRangeChanged.connect(updateRegion1)
updatePlot1()

detail_plot2 = pg.PlotDataItem(t, spectrum, title="",
                antialias=True, pen=pg.mkPen(color=(255,255,0), width=1), connect="finite" )
plot_win_detail2.addItem(detail_plot2)
def updatePlot2():
    plot_win_detail2.setXRange(*lr2.getRegion(), padding=0)
def updateRegion2():
    lr2.setRegion(detail_plot2.getViewBox().viewRange()[0])
lr2.sigRegionChanged.connect(updatePlot2)
plot_win_detail2.sigXRangeChanged.connect(updateRegion2)
updatePlot2()

def update_data():
    t, spectrum = load_file()
    main_plot.setData(t, spectrum)
    detail_plot1.setData(t, spectrum)
    detail_plot2.setData(t, spectrum)

def fit_func(x, a, b,c,d):
    return a * np.cos(b * x+c)+d

def calculate_data():
    c1 = plot_win_detail1.get_cursor_pos()
    c2 = plot_win_detail2.get_cursor_pos()

    c_diff = c2-c1
    cor_range = 200
    
    pilo1 = int(get_partial_index(t,c1))-int(cor_range/2)
    pihi1 = int(get_partial_index(t,c1))+int(cor_range/2)
    picenter2 = int(get_partial_index(t,c2))
    

    slice1 = np.asarray(spectrum)[pilo1:pihi1]
    #pg.plot(np.asarray(slice1), title="slice1")
    t1 = np.asarray(t)[pilo1:pihi1]

    shift_range = cor_range
    cross_corr = []
    for shift in range(shift_range):
        pilo2 = picenter2 - int(cor_range/2) + int((shift-shift_range/2))
        pihi2 = picenter2 + int(cor_range/2) + int((shift-shift_range/2))
        slice2 = np.asarray(spectrum)[pilo2:pihi2]
        c = np.correlate(slice1, slice2)[0]
        cross_corr.append(c)

    x_data=t1
    y_data=np.asarray(cross_corr)
    n = range(len(x_data))
    params, params_covariance = optimize.curve_fit(fit_func, n, y_data,p0=[.5,.02,.1, .1])
    fitted = fit_func(n, params[0], params[1], params[2], params[3])

    #print (params)
    a = params[0]
    b = params[1]
    c = params[2]
    if a >= 0:
        x_max = -c/b 
    else:
        x_max = (np.pi-c)/b
    #print(x_max)

    p_val = get_partial_value(t1,x_max)  # this needs more work, often the output is out of range of array
    c_shift = c1 - p_val
    c1_new_pos = c1+c_shift

    c_diff_optimized = c2-c1
    output_ebx.setText('%.5e' % (c_diff_optimized))
    #print(c_shift)
    plot_win_detail1.set_cursor_pos(c1_new_pos)
    #pg.plot(np.asarray(cross_corr), title="Correlate")
    #pg.plot(np.asarray(fitted), title="Fit")

open_btn.clicked.connect(update_data)
calc_btn.clicked.connect(calculate_data)


my_widget.show()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
