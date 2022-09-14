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

from um.models.tek_fileIO import read_tek_csv
 
logger = logging.getLogger(__name__)


class Overlay_xy():
    def __init__(self, filename):
        self.success = False
        basefile = os.path.basename(filename)
        self.name = basefile.split('.')[:-1][0]

        if filename.endswith('.csv'):
       
            data = self.get_data_from_csv_file(filename)

        else: return
            
        self.det_mode = ''
        self.det_setting = ''
        self.original_unit = ''
        unit = 't'
        if unit == 't':
            self.det_mode = ' '
        self.det_setting = ' '
        self.supported_scales = [' ']
        

        self.filename = filename
        self._original_x = data[0]
        self._original_y = data[1]

        

        self.scaling = 1
        self.offset = 0

        self.success=True

    def get_data_from_csv_file(self, filename):
        data = read_tek_csv(filename,subsample=2)
        return data

    def get_det_setting(self):
        return self.det_setting

    def get_supported_units(self):
        return self.supported_scales

    def get_pattern(self):
        x = self.makeXaxis()
        if x is None: return [[],[]]
        y = self.y_scale(self._original_y,self.scaling,self.offset)
        return [x, y]
    
    def makeXaxis(self):
        return self._original_x

    def y_scale(self, y, scale,offset):
        y = y*scale+offset
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
        return
        self.overlays.append(Overlay_xy())
        self.overlay_added.emit()
        return self.overlays[-1]

    

    def add_overlay_file(self, filename):
        """
        Reads a 2-column (x,y) text file or an mca file and adds it as overlay to the list of overlays
        :param filename: path of the file to be loaded
        :param x_scale: units for horizontal scale. Acceptable values are: 'E', 'q', or 'd'
        :param log_mode: whether vertical axis is in logarithmic scale mode. Needed to deal with zeros and low values.
        """
        if filename.endswith('.csv') :
            overlay = Overlay_xy(filename)
        
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
