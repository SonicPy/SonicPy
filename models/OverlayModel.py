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


import logging
import os
from copy import copy
from PyQt5 import QtCore
import numpy as np
from numpy import sin, pi

from utilities.HelperModule import FileNameIterator, get_base_name
from hpMCA.widgets.UtilityWidgets import xyPatternParametersDialog, selectDetectorDialog
from hpMCA.models.mcaModel import MCA

logger = logging.getLogger(__name__)

class Overlay_mca():
    def __init__(self, filename, x_scale, log_mode):
        self.mca = MCA()
        [_,self.success]=self.mca.read_file(filename)
        if not self.success:
            return
        self.detector=0      
        self.n_detectors = self.mca.n_detectors  
        if self.n_detectors>1:
            self.detector=selectDetectorDialog.showDialog(self.n_detectors)
        self.scaling = 1
        self.offset = 0
        self.log_scale = log_mode        
        self.x_scale = x_scale
        self.name = os.path.basename(self.mca.file_name)
        if self.detector>0:
            self.name += ', det. '+str(self.detector)
        self.data = self.mca.get_data()[self.detector]
        self.bins = self.mca.get_bins(self.detector)
        self.calibration = self.mca.get_calibration()[self.detector]
        self.tth = self.calibration.two_theta
        self.det_mode = 'EDXD'

    def get_det_setting(self):
        return str(self.tth) + ' deg'

    def get_supported_units(self):
        return ['E','q','d']

    def get_pattern(self):
        x = self.calibration.channel_to_scale(self.bins,self.x_scale)
        y = y_scale(self.data,self.scaling,self.offset,self.log_scale)
        return [x, y]

class Overlay_xy():
    def __init__(self, filename, x_scale, log_mode):
        self.success = False
        basefile=os.path.basename(filename)
        if filename.endswith('.chi'):
            fp = open(filename, 'r')
            first_line = fp.readline()
            second_line = fp.readline()
            unit = second_line.strip().upper()[:1]
            fp.close()
            
            skiprows = 4
        elif filename.endswith('.xy'):
            skiprows = 0
            f = open(filename, 'r')
            line = ''
            while 1 :
                prev_line = line
                line = f.readline()
                if not line.strip().startswith('#') : break # stop the loop if no line was read
                skiprows += 1
            f.close() # after the loop, not in it
            if skiprows >0:
                unit = prev_line.strip()[1:].strip().upper()[:1]
        else: return
            
        self.det_mode = ''
        self.det_setting = ''
        self.original_unit = ''
        if unit == '2':
            self.det_mode = 'ADXD'
            self.wavelength = xyPatternParametersDialog.showDialog(basefile,'wavelength',0.406626)
            self.det_setting = str(self.wavelength) + ' ' + f'\N{LATIN CAPITAL LETTER A WITH RING ABOVE}'
            self.original_unit = 'tth'
            self.supported_scales = ['q','d']
        elif unit =='E':
            self.det_mode = 'EDXD'
            self.tth = xyPatternParametersDialog.showDialog(basefile,'tth',15)
            self.det_setting = str(self.tth) + ' deg'
            self.original_unit = 'E'
            self.supported_scales = ['E','q','d']
        elif unit == 'Q':
            self.det_mode = 'q'
            self.original_unit = 'q'
            self.supported_scales = ['q','d']
        elif unit == 'D':
            self.det_mode = 'd'
            self.original_unit = 'd'
            self.supported_scales = ['q','d']    
        else:
            self.supported_scales = [] 
            return    
                
        data = np.loadtxt(filename, skiprows=skiprows)
        self.filename = filename
        self._original_x = data.T[0]
        self._original_y = data.T[1]
        self.name = os.path.basename(filename).split('.')[:-1][0]
        self.log_scale = log_mode        
        self.x_scale = x_scale
        self.scaling = 1
        self.offset = 0
        self.n_detectors = 1
        self.success=True

    def get_det_setting(self):
        return self.det_setting

    def get_supported_units(self):
        return self.supported_scales
    def get_pattern(self):
        x = self.makeXaxis()
        if x is None: return [[],[]]
        y = y_scale(self._original_y,self.scaling,self.offset,self.log_scale)
        return [x, y]
    
    def makeXaxis(self):
        if self.x_scale == 'E':
            if self.original_unit == 'E':
                return self._original_x
            else: return None
        elif self.x_scale == 'd':
            if self.original_unit == 'E':
                return E_to_d(self._original_x,self.tth)
            elif self.original_unit == 'q':
                return q_to_d(self._original_x)
            elif self.original_unit == 'd':
                return self._original_x
            elif self.original_unit == 'tth':
                return tth_to_d(self._original_x,self.wavelength)
            else: return None
        elif self.x_scale == 'q':
            if self.original_unit == 'E':
                return E_to_q(self._original_x,self.tth)
            elif self.original_unit == 'q':
                return self._original_x
            elif self.original_unit == 'd':
                return d_to_q(self._original_x)
            elif self.original_unit == 'tth':
                return tth_to_q(self._original_x,self.wavelength)
            else: return None
        else:
            return None

