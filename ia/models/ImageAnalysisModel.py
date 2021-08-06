
import os.path, sys
from token import NAME

from numpy.core.fromnumeric import transpose
from numpy.lib.type_check import imag
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
from skimage import feature as sfeature

from skimage import data, color
from skimage.transform import rescale, resize, downscale_local_mean
from scipy import interpolate
import copy

from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

class ImageROI():
    def __init__(self, image, pos, size):
        self.image = image
        
        self.pos = pos
        self.width = size
        self.edge_type = 0  # 0 - foil, 1 - edge

        self.text = ''

    def get_sobel_y(self):
        image = self.image
        sobely= cv2.Sobel(image,cv2.CV_64F, dx=0,dy=1)
        sobely= abs(sobely)
        results = sobely
        return results


    def compute(self, threshold=0.2, order = 3):

        if self.edge_type == 0:
            img = self.image
        else:
            img = self.get_sobel_y()

        img_bg = self.get_background(img, 15 )
       
        bg_removed = img - img_bg
       
        mx = np.amax(bg_removed)
        th = np.amax(bg_removed)*threshold
        normalized = (bg_removed-th)/(mx-threshold)

        mask = normalized < 0
        masked = copy.deepcopy(normalized)
        masked[mask]= 0
        self.x_fit, self.y_fit = self.fit(masked, order = order, threshold=0.1)
        return masked, self.x_fit, self.y_fit
        
    def fit(self, I_orig, order = 3, threshold=0.2):
        
        #order = 3
        self.w_weighted = pixel_cluster_polynom_fit(I_orig, order=order, threshold = threshold)
        #print(self.w_weighted)
        '''w_weighted = copy.copy(self.w_weighted)
        w_weighted[0]=w_weighted[0]+self.pos[1]
        w_strings = []
        for w in w_weighted:
            text = "{:.3e}".format(w)
            w_strings.append(text)

        self.text = '['+ ','.join(w_strings) +']'''
        
        # Generate test points
        n_samples = 50
        x_test = np.linspace(0, I_orig.shape[1], n_samples)
        
        y_test_weighted = self.predict(x_test,order)
        return x_test, y_test_weighted

    def predict(self, x, order):
        # Predict y coordinates at test points
        x = feature(x, order)
        y_test_weighted = x.dot(self.w_weighted)
        return y_test_weighted

    def get_background(self, img, pad ):
        
        (m,n) = img.shape
        remove_index_x= range(pad, m-pad)
        img_del = np.delete(img, remove_index_x, 0)
        x = np.asarray(range(m))
        y = np.asarray(range(n))
        new_y = np.delete(x, remove_index_x)
        new_x = y
        z = img_del
        f = interpolate.interp2d(new_x, new_y, z, kind='linear')
        znew = f(y, x)
        bg_image = cv2.GaussianBlur(znew,(17,17),sigmaX=17, sigmaY=17)
        return bg_image

