
import os.path, sys
from token import NAME

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
from skimage import feature

from skimage import data, color
from skimage.transform import rescale, resize, downscale_local_mean
from scipy import interpolate

class ImageAnalysisModel():
    def __init__(self):
        self.image = None
        self.src = None
        
        

    
    def load_file(self, fname):
        src = np.asarray(cv2.imread(fname,0),dtype=np.float)

        
        

        image = medfilt2d(src,kernel_size=3)

        horizontal_bin = 6
        image_resized = resize(image, (image.shape[0] , image.shape[1] // horizontal_bin),
                       anti_aliasing=True)

        self.src = image_resized

        tsrc = -1* np.log(image_resized/255)
        mn = np.amin(tsrc)
        tsrc = tsrc - mn

        m = np.amax(tsrc)
        tsrc = tsrc/m*255

        

        #image = cv2.transpose(src)
        image = medfilt2d(tsrc,kernel_size=3)
        
        self.image = image

    def get_background(self, img, min_x, max_x):

        (m,n) = img.shape
        remove_index_x= range(min_x, max_x)


        img_del = np.delete(img, remove_index_x, 0)
        

        x = np.asarray(range(m))
        y = np.asarray(range(n))

        
        new_y = np.delete(x, remove_index_x)
        new_x = y

        
        z = img_del
        f = interpolate.interp2d(new_x, new_y, z, kind='linear')

        znew = f(y, x)

        bg_image = cv2.GaussianBlur(znew,(25,25),sigmaX=51, sigmaY=51)

        return bg_image


    def compute_canny(self, img):

        image = img

        '''# Below code convert image gradient in both x and y direction
        lap = cv2.Laplacian(image,cv2.CV_64F,ksize=3) 
        lap = np.uint8(np.absolute(lap))
        '''
        # Below code convert image gradient in x direction
        sobelx= cv2.Sobel(image,cv2.CV_64F, dx=1,dy=0)
        sobelx= abs(sobelx)

        # Below code convert image gradient in y direction
        sobely= cv2.Sobel(image,cv2.CV_64F, dx=0,dy=1)
        sobely= abs(sobely)

        
        
        sobel_yx = 1.0 * (sobely > sobelx )

        edges2 = 1* feature.canny(img, sigma=3)
        
        horizontal_edges = edges2 * sobel_yx

        

        return image, horizontal_edges, sobely

    def compute_sobel(self):
        image = self.image
        image = cv2.GaussianBlur(image,(5,5),sigmaX=5, sigmaY=0)

        '''# Below code convert image gradient in both x and y direction
        lap = cv2.Laplacian(image,cv2.CV_64F,ksize=3) 
        lap = np.uint8(np.absolute(lap))
        '''
        # Below code convert image gradient in x direction
        sobelx= cv2.Sobel(image,cv2.CV_64F, dx=1,dy=0)
        sobelx= abs(sobelx)

        # Below code convert image gradient in y direction
        sobely= cv2.Sobel(image,cv2.CV_64F, dx=0,dy=1)
        sobely= abs(sobely)
        
        results = sobely
        return results



    def save_result(self, filename):
        
        data = {'edges':[]}
        
        if filename.endswith('.json'):
            with open(filename, 'w') as json_file:
                json.dump(data, json_file,indent = 2)    

    
  

