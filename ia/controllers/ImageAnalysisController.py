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
import pyqtgraph as pg
from .. import resources_path
import copy

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
        self.edge1_plt = self.display_window.plots['edge1 fit'].plot([], pen = pg.mkPen((255,0,0, 180),width=3,style=pg.QtCore.Qt.DotLine))
        self.edge2_plt = self.display_window.plots['edge2 fit'].plot([], pen = pg.mkPen((255,0,0, 180),width=3,style=pg.QtCore.Qt.DotLine))

        self.display_window.raise_widget()

        fname = os.path.join(resources_path, '6031psi_049.tif')
        self.update_data(filename=fname)
        
        '''filename='resources/ultrasonic/4000psi-300K_+21MHz000.csv'
        self.update_data(filename=filename)'''

    def make_connections(self): 
        self.display_window.open_btn.clicked.connect(self.update_data)
        self.display_window.compute_btn.clicked.connect(self.update_cropped)
        self.display_window.save_btn.clicked.connect(self.save_result)
      
        self.display_window.edge_roi_1.sigRegionChangeFinished.connect(self.update_roi)
        self.display_window.edge_roi_2.sigRegionChangeFinished.connect(self.update_roi) 
        #self.display_window.crop_roi.sigRegionChangeFinished.connect(self.update_frame)

    def update_roi(self):
        if self.model.src is not None:
            roi1 = self.display_window.edge_roi_1
            roi2 = self.display_window.edge_roi_2
            img = self.display_window.imgs['frame cropped']
            
            selected = roi1.getArrayRegion(self.model.image, img)
            selected2 = roi2.getArrayRegion(self.model.image, img)
            self.model.rois[0].pos =  roi1.pos() 
            self.model.rois[1].pos =  roi2.pos()
            self.model.rois[0].size =  roi1.size()
            self.model.rois[1].size =  roi2.size()
            self.model.rois[0].image = selected
            self.model.rois[1].image = selected2

    def update_cropped(self):
        if self.model.src is not None :
            
            threshold = 0.3
            order = 3

            roi1 = self.model.rois[0]
            masked_img, x_fit, y_fit = roi1.compute(threshold = threshold, order = order)
            
            roi2 = self.model.rois[1]
            masked_img2, x_fit2, y_fit2 = roi2.compute(threshold = threshold, order = order)

            self.display_window.imgs['edge1 fit'].setImage(masked_img)
            self.display_window.imgs['edge2 fit'].setImage(masked_img2)
            
            self.edge1_plt.setData(x_fit, y_fit)
            self.edge2_plt.setData(x_fit2, y_fit2)

   

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

    
 
    def update_frame(self):
        image = self.model.image
        img_shape = image.shape

        filtered = self.model.compute_sobel()
        
        self.display_window.imgs['absorbance'].setImage(image)
        
        sobel_mean_vertical = filtered[:,35:65].mean(axis=1)
        
        edges_dict = self.model.estimate_edges()
        edges = list(edges_dict.keys())


        self.display_window.edge_roi_1.sigRegionChangeFinished.disconnect(self.update_roi)
        self.display_window.edge_roi_2.sigRegionChangeFinished.disconnect(self.update_roi) 

        roi1 = self.display_window.edge_roi_1
        roi2 = self.display_window.edge_roi_2

        


        roi1.setPos(0, edges[0]-edges_dict[edges[0]][1]/2-40)
        roi2.setPos(0, edges[1]-edges_dict[edges[1]][1]/2-40)
        roi1.setSize((img_shape[1], edges_dict[edges[0]][1]+80))
        roi2.setSize((img_shape[1], edges_dict[edges[1]][1]+80))
        img = self.display_window.imgs['frame cropped'] 

        selected = roi1.getArrayRegion(self.model.image, img)
        selected2 = roi2.getArrayRegion(self.model.image, img)

        self.model.rois = []
        
        self.model.add_ROI(selected, roi1.pos(), roi1.size())
        self.model.add_ROI(selected2, roi2.pos(), roi1.size())

        self.display_window.plots['sobel vertical mean'].plot(sobel_mean_vertical, clear=True)
        self.display_window.plots['sobel vertical mean'].plot(self.model.blured_sobel_mean_vertical )
        self.display_window.imgs['frame cropped'].setImage(self.model.src_resized )

        self.display_window.imgs['sobel y'].setImage(filtered)

        self.update_roi()
        self.display_window.edge_roi_1.sigRegionChangeFinished.connect(self.update_roi)
        self.display_window.edge_roi_2.sigRegionChangeFinished.connect(self.update_roi) 
        
    def update_data(self, *args, **kwargs):
        filename = kwargs.get('filename', None)
        if filename is None:
            filename = open_file_dialog(None, "Load File(s).",filter='*.png;*.tif;*.bmp')
        if len(filename):
            crop = self.display_window.crop_btn.isChecked()
            
            self.model.load_file(filename, autocrop=crop)
            self.model.filter_image()
            
            self.display_window.fname_lbl.setText(filename)
            self.display_window.imgs['src'].setImage(self.model.src)

            self.display_window.crop_roi.setPos((self.model.crop_limits[0][0],self.model.crop_limits[0][1]))
            self.display_window.crop_roi.setSize((self.model.crop_limits[1][0],self.model.crop_limits[1][1]))

            self.update_frame()

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