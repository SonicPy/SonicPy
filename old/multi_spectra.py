
import numpy as np
import sys

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore


import time
from utilities.utilities import *
from utilities.HelperModule import move_window_relative_to_screen_center
from um.widgets.UtilityWidgets import open_files_dialog

from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QMessageBox, QErrorMessage
from um.models.tek_fileIO import *


app = QApplication(sys.argv)
app.aboutToQuit.connect(app.deleteLater)

#filenames = open_files_dialog(None, "Load File(s).", None) 

folder = '/Users/ross/Globus/s16bmb-20210717-e244302-Aihaiti/sam2/US/2400psi'
json_search = os.path.join(folder,'*.csv')
filenames = sorted( glob.glob(json_search))


'''

filenames =['sweep_test/test_001.csv',
            'sweep_test/test_002.csv',
            'sweep_test/test_003.csv',
            'sweep_test/test_004.csv',
            'sweep_test/test_005.csv']
'''
width = 2

if len(filenames):
    spectra, x = read_multiple_spectra(filenames)

x = rebin(x,width)
for i in range(len(spectra)):
    spectra[i] = rebin(np.asarray(spectra[i]),width)


freqs = [10,15,20,25,30]
envelopes = []

sos = signal.butter(3, .1, 'hp',  output='sos')

del_x = (x[2]-x[1])
for ind, s in enumerate(spectra):
    freq = ind * 2 + 24
    
    filtered = signal.sosfiltfilt(sos, s)
    spectra[ind]=filtered
    y = filtered
    #ave = np.mean(y)
    #m = max(y)
    #y = y / m
    
    xsource, source = generate_source(del_x, freq,  N=2, window=True)
    corr = cross_correlate_sig(y, source)
    #m = max(corr)
    #corr=corr/m
    amplitude_envelope= demodulate(x,corr)
    #amplitude_envelope[amplitude_envelope<=0]=0.01
    amplitude_envelope = np.sqrt(amplitude_envelope)
    envelopes.append(amplitude_envelope)


# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')


win = pg.GraphicsLayoutWidget()
win.setWindowTitle('Ultrasound echo view')

# A plot area (ViewBox + axes) for displaying the image
p1 = win.addPlot(colspan=4)

img = pg.ImageItem()
p1.addItem(img)


'''
# Custom ROI1 for selecting an image region
roi = pg.ROI([20, 38], [7, 140])
roi.addScaleHandle([0.5, 1], [0.5, 0.5])
roi.addScaleHandle([0, 0.5], [0.5, 0.5])
p1.addItem(roi)
roi.setZValue(10)  # make sure ROI is drawn above image

# Custom ROI2 for selecting an image region
roi2 = pg.ROI([95, 38], [7, 140])
roi2.addScaleHandle([0.5, 1], [0.5, 0.5])
roi2.addScaleHandle([0, 0.5], [0.5, 0.5])
p1.addItem(roi2)
roi.setZValue(11)  # make sure ROI is drawn above image
'''
def update_data(param):
    param
# Contrast/color control 
hist = pg.HistogramLUTItem()

hist.setImageItem(img)
win.addItem(hist)
hist.setMaximumWidth(120)
hist.setMaximumHeight(350)

win.nextRow()


p2 = win.addPlot(colspan=4)

img2 = pg.ImageItem()
p2.addItem(img2)
# Contrast/color control
hist2 = pg.HistogramLUTItem()
hist2.setImageItem(img2)
win.addItem(hist2)
hist2.setMaximumWidth(120)
hist2.setMaximumHeight(350)


data2 = np.array(envelopes)

img2.setImage(data2)

hist2.setLevels(data2.min(), data2.max())


win.resize(1000, 550)
win.show()

data = np.array(spectra)

s = data.shape
img.setImage(data)
hist.setLevels(data.min()*0.05, data.max()*0.05)

# set position and scale of image
#img.scale(0.1, 0.1)
#img.translate(0, 0)

# zoom to fit imageo
p1.autoRange()  
'''
p2.autoRange() 
'''

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
