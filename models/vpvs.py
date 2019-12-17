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


class vpvs_reflection():
    """
    Class that defines a reflection.
    Attributes:
   
    """

    def __init__(self, r = 0., d=0., v=0., mode='p',index = 0):
        self.d = d
        self.v = v
        self.r0 = r
        self.r = r
        self.mode = mode
        
    def __str__(self):
        return "{:2d}\t{:.2f}\t{:.3f}".format(self.r, self.d, self.v)


class MyDict(dict):
    def __init__(self):
        super(MyDict, self).__init__()
        self.setdefault('modified', False)


    def __setitem__(self, key, value):
        if key in ['comments',  't_0','t0_p', 't0_s', 'vp', 'vs','d']:
            self.__setitem__('modified', True)
        super(MyDict, self).__setitem__(key, value)

class vpvs(object):
    def __init__(self):
        self._filename = ''
        self._name = ''
        self.params = MyDict()
        self.params['comments'] = []
        self.params['t_0'] = 0.
        self.params['t0_p'] = 0.
        self.params['t0_s'] = 0.
        self.params['t0_p_2'] = 0.
        self.params['t0_s_2'] = 0.
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
        self._filename = 'R'
        self._index = 0
        # Construct base name = file without path and without extension
        
        self._name = 'R'
        self.params['comments'] = ['comment']
        self.reflections = [vpvs_reflection(),vpvs_reflection(),vpvs_reflection(),vpvs_reflection()]

        
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
        return self._filename + str(self._index)

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def name(self):
        #if self.params['modified']:
        #    return self._name + '*'
        #else:
        return self._name + str(self._index)

    @name.setter
    def name(self, value):
        self._name = value

    def compute_v0(self):
        pass
    
    def compute_r0(self):
        """
        computes d0 values for the based on the the current lattice parameters
        """
        
        try:
            vp_t = self.params['d']/1000/self.params['vp']*2
        except:
            vp_t = 0    
        try:
            vs_t = self.params['d']/1000/self.params['vs']*2
        except:
            vs_t = 0

        self.reflections[0].r0 = vp_t
        self.reflections[1].r0 = vs_t

        # "tripple transit" reflections:
        self.reflections[2].r0 = vp_t * 2
        self.reflections[3].r0 = vs_t * 2


    def compute_r(self, *args, **kwargs):
        """
        
        """
        t_0 = kwargs.get('t_0', None)
        if t_0 is not None:
            self.params['t_0']=t_0
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
        r_spacings = [self.reflections[0].r0,self.reflections[1].r0,self.reflections[2].r0,self.reflections[3].r0]
        

        self.reflections[0].r = r_spacings[0] + self.params['t0_p'] + self.params['t_0'] * 1e-6
        self.reflections[1].r = r_spacings[1]+ self.params['t0_s'] + self.params['t_0'] * 1e-6

        self.reflections[2].r = self.reflections[0].r * 2  - self.params['t_0'] * 1e-6
        self.reflections[3].r = self.reflections[1].r * 2 - self.params['t_0'] * 1e-6
        #print(self.reflections)

    def get_reflections(self):
        """
        Returns the information for each reflection for the material.
        This information is an array of elements of class vpvs_reflection
        """
        return self.reflections


   

