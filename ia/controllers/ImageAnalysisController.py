#!/usr/bin/env python



import os.path, sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np

from numpy import arange
from numpy.core.fromnumeric import amax
from utilities.utilities import *
from ia.widgets.ImageAnalysisWidget import ImageAnalysisWidget

from ia.models.ImageAnalysisModel import  ImageAnalysisModel
from utilities.HelperModule import move_window_relative_to_screen_center, get_partial_index, get_partial_value
import math

from utilities.HelperModule import increment_filename, increment_filename_extra
from um.widgets.UtilityWidgets import open_file_dialog

from .. import resources_path


############################################################

class ImageAnalysisController(QObject):
    def __init__(self, app=None, offline = False):
        super().__init__()
        self.model = ImageAnalysisModel()
        self.fname = None
    
        if app is not None:
            self.setStyle(app)
        self.display_window = ImageAnalysisWidget()
        
        self.make_connections()
        self.display_window.raise_widget()

        fname = os.path.join(resources_path, 'SYLG_400psi_C.tif')
        self.update_data(filename=fname)
        
        '''filename='resources/ultrasonic/4000psi-300K_+21MHz000.csv'
        self.update_data(filename=filename)'''

    def make_connections(self): 
        self.display_window.open_btn.clicked.connect(self.update_data)
        self.display_window.save_btn.clicked.connect(self.save_result)
        self.display_window.edge_roi.sigRegionChanged.connect(self.update_cropped)
    

    def update_cropped(self):
        if self.model.src is not None:
            roi = self.display_window.edge_roi
            img = self.display_window.imgs[6]
            
            selected = roi.getArrayRegion(self.model.image, img)
            

            img_bg = self.model.get_background(selected, 20,80 )

            self.display_window.imgs[5].setImage(img_bg)

            
            
            bg_removed = selected - img_bg
            self.display_window.imgs[11].setImage(bg_removed)

            image, horizontal_edges, sobely = self.model.compute_canny(bg_removed)
            #horizontal_edges = 1* (horizontal_edges == 1)
            self.display_window.imgs[1].setImage(image)
            mean_peak = image.mean(axis=1)
            mean_peak_sobel = sobely.mean(axis=1)

            self.display_window.plots[8].plot(mean_peak, clear=True)
            self.display_window.plots[2].plot(mean_peak_sobel, clear=True)
            self.display_window.imgs[4].setImage(horizontal_edges)
            self.display_window.imgs[7].setImage(sobely)
    

    def save_result(self):
        if self.fname is not None:
            filename = self.fname + '.json'
            self.model.save_result(filename)


        

    def RecallSetupCallback(self):
        print('RecallSetupCallback')

    def SaveSetupCallback(self):
        print('SaveSetupCallback')

 
    def preferences_module(self, *args, **kwargs):
        pass

  

    def saveFile(self, filename, params = {}):
        pass

 
    
        
    def update_data(self, *args, **kwargs):
        filename = kwargs.get('filename', None)
        if filename is None:
            filename = open_file_dialog(None, "Load File(s).",filter='*.png;*.tif;*.bmp')
        if len(filename):
            self.model.load_file(filename)
            self.display_window.fname_lbl.setText(filename)
            self.display_window.imgs[0].setImage(self.model.src)
            image = self.model.image
            
            
            ## Display the data and assign each frame a time value from 1.0 to 3.0
            #self.display_window.imgs[3].setImage(image)

            filtered = self.model.compute_sobel()
            self.display_window.imgs[9].setImage(image)
            
            sobel_mean_vertical = filtered[:,35:65].mean(axis=1)
            
            self.model.estimate_edges()
            self.display_window.plots[3].plot(sobel_mean_vertical, clear=True)
            self.display_window.plots[3].plot(self.model.blured_sobel_mean_vertical )
            self.display_window.imgs[6].setImage(self.model.src_resized )

            self.display_window.imgs[10].setImage(filtered)

            #self.display_window.imgs[11].setImage(self.model.base_surface)

            self.display_window.crop_roi.setPos((self.model.crop_limits[0][0],self.model.crop_limits[0][1]))
            self.display_window.crop_roi.setSize((self.model.crop_limits[1][0],self.model.crop_limits[1][1]))
            #self.display_window.plots[7].plot(self.model.ver, clear=True)

    def show_window(self):
        self.display_window.raise_widget()

   

    def up_down_signal_callback(self, event):
        new_ind = self.waveform_index
        if event == 'up':
            new_ind = self.waveform_index + 1
        if event == 'down':
            new_ind = self.waveform_index - 1
        self.show_waveform(new_ind, update_cursor_pos=True)
                
    def show_latest_waveform(self):
        pass
    

    def setStyle(self, app):
        from .. import theme 
        from .. import style_path
        self.app = app
        if theme==1:
            WStyle = 'plastique'
            file = open(os.path.join(style_path, "stylesheet.qss"))
            stylesheet = file.read()
            self.app.setStyleSheet(stylesheet)
            file.close()
            self.app.setStyle(WStyle)
        else:
            WStyle = "windowsvista"
            self.app.setStyleSheet(" ")
            #self.app.setPalette(self.win_palette)
            self.app.setStyle(WStyle)