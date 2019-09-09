import pyqtgraph as pg
from PyQt5.QtGui import QPixmap

from PIL import Image

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

from PyQt5.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout



# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

pg.mkQApp()
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('Radiography: Distance Tool')

# A plot area (ViewBox + axes) for displaying the image
p1 = win.addPlot(colspan=4)
p1.setMaximumHeight(350)

# Item for displaying image data
img = pg.ImageItem()
p1.addItem(img)


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


# Contrast/color control
hist = pg.HistogramLUTItem()

hist.setImageItem(img)
win.addItem(hist)
hist.setMaximumWidth(100)
hist.setMaximumHeight(350)

# Another plot area for displaying ROI data
win.nextRow()
p2 = win.addPlot(colspan=2)
p2.setMaximumHeight(250)

p3 = win.addPlot(colspan=2)
p3.setMaximumHeight(250)


lbl = QLabel('')
lbl.setStyleSheet("background-color: transparent; color: #CCCCCC")
lbl.setMaximumHeight(250)
lbl.setMaximumWidth(150)
btn = QPushButton('Open')
btn.setMaximumWidth(90)
btn.setStyleSheet("background-color: #CCCCCC; color: #000000")

my_widget = QWidget()
my_widget.setMaximumWidth(150)
my_widget.setStyleSheet("background-color: transparent; color: #CCCCCC")
_layout = QVBoxLayout()
_layout.addWidget(lbl)
_layout.addWidget(btn)
my_widget.setLayout(_layout)

proxy = QtGui.QGraphicsProxyWidget()
proxy.setWidget(my_widget)
p4 = win.addLayout()
p4.addItem(proxy)

win.resize(800, 550)
win.show()


# Generate image data

im = Image.open("resources/4000psi_300K_Fe-1.7C.bmp")

import epics
import time
pvname = '16AVT2:image1:ArrayData'
img_pv  = epics.PV(pvname)

raw_image = img_pv.get()
im = raw_image.reshape((1216,1936,3))[:,:,1]



data = np.array(im).T
s = data.shape
#from scipy.ndimage import median_filter

#data = median_filter(data, size=3)

def set_data(data):
    img.setImage(data)
    hist.setLevels(data.min(), data.max())
    
set_data(data)

# set position and scale of image
img.scale(0.1, 0.1)
img.translate(0, 0)

# zoom to fit imageo
p1.autoRange()  

pos1 = 0
pos2 = 0




def update_lbl():
    global lbl, pos1, pos2
    d = abs(pos1-pos2)
    um = d * 0.85
    s = 'Pos 1: %0.1f\nPos 2: %0.1f\nDiff (px): %0.1f\nDiff (um): %0.1f' % (pos1,pos2,d,um)
    lbl.setText(s)

def get_optimum(m):
    g = np.gradient(m)
    
    amin = abs(min(g))
    amax = abs(max(g))
    direction = amax< amin
    if direction:
        pos = np.argmin(g)
    else:  
        pos = np.argmax(g)
    return pos, g

# Callbacks for handling user interaction
def updatePlot():
    global img, roi, data, p2, pos1
    p = roi.pos()[0]*10
    selected = roi.getArrayRegion(data, img)
    m = selected.mean(axis=0)
    
    pos1, g = get_optimum(m)
    pos1 = pos1+p
    p2.plot(g, clear=True)
    update_lbl()

# Callbacks for handling user interaction
def updatePlot2():
    global img, roi2, data, p3, pos2
    p = roi2.pos()[0]*10
    selected = roi2.getArrayRegion(data, img)
    m = selected.mean(axis=0)
    pos2, g = get_optimum(m)
    pos2 = pos2+p
    p3.plot(g, clear=True)
    update_lbl()

roi.sigRegionChanged.connect(updatePlot)
roi2.sigRegionChanged.connect(updatePlot2)
updatePlot()
updatePlot2()

'''


'''

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
