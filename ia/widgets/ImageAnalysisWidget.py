#!/usr/bin/env python


import os, os.path
from PyQt5 import uic, QtWidgets,QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow 
from PyQt5.QtCore import QObject, pyqtSignal, Qt

import pyqtgraph as pg
from pyqtgraph import QtCore 
from um.widgets.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton, NumberTextField
from ia.widgets.FileViewWidget import FileViewWidget

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

from .. import style_path, icons_path,title

class ImageAnalysisWidget(QMainWindow):
    
    preferences_signal = pyqtSignal()
    up_down_signal = pyqtSignal(str)
    panelClosedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.initialized = False
        self.t = None
        self.spectrum = None


        self.setWindowTitle(title)

        self.resize(1100, 770)
        
        self.make_widget()


        self.setCentralWidget(self.splitter_widget)

        self.create_plots()
        self.create_menu()
        self.style_widgets()

    def create_plots(self):

        self.make_roi()
        self.make_edge_roi(self.plots['absorbance'])



    def update_view(self, image):
        pass
    


    def make_widget(self):


        self.splitter_widget = QtWidgets.QSplitter(Qt.Horizontal)

        self.file_widget = FileViewWidget()
        self.file_widget.setMinimumWidth(330)
        self.splitter_widget .addWidget(self.file_widget)

        self.analysis_widget = QtWidgets.QWidget()

        self.splitter_widget .addWidget(self.analysis_widget)
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(10, 10, 10, 10)

        

        self.detail_widget = QtWidgets.QWidget()
        self._detail_layout = QtWidgets.QHBoxLayout()
        self._detail_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget_top = QtWidgets.QWidget()
        self._buttons_layout_top = QtWidgets.QHBoxLayout()
        self._buttons_layout_top.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget_bottom = QtWidgets.QWidget()
        self._buttons_layout_bottom = QtWidgets.QHBoxLayout()
        self._buttons_layout_bottom.setContentsMargins(0, 0, 0, 0)
        self.open_btn = QtWidgets.QPushButton("Open")
        self.crop_btn = QtWidgets.QPushButton("Auto crop")
        self.crop_btn.setCheckable(True)
        self.crop_btn.setChecked(True)
        self.compute_btn = QtWidgets.QPushButton("Compute")
        self.compute_btn.setCheckable(True)
        self.fname_lbl = QtWidgets.QLineEdit('')
        
        self.save_btn = QtWidgets.QPushButton('Save result')
        self.result_lbl = QtWidgets.QLineEdit('')

        self._buttons_layout_top.addWidget(self.open_btn)
        
        self._buttons_layout_top.addWidget(self.compute_btn)
        self._buttons_layout_top.addWidget(QtWidgets.QLabel("   File"))
        self._buttons_layout_top.addWidget(self.fname_lbl)
       
        
        self._buttons_layout_top.addWidget(QtWidgets.QLabel("   Distance"))
        self._buttons_layout_top.addWidget(self.result_lbl)
        #self._buttons_layout_top.addWidget(self.save_btn)
        self._buttons_layout_top.addSpacerItem(HorizontalSpacerItem())
    
        self.buttons_widget_top.setLayout(self._buttons_layout_top)
        self._layout.addWidget(self.buttons_widget_top)


        self.menu_bar = QtWidgets.QWidget(self.analysis_widget)
        self._menu_bar_layout = QtWidgets.QHBoxLayout(self.menu_bar)
        self._menu_bar_layout.setContentsMargins(0,0,0,0)

        self._menu_bar_layout.addWidget(self.crop_btn)

        self._menu_bar_layout.addWidget(QtWidgets.QLabel('      Sample type'))

        self.edge_options_widget = QtWidgets.QWidget(self.analysis_widget)
        self._edge_options_widget_layout = QtWidgets.QHBoxLayout(self.edge_options_widget)
        self._edge_options_widget_layout.setSpacing(0)
        self.edge_options = QtWidgets.QButtonGroup(self.edge_options_widget)
        self.edge_000_btn = QtWidgets.QPushButton()
        self.edge_100_btn = QtWidgets.QPushButton()
        self.edge_001_btn = QtWidgets.QPushButton()
        self.edge_101_btn = QtWidgets.QPushButton()
        self.edge_010_btn = QtWidgets.QPushButton()

        self.edge_000_btn.setObjectName('edge_000_btn')
        self.edge_100_btn.setObjectName('edge_100_btn')
        self.edge_001_btn.setObjectName('edge_001_btn')
        self.edge_101_btn.setObjectName('edge_101_btn')
        self.edge_010_btn.setObjectName('edge_010_btn')

        self.edge_000_btn.setCheckable(True)
        self.edge_100_btn.setCheckable(True)
        self.edge_001_btn.setCheckable(True)
        self.edge_101_btn.setCheckable(True)
        self.edge_010_btn.setCheckable(True)
        
        self.edge_options.addButton(self.edge_000_btn)
        self.edge_options.addButton(self.edge_100_btn)
        self.edge_options.addButton(self.edge_001_btn)
        self.edge_options.addButton(self.edge_101_btn)
        self.edge_options.addButton(self.edge_010_btn)
        self.edge_000_btn.setChecked(True)

        self._edge_options_widget_layout.addWidget(self.edge_000_btn)
        self._edge_options_widget_layout.addWidget(self.edge_010_btn)
        self._edge_options_widget_layout.addWidget(self.edge_001_btn)
        self._edge_options_widget_layout.addWidget(self.edge_100_btn)  
        self._edge_options_widget_layout.addWidget(self.edge_101_btn)

        self.edge_options_widget.setLayout(self._edge_options_widget_layout)

        self._menu_bar_layout.addWidget(self.edge_options_widget)

        


        self.order_options = QtWidgets.QButtonGroup(self.analysis_widget)
        self.order_btns_widget = QtWidgets.QWidget(self.analysis_widget)
        self._order_btns_widget_layout = QtWidgets.QHBoxLayout(self.order_btns_widget)
        self._order_btns_widget_layout.setSpacing(0)
        self.order_1_btn = QtWidgets.QPushButton('1')
        self.order_2_btn = QtWidgets.QPushButton('2')
        self.order_3_btn = QtWidgets.QPushButton('3')
        self.order_1_btn.setObjectName('order_1_btn')
        self.order_2_btn.setObjectName('order_2_btn')
        self.order_3_btn.setObjectName('order_3_btn')
        self.order_1_btn.setCheckable(True)
        self.order_2_btn.setCheckable(True)
        self.order_3_btn.setCheckable(True)
        self.order_options.addButton(self.order_1_btn)
        self.order_options.addButton(self.order_2_btn)
        self.order_options.addButton(self.order_3_btn)
        self.order_2_btn.setChecked(True)
        self._order_btns_widget_layout.addWidget(self.order_1_btn)
        self._order_btns_widget_layout.addWidget(self.order_2_btn)
        self._order_btns_widget_layout.addWidget(self.order_3_btn)
        self.order_btns_widget.setLayout(self._order_btns_widget_layout)

        self._menu_bar_layout.addWidget(QtWidgets.QLabel('   Polynomial order'))
        self._menu_bar_layout.addWidget(self.order_btns_widget)

        self.threshold_num = NumberTextField()
        self.threshold_num.setMinimum(0)
        self.threshold_num.setMaximum(1)
        self.threshold_num.setValue(0.3)

        self.threshold_num.setMaximumWidth(50)
        self._menu_bar_layout.addWidget(QtWidgets.QLabel('   Fit threshold'))
        self._menu_bar_layout.addWidget(self.threshold_num)

        self._menu_bar_layout.addSpacerItem(HorizontalSpacerItem())

        

        self._layout.addWidget(self.menu_bar)

        self.plot_grid = pg.GraphicsLayoutWidget(self.analysis_widget)
        
        self.plot_grid.setBackground((255,255,255))
        #self._plot_grid_layout = QtWidgets.QGridLayout(self.plot_grid)

        plots_settings = {  'src':['img','Source image, (<i>I</i>/<i>I</i><sub>0</sub>)',True],
                            'edge2 fit':['img', 'Edge 2', False],
                            'absorbance':['img', u'Absorbance (<i>A</i>) = -log<sub>10</sub>(<i>I</i>/<i>I</i><sub>0</sub>) ', False], 
                            #'frame cropped':['img','Cropped Frame',False],
                            'edge1 fit':['img','Edge 1', False]
                            
                            #'sobel y': ['img',u'Vertical gradient |𝜕<sub>𝑦</sub>𝛢|', False],
                            #'sobel vertical mean':['plot','Sobel y filter vertical mean',False]   
                            }
        self.imgs = {}
        
        self.plots = {}
        
        col = 0
        for plot_label in plots_settings:
            
            if col >1:
                col = 0
                self.plot_grid.nextRow()

            plot_type = plots_settings[plot_label][0]
            title = plots_settings[plot_label][1]
            plt = self.plot_grid.addPlot(title=title)
            if plot_type == 'img':
                square = plots_settings[plot_label][2]
                view = plt.getViewBox()
                if square:
                    view.setAspectLocked(True)
                img = pg.ImageItem()
                plt.addItem(img)
                self.imgs[plot_label] =img
                self.plots[plot_label]=plt
            elif plot_type == 'plot':
                
                self.plots[plot_label]=plt
            
        
            col = col + 1
            
        self.edge1_plt = self.plots['edge1 fit'].plot([], pen = pg.mkPen((255,0,0, 180),width=4,style=pg.QtCore.Qt.DotLine))
      
        self.edge2_plt = self.plots['edge2 fit'].plot([], pen = pg.mkPen((255,0,0, 180),width=4,style=pg.QtCore.Qt.DotLine))
      
        self.abs_plt = self.plots['absorbance'].plot([], pen = pg.mkPen((255,0,0, 180),width=4,style=pg.QtCore.Qt.DotLine),connect='finite')
  

        self._layout.addWidget(self.plot_grid)
        
        calc_btn = QtWidgets.QPushButton('Correlate')
        #_buttons_layout_bottom.addWidget(calc_btn)
        #_buttons_layout_bottom.addWidget(QtWidgets.QLabel('2-way travel time:'))
        output_ebx = QtWidgets.QLineEdit('')
        #_buttons_layout_bottom.addWidget(output_ebx)
        self._buttons_layout_bottom.addSpacerItem(HorizontalSpacerItem())
        self.buttons_widget_bottom.setLayout(self._buttons_layout_bottom)
        self._layout.addWidget(self.buttons_widget_bottom)
        self.analysis_widget.setLayout(self._layout)

    

    def make_roi(self):
        # Custom ROI for selecting an image region
        self.crop_roi = pg.ROI([50, 200], [150, 100])
        self.crop_roi.setPen(pg.mkPen((255,0,0), width=3))
        self.crop_roi.addScaleHandle([0, 1], [1, 0])
        self.crop_roi.addScaleHandle([1, 0], [0, 1])
        self.crop_roi.addScaleHandle([0, 0], [1, 1])
        self.crop_roi.addScaleHandle([1, 1], [0, 0])

        self.crop_roi.addScaleHandle([0, .5], [1, .5])
        self.crop_roi.addScaleHandle([1, .5], [0, .5])

        self.crop_roi.addScaleHandle([.5, 0], [0.5, 1])
        self.crop_roi.addScaleHandle([.5, 1], [0.5, 0])
        
        self.crop_roi.setZValue(10)  # make sure ROI is drawn above image
        self.plots['src'].addItem(self.crop_roi)

    def make_edge_roi(self, plot):
        # Custom ROI for selecting an image region
        self.edge_roi_1 = pg.ROI([5, 100], [60, 100])
        self.edge_roi_1.setPen(pg.mkPen((0,200,0), width=3))
        handle1 = self.edge_roi_1.addScaleHandle([0, 1], [1, 0])
        handle2 = self.edge_roi_1.addScaleHandle([1, 0], [0, 1])

        self.edge_roi_1.addScaleHandle([0, 0], [1, 1])
        self.edge_roi_1.addScaleHandle([1, 1], [0, 0])

        self.edge_roi_1.addScaleHandle([0, .5], [1, .5])
        self.edge_roi_1.addScaleHandle([1, .5], [0, .5])

        self.edge_roi_1.addScaleHandle([.5, 0], [0.5, 1])
        self.edge_roi_1.addScaleHandle([.5, 1], [0.5, 0])



        self.edge_roi_1.setZValue(10)  # make sure ROI is drawn above image
        plot.addItem(self.edge_roi_1)

        # Custom ROI for selecting an image region
        self.edge_roi_2 = pg.ROI([5, 800], [60, 100])
        self.edge_roi_2.setPen(pg.mkPen((0,200,0), width=3))
        self.edge_roi_2.addScaleHandle([0, 1], [1, 0])
        self.edge_roi_2.addScaleHandle([1, 0], [0, 1])

        self.edge_roi_2.addScaleHandle([0, 0], [1, 1])
        self.edge_roi_2.addScaleHandle([1, 1], [0, 0])

        self.edge_roi_2.addScaleHandle([0, .5], [1, .5])
        self.edge_roi_2.addScaleHandle([1, .5], [0, .5])

        self.edge_roi_2.addScaleHandle([.5, 0], [0.5, 1])
        self.edge_roi_2.addScaleHandle([.5, 1], [0.5, 0])

        self.edge_roi_2.setZValue(10)  # make sure ROI is drawn above image
        plot.addItem(self.edge_roi_2)


    def closeEvent(self, QCloseEvent, *event):
        self.panelClosedSignal.emit()
        

    def keyPressEvent(self, e):
        event = None
        if e.key() == Qt.Key_Up:
            event = 'up'
        if e.key() == Qt.Key_Down:
            event = 'down'
        if event is not None:
            self.up_down_signal.emit(event)
        else:
            super().keyPressEvent(e)

    

    def style_widgets(self):
        
        self.setStyleSheet("""
            #scope_waveform_widget FlatButton {
                min-width: 70;
                max-width: 70;
            }
            #scope_waveform_widget QLabel {
                min-width: 110;
                max-width: 110;
            }
            #controls_sidebar QLineEdit {
                min-width: 120;
                max-width: 120;
            }
            #controls_sidebar QLabel {
                min-width: 110;
                max-width: 110;
            }
            
        """)

        
        button_height = 48
        button_width = 48

        icon_size = QtCore.QSize(36, 36)
        self.edge_000_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, '000.png')))
        self.edge_000_btn.setIconSize(icon_size)
        self.edge_000_btn.setMinimumHeight(button_height)
        self.edge_000_btn.setMaximumHeight(button_height)
        self.edge_000_btn.setMinimumWidth(button_width)
        self.edge_000_btn.setMaximumWidth(button_width)

        icon_size = QtCore.QSize(36, 36)
        self.edge_001_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, '001.png')))
        self.edge_001_btn.setIconSize(icon_size)
        self.edge_001_btn.setMinimumHeight(button_height)
        self.edge_001_btn.setMaximumHeight(button_height)
        self.edge_001_btn.setMinimumWidth(button_width)
        self.edge_001_btn.setMaximumWidth(button_width)

        icon_size = QtCore.QSize(36, 36)
        self.edge_100_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, '100.png')))
        self.edge_100_btn.setIconSize(icon_size)
        self.edge_100_btn.setMinimumHeight(button_height)
        self.edge_100_btn.setMaximumHeight(button_height)
        self.edge_100_btn.setMinimumWidth(button_width)
        self.edge_100_btn.setMaximumWidth(button_width)

        icon_size = QtCore.QSize(36, 36)
        self.edge_101_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, '101.png')))
        self.edge_101_btn.setIconSize(icon_size)
        self.edge_101_btn.setMinimumHeight(button_height)
        self.edge_101_btn.setMaximumHeight(button_height)
        self.edge_101_btn.setMinimumWidth(button_width)
        self.edge_101_btn.setMaximumWidth(button_width)

        icon_size = QtCore.QSize(36, 36)
        self.edge_010_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, '010.png')))
        self.edge_010_btn.setIconSize(icon_size)
        self.edge_010_btn.setMinimumHeight(button_height)
        self.edge_010_btn.setMaximumHeight(button_height)
        self.edge_010_btn.setMinimumWidth(button_width)
        self.edge_010_btn.setMaximumWidth(button_width)
 
 
    def create_menu(self):

        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 793, 22))
        
        self.file_save_hdf5_act = QtWidgets.QAction('Save to HDF5', self)    
        self.actionSave_next = QtWidgets.QAction("Save", self)
        self.actionSave_As = QtWidgets.QAction("Save as...", self)
        self.actionPreferences = QtWidgets.QAction("Preferences", self)
        self.actionBG = QtWidgets.QAction("Overlay", self)
        self.actionBGclose = QtWidgets.QAction("Close overlay", self)
        self.actionCursors = QtWidgets.QAction("Phase", self)
        
        
        self.ActionRecallSetup = QtWidgets.QAction('Recall setup', self)        
        self.ActionSaveSetup = QtWidgets.QAction('Save setup', self)   
        self.ActionSetUserWaveform = QtWidgets.QAction('Edit user waveform', self)   
        self.setMenuBar(self.menuBar)

    def preferences_module(self):
        self.preferences_signal.emit()

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()  


