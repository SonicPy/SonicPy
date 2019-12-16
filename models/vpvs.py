# -*- coding: utf8 -*-

# DISCLAIMER
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Principal author: R. Hrubiak (hrubiak@anl.gov)
# Copyright (C) 2018-2019 ANL, Lemont, USA

# Based on code from Dioptas - GUI program for fast processing of 2D X-ray diffraction data


import string, ast, json
import numpy as np
from math import isnan
from scipy.optimize import minimize
import os
import os.path


class vpvs_reflection:
    """
    Class that defines a reflection.
    Attributes:
   
    """

    def __init__(self, r = 0., d=0., v=0.):
        self.r0 = r
        self.d = d
        self.v = v
        self.r = r
        
    def __str__(self):
        return "{:2d},{:2d}\t{:.2f}\t{:.3f}".format(self.r, self.r*2, self.d, self.v)

    def get_r(self):
        return "%f %f %f"%(self.r,self.r*2)

    def get_r_list(self):
        return [self.r,self.r*2]



class MyDict(dict):
    def __init__(self):
        super(MyDict, self).__init__()
        self.setdefault('modified', False)


    def __setitem__(self, key, value):
        if key in ['comments',  't0_p', 't0_s', 'vp', 'vs','d']:
            self.__setitem__('modified', True)
        super(MyDict, self).__setitem__(key, value)

class vpvs(object):
    def __init__(self):
        self._filename = ''
        self._name = ''
        self.params = MyDict()
        self.params['comments'] = []
        self.params['t0_p'] = 0.
        self.params['t0_s'] = 0.
        self.params['vp'] = 0.
        self.params['vs'] = 0.
        self.params['d'] = 0.
        self.reflections = []
        self.params['modified'] = False


    def load_file(self, filename):
        """
        Reads a VPVS file into the VPVS object.

        Inputs:
           file:  The name of the file to read.

        Procedure:
           This procedure read the VPVS file.
        """
        self.__init__()
        # Initialize variables
        self._filename = 'filename'
        # Construct base name = file without path and without extension
        
        self._name = 'name'
        self.params['comments'] = ['comment']
        self.reflections = [vpvs_reflection()]

        
        self.params['vp'] = 5000
        self.params['vs'] = 3000
        self.params['d'] = 1
        self.compute_r()
        

        self.params['modified'] = False



    @property
    def filename(self):
        #if self.params['modified']:
        #    return self._filename + '*'
        #else:
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def name(self):
        #if self.params['modified']:
        #    return self._name + '*'
        #else:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def compute_v0(self):
        pass
    
    def compute_r0(self):
        """
        computes d0 values for the based on the the current lattice parameters
        """
        
        r_spacings = [  self.params['d']/1000/self.params['vp']]

        for ind in range(len(self.reflections)):
            self.reflections[ind].r0 = r_spacings[ind]

    def compute_r(self, *args, **kwargs):
        """
        
        """
        t0_p = kwargs.get('t0_p', None)
        if t0_p is not None:
            self.params['t0_p']=t0_p
        t0_s = kwargs.get('t0_s', None)
        if t0_s is not None:
            self.params['t0_s']=t0_s
        vp = kwargs.get('vp', None)
        if vp is not None:
            self.params['vp']=vp
        vs = kwargs.get('vs', None)
        if vs is not None:
            self.params['vs']=vs
        d = kwargs.get('d', None)
        if d is not None:
            self.params['d']=d

        self.compute_r0()
        r_spacings = []
        for r in self.reflections:
            r_spacings.append(r.r0)

        for ind in range(len(r_spacings)):
            self.reflections[ind].r = r_spacings[ind] + self.params['t0_p']

    

    def get_reflections(self):
        """
        Returns the information for each reflection for the material.
        This information is an array of elements of class vpvs_reflection
        """
        return self.reflections


   

