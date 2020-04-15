import os.path, sys
import numpy as np


from um.models.tek_fileIO import *


from functools import partial
import json


def read_arb():

    desc = read_file_TEKAFG3000('3pulse.tfw')
    data_length = desc['data_length']
    binary_waveform = desc['binary_waveform']

    return binary_waveform


y = read_arb()
# max: 16382  (2^14-2)


import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore

data = y
pg.plot(data, title="Simplest possible plotting example")



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.exec_()
