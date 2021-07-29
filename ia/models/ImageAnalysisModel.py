
import os.path, sys

from numpy.core.fromnumeric import transpose
from utilities.utilities import *
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import numpy as np
from numpy import argmax, nan, greater,less, append, sort, array

from scipy import optimize
from scipy.signal import argrelextrema, tukey, medfilt2d

from functools import partial
from um.models.tek_fileIO import *
from scipy import signal
import pyqtgraph as pg
from utilities.utilities import zero_phase_bandpass_filter
import json
import cv2
import numpy as np


class ImageAnalysisModel():
    def __init__(self):
        self.image = None
        self.load_file("/Users/hrubiak/GitHub/sonicPy/ia/resources/logo_og.png")
        

    
    def load_file(self, fname):
        src = cv2.imread(fname,0)
        #image = cv2.transpose(src)
        self.image = medfilt2d(src,kernel_size=3)

    def compute_edges(self):
        image = self.image
        #image = cv2.GaussianBlur(self.image,(5,5),0)

        '''# Below code convert image gradient in both x and y direction
        lap = cv2.Laplacian(image,cv2.CV_64F,ksize=3) 
        lap = np.uint8(np.absolute(lap))

        # Below code convert image gradient in x direction
        sobelx= cv2.Sobel(image,cv2.CV_64F, dx=1,dy=0)
        sobelx= np.uint8(np.absolute(sobelx))'''

        # Below code convert image gradient in y direction
        sobely= cv2.Sobel(image,cv2.CV_64F, dx=0,dy=1)
        sobely = np.uint8(np.absolute(sobely))

        results = sobely
        return results

    def save_result(self, filename):
        
        data = {'edges':[]}
        
        if filename.endswith('.json'):
            with open(filename, 'w') as json_file:
                json.dump(data, json_file,indent = 2)    

    
  