def E_to_q(e,tth):
    q = 6.28318530718 /(6.199 / e / sin(tth/180.*pi/2.))
    return q

def E_to_d(e,tth):
    q = E_to_q(e,tth)
    d = q_to_d(q)
    return d

def d_to_q(d):
    q = 2. * pi / d
    return q

def q_to_d(q):
    d = 2. * pi / q
    return d

def tth_to_d(tth,wavelength):
    
    d = wavelength/(2.0 * sin(0.5 * tth * 0.0174532925199433))
    return d

def tth_to_q(tth,wavelength):
    d = tth_to_d(tth,wavelength)
    q = d_to_q(d)
    return q

def y_scale(y, scale,offset,log_scale):
    if log_scale:
        y = np.clip(y,0.5,None)
    y = y*scale+offset
    if log_scale:
        y = np.clip(y,10e-8,None)
    return y

class OverlayModel(QtCore.QObject):
    """
    Main Overlay MCA Handling Model. ,
    """

    overlay_changed = QtCore.pyqtSignal(int)  # changed index
    overlay_added = QtCore.pyqtSignal()
    overlay_removed = QtCore.pyqtSignal(int)  # removed index

    def __init__(self):
        super().__init__()
        self.overlays = []
        self.default_wavelength = 0.406626
        self.default_tth = 15

    def set_x_scale (self, scale=''):
        for overlay in self.overlays:
            overlay.x_scale = scale
            self.overlay_changed.emit(self.overlays.index(overlay))

    def set_log_scale(self, scale=False):
        for overlay in self.overlays:
            overlay.log_scale = scale
            self.overlay_changed.emit(self.overlays.index(overlay))

    def add_overlay(self, x, y, name=''):  #needs fixing !!!!
        """
        Adds an overlay to the list of overlays
        :param x: x-values
        :param y: y-values
        :param name: name of overlay to be used for displaying etc.
        """
        self.overlays.append(Overlay_xy())
        self.overlay_added.emit()
        return self.overlays[-1]

    

    def add_overlay_file(self, filename, x_scale, log_mode):
        """
        Reads a 2-column (x,y) text file or an mca file and adds it as overlay to the list of overlays
        :param filename: path of the file to be loaded
        :param x_scale: units for horizontal scale. Acceptable values are: 'E', 'q', or 'd'
        :param log_mode: whether vertical axis is in logarithmic scale mode. Needed to deal with zeros and low values.
        """
        if filename.endswith('.chi') or filename.endswith('.xy'):
            overlay = Overlay_xy(filename, x_scale, log_mode)
        else:
            overlay = Overlay_mca(filename,x_scale, log_mode)
        if overlay.success:
            self.overlays.append(overlay)
            self.overlay_added.emit()

    def remove_overlay(self, ind):
        """
        Removes an overlay from the list of overlays
        :param ind: index of the overlay
        """
        if ind >= 0:
            del self.overlays[ind]
            self.overlay_removed.emit(ind)

    def get_overlay(self, ind):
        """
        :param ind: overlay ind
        :return: returns overlay if existent or None if it does not exist
        """
        try:
            return self.overlays[ind]
        except IndexError:
            return None


    def set_overlay_scaling(self, ind, scaling):
        """
        Sets the scaling of the specified overlay
        :param ind: index of the overlay
        :param scaling: new scaling value
        """
        self.overlays[ind].scaling = scaling
        self.overlay_changed.emit(ind)

    def get_overlay_scaling(self, ind):
        """
        Returns the scaling of the specified overlay
        :param ind: index of the overlay
        :return: scaling value
        """
        return self.overlays[ind].scaling

    def set_overlay_offset(self, ind, offset):
        """
        Sets the offset of the specified overlay
        :param ind: index of the overlay
        :param offset: new offset value
        """
        self.overlays[ind].offset = offset
        self.overlay_changed.emit(ind)

    def get_overlay_offset(self, ind):
        """
        Return the offset of the specified overlay
        :param ind: index of the overlay
        :return: overlay value
        """
        return self.overlays[ind].offset

    def overlay_waterfall(self, separation):
        offset = 0
        for ind in range(len(self.overlays)):
            offset += separation
            self.overlays[ind ].offset = offset
            self.overlay_changed.emit(ind )

    def reset_overlay_offsets(self):
        for ind, overlay in enumerate(self.overlays):
            overlay.offset = 0
            self.overlay_changed.emit(ind)

    def reset(self):
        for _ in range(len(self.overlays)):
            self.remove_overlay(0)
