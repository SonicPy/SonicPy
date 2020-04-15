

import  time, logging, os, struct, sys, copy

from pyqtgraph.Qt import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import queue 
from functools import partial
import json

class pvServer():
    pvs = {}
    def __init__(self):
        pass

    def set_pv(self, pv_name, pv):
        self.pvs[pv_name] = pv
        #print(str(pv_name)+':'+str(pv))

    def get_pv(self, pv_name):
        #print(pv_name)
        pv = self.pvs[pv_name]
        
        return pv

