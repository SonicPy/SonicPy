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
        self.display_window.raise_widget()

        fname = os.path.join(resources_path, '6031psi_049.tif')
        self.update_data(filename=fname)
        
        '''filename='resources/ultrasonic/4000psi-300K_+21MHz000.csv'
        self.update_data(filename=filename)'''

    def make_connections(self): 
        self.display_window.open_btn.clicked.connect(self.update_data)
        self.display_window.compute_btn.clicked.connect(self.update_cropped)
        self.display_window.save_btn.clicked.connect(self.save_result)

        self.display_window.crop_btn.clicked.connect(self.autocrop_btn_callback)
      
        self.display_window.edge_roi_1.sigRegionChangeFinished.connect(self.roi_changed_callback)
        self.display_window.edge_roi_2.sigRegionChangeFinished.connect(self.roi_changed_callback) 
        self.display_window.crop_roi.sigRegionChangeFinished.connect(self.crop_roi_changed_callback)

        self.display_window.edge_options.buttonClicked.connect(self.edge_type_selection_btn_callback)


    def roi_changed_callback(self):
        self.update_roi()

    def update_roi(self):

        rois = [self.display_window.edge_roi_1,self.display_window.edge_roi_2]
        if self.model.src is not None:
            for i, roi in enumerate(rois):
                img = self.display_window.imgs['absorbance']
                selected = roi.getArrayRegion(self.model.image, img)
                self.model.rois[i].pos =  roi.pos() 
                self.model.rois[i].size =  roi.size()
                self.model.rois[i].image = selected
            
            edges = self.get_edge_types()
            self.set_edge_types(edges)

    def update_cropped(self):
        if self.model.src is not None :
        
            thresholds = self.model.settings['edge_fit_threshold']
            orders = self.model.settings['edge_polynomial_order']

            img_plots = [self.display_window.imgs['edge1 fit'],self.display_window.imgs['edge2 fit']]
            edge_plots = [self.display_window.edge1_plt, self.display_window.edge2_plt]

            for i, roi in enumerate(self.model.rois):
                masked_img, x_fit, y_fit = roi.compute(threshold = thresholds[i], order = orders[i])
                img_plots[i].setImage(masked_img)
                edge_plots[i].setData(x_fit, y_fit)

    def update_frame(self):
        image = self.model.image
        img_shape = image.shape

        filtered = self.model.compute_sobel()
        
        self.display_window.imgs['absorbance'].setImage(image)

        #self.display_window.imgs['frame cropped'].setImage(image )
        self.display_window.imgs['sobel y'].setImage(filtered)
        

        edges_dict = self.model.estimate_edges()
        edges = list(edges_dict.keys())[:2]
        
        self.display_window.plots['sobel vertical mean'].plot(self.model.sobel_mean_vertical, clear=True)
        self.display_window.plots['sobel vertical mean'].plot(self.model.blured_sobel_mean_vertical )

        rois = [self.display_window.edge_roi_1,self.display_window.edge_roi_2]
        self.model.rois = []
       
        for i, edge in enumerate(edges):
            roi = rois[i]
            roi.sigRegionChangeFinished.disconnect(self.roi_changed_callback)
            roi.setPos(0, edge-edges_dict[edge][1]/2-40)
            roi.setSize((img_shape[1], edges_dict[edge][1]+80))
            roi.sigRegionChangeFinished.connect(self.roi_changed_callback)

        img = self.display_window.imgs['absorbance']
        for i, roi in enumerate(rois):  
            selected = roi.getArrayRegion(self.model.image, img)
            self.model.add_ROI(selected, roi.pos(), roi.size())

        self.update_roi()
        
    def update_data(self, *args, **kwargs):
        filename = kwargs.get('filename', None)
        if filename is None:
            filename = open_file_dialog(None, "Load File(s).",filter='*.png;*.tif;*.bmp')
        if len(filename):
            
            self.model.load_file(filename)
            self.display_window.fname_lbl.setText(filename)
            self.display_window.imgs['src'].setImage(self.model.src)

            self.update_crop()
            self.model.filter_image()
            self.update_frame()

    def update_crop(self, *args, **kwargs):
        
        auto_crop = self.display_window.crop_btn.isChecked()
        if auto_crop :
            self.model.settings['crop_limits'] = self.model.get_auto_crop_limits()
        self.model.crop()
        
        crop_limits = self.model.settings['crop_limits']
        self.display_window.crop_roi.sigRegionChangeFinished.disconnect(self.crop_roi_changed_callback)
        self.display_window.crop_roi.setPos((crop_limits[0][0],crop_limits[0][1]))
        self.display_window.crop_roi.setSize((crop_limits[1][0],crop_limits[1][1]))
        self.display_window.crop_roi.sigRegionChangeFinished.connect(self.crop_roi_changed_callback)

    def autocrop_btn_callback(self, btn):
        if btn:
            self.update_crop()
            self.model.filter_image()
            self.update_frame()

    def crop_roi_changed_callback(self, roi:pg.graphicsItems.ROI.ROI):
        self.display_window.crop_btn.setChecked(False)
        pos = [int(roi.pos()[0]),int(roi.pos()[1])]
        size = [int(roi.size()[0]),int(roi.size()[1])]
        roi_limits = [pos,size]
        self.model.settings['crop_limits'] = roi_limits
        self.update_crop()
        self.model.filter_image()
        self.update_frame()
        

    def show_window(self):
        self.display_window.raise_widget()

    def edge_type_selection_btn_callback(self, *args, **kwargs):
        
        
        edges = self.get_edge_types()
        self.set_edge_types(edges)

    def get_edge_types(self):
        btn = self.display_window.edge_options.checkedButton()
        lbl = btn.objectName()[5:8]

        '''possible values for lbl should be '000', '100', '001', '101', '010', 
        where 0 = low Z layer, 1 = high Z layer
        edge type determine whether edge fitting is done using the 
        absorbance image (0-type edges) or the sobel-Y filtered image (1-type edges)
        '''

        edges = [ 1*(lbl[1]!=lbl[2]), 1*(lbl[0]!=lbl[1])]
        return edges

    def set_edge_types(self, edges):
        
        rois = self.model.rois
        for i, roi in enumerate(rois):
            roi.edge_type = edges[i]
            
    def up_down_signal_callback(self, event):
        new_ind = self.waveform_index
        if event == 'up':
            new_ind = self.waveform_index + 1
        if event == 'down':
            new_ind = self.waveform_index - 1
        self.show_waveform(new_ind, update_cursor_pos=True)

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