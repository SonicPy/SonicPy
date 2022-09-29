#!/usr/bin/env python



from functools import partial
import os.path

from PyQt5.QtCore import QObject
import numpy as np

#from utilities.utilities import *
from ia.widgets.ImageAnalysisWidget import ImageAnalysisWidget

from ia.models.ImageAnalysisModel import  ImageAnalysisModel

from um.widgets.UtilityWidgets import open_file_dialog
import pyqtgraph as pg
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
        
        order = self.model.settings['edge_polynomial_order'][0]
        self.display_window.order_options.buttons()[order-1].setChecked(True)

        fit_threshold = self.model.settings['edge_fit_threshold'][0]
        self.display_window.threshold_num.setValue(fit_threshold)

        bins = self.model.settings['horizontal_bin']
        self.display_window.plots['absorbance'].getAxis('bottom').setScale(bins)
        self.display_window.plots['edge1 fit'].getAxis('bottom').setScale(bins)
        self.display_window.plots['edge2 fit'].getAxis('bottom').setScale(bins)
        #self.display_window.plots['sobel vertical mean'].getAxis('bottom').setScale(bins)
       
        
        self.make_connections()
        self.display_window.raise_widget()

        #fname = os.path.join(resources_path, '6031psi_049.tif')
        #self.update_data(filename=fname)
        
        '''filename='resources/ultrasonic/4000psi-300K_+21MHz000.csv'
        self.update_data(filename=filename)'''

    def make_connections(self): 
        self.display_window.file_widget.file_selected_signal.connect(self.update_data)
        self.display_window.open_btn.clicked.connect(self.update_data)
        self.display_window.compute_btn.clicked .connect(self.update_cropped)
        self.display_window.save_btn.clicked.connect(self.save_result)

        self.display_window.crop_btn.clicked.connect(self.autocrop_btn_callback)
      
        self.display_window.edge_roi_1.sigRegionChangeFinished.connect(self.roi_changed_callback)
        self.display_window.edge_roi_2.sigRegionChangeFinished.connect(self.roi_changed_callback) 
        self.display_window.crop_roi.sigRegionChangeFinished.connect(self.crop_roi_changed_callback)

        self.display_window.edge_options.buttonClicked.connect(self.edge_type_selection_btn_callback)
        self.display_window.order_options.buttonClicked.connect(self.order_options_callback)

        self.display_window.threshold_num.editingFinished.connect(self.threshold_num_callback)

    def threshold_num_callback(self):
        num = self.display_window.threshold_num.value()
        
        self.model.settings['edge_fit_threshold'] = [num,num]

    def order_options_callback(self):
        btn = self.display_window.order_options.checkedButton()
        order  = int(btn.objectName()[6:7])
        self.model.settings['edge_polynomial_order'] = [order,order]

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
       
        if self.model.src is not None and self.display_window.compute_btn.isChecked() :
        
            thresholds = self.model.settings['edge_fit_threshold']
            orders = self.model.settings['edge_polynomial_order']

            img_plots = [self.display_window.imgs['edge1 fit'],self.display_window.imgs['edge2 fit']]
            edge_plots = [self.display_window.edge1_plt, self.display_window.edge2_plt]
            abs_plot = self.display_window.abs_plt
            
            abs_datas = []
            #legends = [self.display_window.edge1_plt_legend, self.display_window.edge2_plt_legend]
        
            for i, roi in enumerate(self.model.rois):
                masked_img, x_fit, y_fit = roi.compute(threshold = thresholds[i], order = orders[i])
                img_plots[i].setImage(masked_img)
                edge_plots[i].setData(x_fit, y_fit)
                '''p = roi.text
                note =  "y(x) = p[0]*x<sup>n</sup>+p[1]*x<sup>n-1</sup>+...+p[n]; p=" + p
                legends[i].renameItem(0,note)'''
                abs_datas.append([x_fit + roi.pos[0], y_fit + roi.pos[1]])

            roi1 = self.display_window.edge_roi_1
            roi2 = self.display_window.edge_roi_2
            r1_xmin = roi1.pos()[0]
            r1_xmax = roi1.pos()[0] + roi1.size()[0]
            r2_xmin = roi2.pos()[0]
            r2_xmax = roi2.pos()[0] + roi2.size()[0]

            min_x = min(r1_xmin,r2_xmin)
            max_x = max(r1_xmax,r2_xmax)
            
            n_samples = 50
            x_test = np.linspace(min_x, max_x, n_samples)
            edge1_y = self.model.rois[0].predict(x_test-self.model.rois[0].pos[0],orders[0])+ self.model.rois[0].pos[1]
            edge2_y = self.model.rois[1].predict(x_test-self.model.rois[1].pos[0],orders[1])+ self.model.rois[1].pos[1]
            y_diff = abs(np.mean(edge2_y - edge1_y))
            std_dev = np.std(edge2_y - edge1_y)

            output_txt = "mean: " + str(round(y_diff,1)) + '; std: ' +str(round(std_dev,1))
            self.display_window.result_lbl.setText(output_txt)

            data_x = np.array([])
            data_y = np.array([])
    
            data_x = np.append(np.append(x_test,np.nan),x_test)
            data_y = np.append(np.append(edge1_y,np.nan),edge2_y)
                
            abs_plot.setData(data_x, data_y)

    def update_frame(self):
        image = self.model.image
        img_shape = image.shape

        filtered = self.model.compute_sobel()
        
        self.display_window.imgs['absorbance'].setImage(image)

        #self.display_window.imgs['frame cropped'].setImage(image )
        #self.display_window.imgs['sobel y'].setImage(filtered)
        

        edges_dict = self.model.estimate_edges()
        edges = list(edges_dict.keys())[:2]
        
        #self.display_window.plots['sobel vertical mean'].plot(self.model.sobel_mean_vertical, clear=True)
        #self.display_window.plots['sobel vertical mean'].plot(self.model.blured_sobel_mean_vertical )

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
        
        if len(args):
            filename = args[0]
        else:
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
            self.update_cropped()

    def update_crop(self, *args, **kwargs):
        
        auto_crop = self.display_window.crop_btn.isChecked()
        if auto_crop :
            v_crop = self.get_vertical_autocrop()
            self.model.settings['crop_limits'] = self.model.get_auto_crop_limits(y=v_crop)
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

    def get_vertical_autocrop(self):
        btn = self.display_window.edge_options.checkedButton()
        lbl = btn.objectName()[5:8]
        v_crop = lbl[0] == '0' and lbl[2] == '0'
        return v_crop


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