class ImageAnalysisModel():
    def __init__(self):
        self.image = None
        self.src = None
        self.cropped = None
        self.cropped_resized = None
        self.rois = []
        self.settings = {'horizontal_bin':15, 
                         'median_kernel_size':3, 
                         'image_bits':8,
                         'crop_limits':[],
                         'edges_roi':  [],
                         'edge_polynomial_order':[2,2],
                         'edge_fit_threshold':[0.3,0.3]} 

    def add_ROI(self, selected,pos, size):


        roi = ImageROI(selected, pos, size)
        self.rois.append(roi)


    def crop(self):
        crop_limits=self.settings['crop_limits']

        src = self.src
        [[x, y],[width, height]] = crop_limits
        self.cropped = src[y: y+height,x: x+ width]


    def filter_image(self):
        horizontal_bin = self.settings['horizontal_bin']
        median_kernel_size= self.settings['median_kernel_size']
        image_bits = self.settings['image_bits']
     
        max_bit = 2**image_bits
        cropped = self.cropped
        image = medfilt2d(cropped,kernel_size=median_kernel_size) 
        

        image_resized = resize(image, (image.shape[0] , image.shape[1] // horizontal_bin),
                       anti_aliasing=True)

        self.cropped_resized = image_resized

        # confert to absrobance
        tsrc = -1* np.log10 (image_resized/max_bit)
        mn = np.amin(tsrc)
        tsrc = tsrc - mn

        m = np.amax(tsrc)
        tsrc = tsrc/m*max_bit
        image = tsrc
        #image = cv2.transpose(src)
        #image = medfilt2d(tsrc,kernel_size=median_kernel_size)
        #self.base_surface = self.get_base_surface(image)
        self.image = image # - self.base_surface

    def load_file(self, fname, autocrop=False):
        src = np.flip(np.asarray(cv2.imread(fname,0),dtype=np.float),axis=0)
        self.src = src
        

    def get_base_surface(self, img, iterations = 30):
        sig_work = copy.copy(img)
        for i in range(iterations):
            f = cv2.GaussianBlur(sig_work,(21,21),sigmaX=21, sigmaY=21)
            less = f <= sig_work
            sig_work[less] = f[less]
        f = cv2.GaussianBlur(sig_work,(21,21),sigmaX=21, sigmaY=21)
        return f

    def estimate_edges(self):
        filtered = self.compute_sobel()
        y_size = filtered.shape[1]
        min_y=(int(y_size*0.25))
        max_y=(int(y_size*0.75))
        self.sobel_mean_vertical = filtered[:,min_y:max_y].mean(axis=1)
        self.blured_sobel_mean_vertical = gaussian_filter1d(self.sobel_mean_vertical,10)
        peaks = find_peaks(self.blured_sobel_mean_vertical/np.amax(self.blured_sobel_mean_vertical), height=0.2, width=5 )
        
        peaks_heights = {}
        for i, peak in enumerate(peaks[1]['peak_heights']):
            w = peaks[1]['widths'][i]
            peaks_heights[round(peak,4)] = [peaks[0][i],w]
        
        edges_combined = {}
        for edge in peaks_heights:
            new_edge = True
            for i, combined_edge in enumerate(edges_combined.keys()):
                diff = abs(combined_edge-peaks_heights[edge][0])
                if diff< 100:
                    new_edge=False
                    break
            if new_edge:
                edges_combined[peaks_heights[edge][0]] = (edge, peaks_heights[edge][1])
            else:
                average_edge=round((combined_edge+peaks_heights[edge][0])/2)
                average_height=round(((edges_combined[combined_edge][0]+edge)/2),4)
                new_width = edges_combined[combined_edge][0]/2+peaks_heights[edge][1]/2+diff
                edges_combined[average_edge]=(average_height,new_width)
                del(edges_combined[combined_edge])

        return edges_combined

    def get_auto_crop_limits(self, x=True, y=True):
        median_kernel_size= self.settings['median_kernel_size']
        src = self.src
        img = medfilt2d(src,kernel_size=median_kernel_size)
        crop_tightness = 5
        

        hor = img.mean(axis=0)
        ver = img.mean(axis=1)
        m = min( min(hor), min(ver))
        crop_limit = m*crop_tightness
        
        if x:
            hor_first, hor_last = self.get_1d_limits(hor,crop_limit, pad=36)
        else:
            hor_first, hor_last = 0, img.shape[1]-1
        if y:
            ver_first, ver_last = self.get_1d_limits(ver,crop_limit, pad=24)
        else:
            ver_first, ver_last = 0, img.shape[0]-1
        width = hor_last -hor_first
        height = ver_last- ver_first

        


        return [hor_first, ver_first],[width, height]

    def get_1d_limits(self, profile, limit, pad=0):
        first = np.argmax(profile>limit) + pad
        last = len(profile) - np.argmax(np.flip(profile)> limit) - pad
        return [first,last]

    '''def compute_canny(self, img):

        image = img
        # Below code convert image gradient in both x and y direction
        lap = cv2.Laplacian(image,cv2.CV_64F,ksize=3) 
        lap = np.uint8(np.absolute(lap))
        
        # Below code convert image gradient in x direction
        sobelx= cv2.Sobel(image,cv2.CV_64F, dx=1,dy=0)
        sobelx= abs(sobelx)

        # Below code convert image gradient in y direction
        sobely= cv2.Sobel(image,cv2.CV_64F, dx=0,dy=1)
        sobely= abs(sobely)
        sobel_yx = 1.0 * (sobely > sobelx )
        edges2 = 1* sfeature.canny(img/np.amax(img), sigma=3, low_threshold=.15)
        horizontal_edges = edges2 * sobel_yx
        return image, horizontal_edges, sobely'''

    def compute_sobel(self):
        image = self.image
        image = cv2.GaussianBlur(image,(5,5),sigmaX=5, sigmaY=0)

        '''# Below code convert image gradient in both x and y direction
        lap = cv2.Laplacian(image,cv2.CV_64F,ksize=3) 
        lap = np.uint8(np.absolute(lap))
        '''
        # Below code convert image gradient in x direction
        #sobelx= cv2.Sobel(image,cv2.CV_64F, dx=1,dy=0)
        #sobelx= abs(sobelx)
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

    

def feature(x, order=3):
    """Generate polynomial feature of the form
    [1, x, x^2, ..., x^order] where x is the column of x-coordinates
    and 1 is the column of ones for the intercept.
    """
    x = x.reshape(-1, 1)
    return np.power(x, np.arange(order+1).reshape(1, -1)) 

def pixel_cluster_polynom_fit(I, order=3, threshold = .2):
    '''
    We find all (xi, yi) coordinates of the bright regions, 
    then set up a regularized least squares system where the we want to 
    find the vector of weights, (w0, ..., wd) such that 
    yi = w0 + w1 xi + w2 xi^2 + ... + wd xi^d "as close as possible" 
    in the least squares sense.
    Source: https://stackoverflow.com/questions/52802648/how-do-i-fit-a-line-to-a-cluster-of-pixels
    '''
    
    # Mask out region
    mask = I > threshold

    # Get coordinates of pixels corresponding to marked region
    X = np.argwhere(mask)

    # Use the value as weights later
    weights = I[mask] / float(I.max())
    # Convert to diagonal matrix
    W = np.diag(weights)

    # Column indices
    x = X[:, 1].reshape(-1, 1)
    # Row indices to predict. Note origin is at top left corner
    y = X[:, 0]


    # Ridge regression, i.e., least squares with l2 regularization. 
    # Should probably use a more numerically stable implementation, 
    # e.g., that in Scikit-Learn
    # alpha is regularization parameter. Larger alpha => less flexible curve
    alpha = 0.01

    # Construct data matrix, A
    #order = 3
    A = feature(x, order)
    # w = inv (A^T A + alpha * I) A^T y
    #w_unweighted = np.linalg.pinv( A.T.dot(A) + alpha * np.eye(A.shape[1])).dot(A.T).dot(y)
    # w = inv (A^T W A + alpha * I) A^T W y
    w_weighted = np.linalg.pinv( A.T.dot(W).dot(A) + alpha * \
                             np.eye(A.shape[1])).dot(A.T).dot(W).dot(y)

    return w_weighted