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
        return "{:2d},{:2d},{:2d}\t{:.2f}\t{:.3f}".format(self.r, self.r*2,self.r*3, self.d, self.v)

    def get_r(self):
        return "%f %f %f"%(self.r,self.r*2,self.r*3)

    def get_r_list(self):
        return [self.r,self.r*2,self.r*3]



class MyDict(dict):
    def __init__(self):
        super(MyDict, self).__init__()
        self.setdefault('modified', False)


    def __setitem__(self, key, value):
        if key in ['comments',  'reflections', ]:
            self.__setitem__('modified', True)
        super(MyDict, self).__setitem__(key, value)

class vpvs(object):
    def __init__(self):
        self._filename = ''
        self._name = ''
        self.params = MyDict()
        self.params['comments'] = []
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
        self.reflections = [vpvs_reflection(),vpvs_reflection(),vpvs_reflection()]

        
        self.params['vp'] = 5000
        self.params['vs'] = 3000
        self.compute_r()
        for reflection in self.reflections:
            reflection.r = reflection.r

        self.params['modified'] = False



    @property
    def filename(self):
        if self.params['modified']:
            return self._filename + '*'
        else:
            return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def name(self):
        if self.params['modified']:
            return self._name + '*'
        else:
            return self._name

    @name.setter
    def name(self, value):
        self._name = value

    
    def compute_r0(self):
        """
        computes d0 values for the based on the the current lattice parameters
        """
        
        r_spacings = [ 1e-6, 2e-6, 4e-6]

        for ind in range(len(self.reflections)):
            self.reflections[ind].r0 = r_spacings[ind]

    def compute_r(self, shift=0):
        """
        
        """
        
        self.compute_r0()
        

        r_spacings = [ 1.1e-6, 2.1e-6, 4.1e-6]
        for ind in range(len(self.reflections)):

            self.reflections[ind].r = r_spacings[ind]

    def add_reflection(self, r=0, d = 0, v = 0):
        new_reflection = vpvs_reflection(r,d,v)
        self.reflections.append(new_reflection)
        self.params['modified'] = True

    def delete_reflection(self, ind):
        del self.reflections[ind]
        self.params['modified'] = True

    def get_reflections(self):
        """
        Returns the information for each reflection for the material.
        This information is an array of elements of class vpvs_reflection
        """
        return self.reflections

    

    def reorder_reflections_by_index(self, ind_list, reversed_toggle=False):
        if reversed_toggle:
            ind_list = ind_list[::-1]
        new_reflections = []
        for ind in ind_list:
            new_reflections.append(self.reflections[ind])

        modified_flag = self.params['modified']
        self.reflections = new_reflections
        self.params['modified'] = modified_flag

 
    def sort_reflections_by_r(self, reversed_toggle=False):
        r_list = []
        for reflection in self.reflections:
            r_list.append(reflection.r)
        sorted_ind = np.argsort(r_list)
        self.reorder_reflections_by_index(sorted_ind, reversed_toggle)

   

