import pyqtgraph as pg
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor, ViewBox
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QPoint
from PyQt5.QtGui import QColor, QPen
from  PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QApplication, QInputDialog, QWidget, QLabel
from um.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight
from utilities.HelperModule import calculate_color, get_partial_index, get_partial_value
from um.widgets.ExLegendItem import LegendItem
from um.widgets.PhasePlot import PhasePlot

from numpy import argmax, nan, greater,less, append, sort, array
from PyQt5 import QtWidgets
import copy




class SimpleDisplayWidget(QtWidgets.QWidget):
    widget_closed = QtCore.pyqtSignal()
    fast_cursor_changed_singal = QtCore.pyqtSignal(float)
    cursor_changed_singal = QtCore.pyqtSignal(float)
    cursor_y_signal = QtCore.pyqtSignal(float)
    
    def __init__(self, fig_params):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0,0,0,0)
        self.fig = plotWindow(*fig_params)
        self._layout.addWidget(self.fig)
        self.cursor_fast = QLabel()
        self.cursor_fast.setFixedWidth(70)
        self.cursor = QLabel()
        self.cursor.setFixedWidth(70)
        self.cursor_widget = QWidget()
        self._cursor_widget_layout = QtWidgets.QHBoxLayout()
        self._cursor_widget_layout.setContentsMargins(0,0,0,0)
        self._cursor_widget_layout.addSpacerItem(HorizontalSpacerItem())
        self._cursor_widget_layout.addWidget(self.cursor_fast)
        self._cursor_widget_layout.addWidget(self.cursor)
        self._cursor_widget_layout.addSpacerItem(HorizontalSpacerItem())
        self.cursor_widget.setLayout(self._cursor_widget_layout)
        self._layout.addWidget(self.cursor_widget)
        self.button_widget = QtWidgets.QWidget()
        self._button_widget_layout = QtWidgets.QHBoxLayout()
        self._button_widget_layout.setContentsMargins(0,0,0,0)
        self.button_widget.setLayout(self._button_widget_layout)
        self._layout.addWidget(self.button_widget)
        self.setLayout(self._layout)
        self.create_connections()
        

    def add_button_widget_item(self, item):
        self._button_widget_layout.addWidget(item)
    
    def add_button_widget_spacer(self):
        self._button_widget_layout.addSpacerItem(HorizontalSpacerItem())

    def create_connections(self):
        self.fig.fast_cursor.connect(self.update_fast_cursor)
        self.fig.cursor.connect(self.update_cursor)
        self.fig.cursor_y_signal.connect(self.update_cursor_y)
   


    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.widget_closed.emit()

    def update_fast_cursor(self, pos):
        c = '%.3e' % (pos)
        self.cursor_fast.setText(c)
        self.fig.set_fast_cursor(pos)
        self.fast_cursor_changed_singal.emit(pos)

    def update_cursor(self, pos):
        c = "<span style='color: #00CC00'>%0.3e</span>"  % (pos)
     
        self.cursor.setText(c)
        self.fig.set_cursor(pos)
        self.cursor_changed_singal.emit(pos)

    def update_cursor_y(self, pos):
        '''c = "<span style='color: #00CC00'>%0.3e</span>"  % (pos)
        self.cursor.setText(c)
        self.fig.set_cursor(pos)'''
        self.cursor_y_signal.emit(pos)

    def setText(self, text, plot_ind):
        self.fig.set_plot_label(text,plot_ind)

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()

'''class SimpleDisplayWidget(customWidget):
    def __init__(self, fig_params):
        super().__init__(fig_params)
        #self.resize(800,200)'''''''''

class plotWindow(QtWidgets.QWidget):
    widget_closed = QtCore.pyqtSignal()

    def __init__(self, title, left_label, bottom_label):
        super().__init__()

        self._layout = QtWidgets.QVBoxLayout()  
        self._layout.setContentsMargins(0,0,0,0)
        self.setWindowTitle(title)
        self.win = PltWidget()
        self.win.setLogMode(False,False)
        #self.win.vLineFast.setObjectName(title+'vLineFast')
        self.win.setWindowTitle(title)
        self.win.setBackground(background=(0,0,0))
        
        self.win.setLabel('left',left_label)
        self.win.setLabel('bottom', bottom_label)
        
        self._layout.addWidget(self.win)
        self.setLayout(self._layout)
        #self.resize(600,400)
        self.plots = []
        self.fast_cursor = self.win.plotMouseMoveSignal
        self.cursor = self.win.viewBox.plotMouseCursorSignal
        self.cursor_y_signal = self.win.viewBox.cursor_y_signal
        self.win.create_graphics()
        self.win.legend.setParentItem(self.win.viewBox)
        self.win.legend.anchor(itemPos=(1, 0), parentPos=(1, 0), offset=(-10, -10))
        self.legend_items = []


    def set_plot_label(self, text, plot_ind):
        self.win.legend.renameItem(plot_ind, text)
    
    def set_plot_label_color(self, color, plot_ind):
        self.win.legend.setItemColor(plot_ind, color)

    def set_fast_cursor(self, pos):
        self.win.set_cursorFast_pos(pos)

    def set_cursor(self, pos):
        self.win.set_cursor_pos(pos)

    def create_plots(self):
        self.win.create_plots([],[],[],[],'Time (s)')
        self.win.set_colors({'data_color':'FFFF00','rois_color': '#00b4ff'})
        
  

    def add_line_plot(self, x=[],y=[],color = (0,0,0),Width = 1,title=""):
        Pen=mkPen(color, width=Width)
        Plot = self.win.plot(x,y, 
                        pen= Pen, 
                        antialias=True)
        self.plots.append(Plot)

        self.win.legend.addItem(self.plots[-1], '') # can display name in upper right corner in same color 
        return Plot
        
    def add_scatter_plot(self, x=[],y=[],color=(100, 100, 255),opacity=100,symbolSize=7):
        sb = (color[0], color[1],color[2],opacity)
        Plot = self.win.plot(x,y, 
                                pen=None, symbol='o', \
                                symbolPen=None, symbolSize=symbolSize, \
                                symbolBrush=sb)
        self.plots.append(Plot)
         # can display name in upper right corner in same color 
        self.win.legend.addItem(self.plots[-1], '')
        return Plot
            

    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.widget_closed.emit()

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()




class myLegendItem(LegendItem):
    def __init__(self, size=None, offset=None, horSpacing=25, verSpacing=0, box=True, labelAlignment='center', showLines=True):
        super().__init__(size=size, offset=offset, horSpacing=horSpacing, verSpacing=verSpacing, box=box, labelAlignment=labelAlignment, showLines=showLines)

    def my_hoverEvent(self, ev):
        pass

    def mouseDragEvent(self, ev):
        pass

class myVLine(pg.InfiniteLine):
    def __init__(self, pos=None, angle=90, pen=None, movable=False, bounds=None,
                 hoverPen=None, label=None, labelOpts=None, span=(0, 1), markers=None, 
                 name=None):
        super().__init__(pos=pos, angle=angle, pen=pen, movable=movable, bounds=bounds,
                 hoverPen=hoverPen, label=label, labelOpts=labelOpts,  
                 name=name)

class CustomViewBox(pg.ViewBox):  
    plotMouseCursorSignal = pyqtSignal(float)
    plotMouseCursor2Signal = pyqtSignal(float)  
    cursor_y_signal = pyqtSignal(float)
    def __init__(self, *args, **kwds):
        super().__init__()
        
        self.cursor_signals = [self.plotMouseCursorSignal, self.plotMouseCursor2Signal]
        self.vLine = myVLine(movable=False, pen=pg.mkPen(color=(0, 255, 0), width=2 , style=QtCore.Qt.DashLine))
        
        #self.vLine.sigPositionChanged.connect(self.cursor_dragged)
        self.vLineFast = myVLine(movable=False,pen=mkPen({'color': '808080', 'width': 2, 'style':QtCore.Qt.DashLine}))
        self.cursors = [self.vLine, self.vLineFast]
        self.setMouseMode(self.RectMode)
        self.addItem(self.vLine, ignoreBounds=True)
        self.addItem(self.vLineFast, ignoreBounds=True)
        self.enableAutoRange(self.XYAxes, enable = True)
        self.cursorPoint = 0
        self.cursorPoint_y = 0
        # Enable dragging and dropping onto the GUI 
        self.setAcceptDrops(True) 
        
        

    '''
    def cursor_dragged(self, cursor):
        ind = self.cursors.index(cursor)
        pos = cursor.getXPos()
        
        sig = self.cursor_signals[ind]
        sig.emit(pos)    
    '''

    ## reimplement right-click to zoom out
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            #self.enableAutoRange(self.XYAxes, True)    
            
            self.enableAutoRange(enable=1) 
            
        elif ev.button() == QtCore.Qt.LeftButton: 
            pos = ev.pos()  ## using signal proxy turns original arguments into a tuple
            mousePoint = self.mapToView(pos)
            x = mousePoint.x()
            y = mousePoint.y()
            self.cursorPoint=x
            self.cursorPoint_y = y
            self.plotMouseCursorSignal.emit(x)   
            self.cursor_y_signal.emit(y) 
        ev.accept()
            

class PltWidget(pg.PlotWidget):

    """
    Subclass of PlotWidget
    """
    plotMouseMoveSignal = pyqtSignal(float)  
    range_changed = QtCore.Signal(list)
    auto_range_status_changed = QtCore.Signal(bool)

    def __init__(self, parent=None, colors = None):
        """
        Constructor of the widget
        """
        #app = pg.mkQApp()
        vb = CustomViewBox()  
        
        super().__init__(parent, viewBox=vb)
        self.viewBox = self.getViewBox() # Get the ViewBox of the widget
        
       
        self.cursorPoints = [nan,nan]
        # defined default colors
        self.colors = { 'plot_background_color': '#ffffff',\
                        'data_color': '#2f2f2f',\
                        'rois_color': '#00b4ff', \
                        'roi_cursor_color': '#969600', \
                        'xrf_lines_color': '#969600', \
                        'mouse_cursor_color': '#00cc00', \
                        'mouse_fast_cursor_color': '#323232'}

        # override default colors here:
        if colors != None:
            for c in colors:
                if c in self.colors:
                    self.colors[c] = colors[c]
            
        plot_background_color = self.colors['plot_background_color']
        self.setBackground(background=plot_background_color)
        
        #mouse_fast_cursor_color = self.colors['mouse_fast_cursor_color']

        self.vLine = self.viewBox.vLine
        self.vLineFast  = self.viewBox.vLineFast
        #self.vLine.setPos(0)
        #self.vLineFast.setPos(0)

        self.selectionMode = False # Selection mode used to mark histo data
        
        self.viewBox.setMouseMode(self.viewBox.RectMode) # Set mouse mode to rect for convenient zooming
        self.setMenuEnabled(enableMenu=False)
        # cursor
        
        
        self.proxy = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=60, slot=self.fastCursorMove)
        # self.getViewBox().addItem(self.hLine, ignoreBounds=True)
        self.create_graphics()
        self.pattern_plot = self.plotItem
        self.phases = []
        self.xrf = []
        self.roi_cursor = []
        #self.phases_vlines = []
        self.overlays = []
        self.overlay_names = []
        self.overlay_show = []
        #initialize data plots object names
        self._auto_range = True
        self.plotForeground = None
        self.plotRoi = None
        self.showGrid(x=True, y=True)
        
        self.set_log_mode(False,True)
        self.xAxis = None
        self.yData = None

        
    def set_cursorFast_pos(self, pos):
        self.vLineFast.blockSignals(True)
        self.vLineFast.setPos(pos)
        self.cursorPoints[1] = pos
        self.vLineFast.blockSignals(False)

    def set_cursor_pos(self, pos):
        self.vLine.blockSignals(True)
        self.vLine.setPos(pos)
        self.cursorPoints[0] = pos
        self.vLine.blockSignals(False)

    def get_cursor_pos(self):
        return self.cursorPoints[0]

    def get_cursorFast_pos(self):
        return self.cursorPoints[1]

    def set_log_mode(self, x, y):
        self.LM = (x,y)
        self.setLogMode(*self.LM)
        
    def set_colors(self, params):

        self.colors = copy.deepcopy(params)
   
        for p in params:
            color = params[p]
            self.colors[p] = color
            if p == 'plot_background_color':
                self.setBackground(color)
            elif p == 'data_color':
                if self.plotForeground is not None:
                    self.plotForeground.setPen(color)
                    self.legend.setItemColor(0, color)
            elif p == 'rois_color':
                if self.plotRoi is not None:
                    self.plotRoi.setPen(color)
                    self.legend.setItemColor(1, color)
            elif p == 'roi_cursor_color':
                if len(self.roi_cursor):
                    self.set_roi_cursor_color(0, params[p])
            elif p == 'xrf_lines_color':
                pass
            elif p == 'mouse_cursor_color':
                pass
            elif p == 'mouse_fast_cursor_color':
                pass
            

    def export_plot_png(self,filename):
        exporter = pg.exporters.ImageExporter(self.plotItem)
        #exporter.parameters()['width']= 200
        exporter.export(filename)
    
    def export_plot_svg(self,filename):
        exporter = pg.exporters.SVGExporter(self.plotItem)
        #exporter.parameters()['width']= 200
        exporter.export(filename)

    def emit_sig_range_changed(self):
        pass

    def create_plots(self, xAxis,data,roiHorz,roiData, xLabel):
        # initialize some plots
        #self.setLabel('left', 'Amplitude')
        data_color = self.colors['data_color']
        self.plotForeground = pg.PlotDataItem(xAxis, data, title="",
                antialias=True, pen=pg.mkPen(color=data_color, width=1), connect="finite" )
        self.addItem(self.plotForeground)
        # plot legend items 
        self.legend.addItem(self.plotForeground, '') # can display name in upper right corner in same color 
        self.legend.setParentItem(self.viewBox)
        self.legend.anchor(itemPos=(0, 0), parentPos=(0, 0), offset=(0, 00))
        self.phases_legend.setParentItem(self.viewBox)
        self.phases_legend.anchor(itemPos=(0, 0), parentPos=(0, 0), offset=(0, -10))
        self.xrf_legend.setParentItem(self.viewBox)
        self.xrf_legend.anchor(itemPos=(0.5, 0), parentPos=(0.5, 0), offset=(0, -10))
        #self.roi_cursor_legend.setParentItem(self.viewBox)
        #self.roi_cursor_legend.anchor(itemPos=(0, 0), parentPos=(0, 0), offset=(0, 30))
        # initialize roi plot 
        rois_color = self.colors['rois_color']
        self.plotRoi = pg.PlotDataItem(roiHorz, roiData, 
            antialias=True, pen=rois_color, connect="finite", width=2)
        self.addItem(self.plotRoi)  
        self.legend.addItem(self.plotRoi, '')
        self.setLabel('bottom', xLabel) 

    def plotData(self, xAxis,data,roiHorz=[],roiData=[], xLabel='', dataLabel=''):
        if len(xAxis)==len(data):
            self.xAxis = xAxis
            self.yData = data
            if self.plotForeground == None:
                self.create_plots(xAxis,data,roiHorz,roiData, xLabel)
            else:
                self.plotForeground.setData(xAxis, data) 
                self.plotRoi.setData(roiHorz, roiData) 
            # if nonzero ROI data, show ROI legend on plot
            if len(roiHorz) > 0: roiLabel = 'ROIs'
            else:   roiLabel = ''
            self.legend.renameItem(0, dataLabel)
            self.legend.renameItem(1, roiLabel)
            self.setLabel('bottom', xLabel)     
        else:
            print('x and y arrays not the same length')

    def lin_reg_mode(self, mode,**kwargs):
        if mode == 'Add':
            width = kwargs.get('width', None)
            if width is None:
                width = 0.6
            self.lr = pg.LinearRegionItem([self.viewBox.cursorPoint-width/2,self.viewBox.cursorPoint+width/2])
            self.lr.setZValue(-10)
            self.addItem(self.lr)
        if mode == 'Set':
            reg = self.lr.getRegion()
            #print(str(reg))
            self.removeItem(self.lr)
            return reg

    def setPlotMouseMode(self, mode):
        vb = self.getViewBox()
        if mode==0:
            mMode = pg.ViewBox.RectMode
        else:
            mMode = pg.ViewBox.PanMode
        vb.setMouseMode(mMode)
        
    def fastCursorMove(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.sceneBoundingRect().contains(pos):
            mousePoint = self.getViewBox().mapSceneToView(pos)
            index = mousePoint.x()
            self.plotMouseMoveSignal.emit(index)
            
           # self.hLine.setPos(mousePoint.y())
    

    ########### taken from DIOPTAS:

    def create_graphics(self):
        self.legend = LegendItem(horSpacing=20, box=False, verSpacing=-3, labelAlignment='right', showLines=False)
        self.phases_legend = LegendItem(horSpacing=20, box=False, verSpacing=-3, labelAlignment='left', showLines=False)
        self.xrf_legend = LegendItem(horSpacing=20, box=False, verSpacing=-3, labelAlignment='left', showLines=False)
        #self.roi_cursor_legend = LegendItem(horSpacing=20, box=False, verSpacing=-3, labelAlignment='right', showLines=False)

    #### control roi_cursor #### 

    def add_roi_cursor(self, name, positions, intensities, baseline):
        self.roi_cursor.append(PhasePlot(self.pattern_plot, \
                    self.xrf_legend, positions, intensities, \
                    name, baseline,'solid',line_width=2,color=(255,0,0)))
        return self.roi_cursor[-1].color

    def set_roi_cursor_color(self, ind, color):
        self.roi_cursor[ind].set_color(color)
        self.xrf_legend.setItemColor(ind, color)

    def hide_roi_cursor(self, ind):
        self.roi_cursor[ind].hide()
        self.xrf_legend.hideItem(ind)

    def show_roi_cursor(self, ind):
        self.roi_cursor[ind].show()
        self.xrf_legend.showItem(ind)

    def rename_roi_cursor(self, ind, name):
        self.xrf_legend.renameItem(ind, name)

    def update_roi_cursor_intensities(self, ind, positions, intensities, baseline):
        if len(self.roi_cursor):
            self.roi_cursor[ind].update_intensities(positions, \
                    intensities, baseline)

    def update_roi_cursor_line_visibility(self, ind):
        x_range = self.plotForeground.dataBounds(0)
        self.roi_cursor[ind].update_visibilities(x_range)

    def update_roi_cursor_line_visibilities(self):
        x_range = self.plotForeground.dataBounds(0)
        for roi_cursor in self.roi_cursor:
            roi_cursor.update_visibilities(x_range)

    def del_roi_cursor(self, ind):
        self.roi_cursor[ind].remove()
        del self.roi_cursor[ind]

    #### END control roi_cursor ####

 
    ###################  OVERLAY STUFF  ################### from DIOPTAS
    def update_graph_range(self):
        pass

    def add_overlay(self, pattern, show=True):
        [x,y]=pattern.get_pattern()
        
        color = calculate_color(len(self.overlays) + 1)
        self.overlays.append(pg.PlotDataItem(pen=pg.mkPen(color=color, width=1), \
                    antialias=True, conntect='finite'))
        #self.overlays.append(pg.PlotDataItem(x, y, pen=pg.mkPen(color=color, width=1), antialias=True, conntect='finite'))
        if x is not None:
            self.overlays[-1].setData(x, y)
        self.overlay_names.append(pattern.name)
        self.overlay_show.append(True)
        if show:
            self.pattern_plot.addItem(self.overlays[-1])
            self.legend.addItem(self.overlays[-1], pattern.name)
            self.update_graph_range()
        return color

    def remove_overlay(self, ind):
        self.pattern_plot.removeItem(self.overlays[ind])
        self.legend.removeItem(self.overlays[ind])
        self.overlays.remove(self.overlays[ind])
        self.overlay_names.remove(self.overlay_names[ind])
        self.overlay_show.remove(self.overlay_show[ind])
        self.update_graph_range()

    def hide_overlay(self, ind):
        self.pattern_plot.removeItem(self.overlays[ind])
        self.legend.hideItem(ind + 2)
        self.overlay_show[ind] = False
        self.update_graph_range()

    def show_overlay(self, ind):
        self.pattern_plot.addItem(self.overlays[ind])
        self.legend.showItem(ind + 2)
        self.overlay_show[ind] = True
        self.update_graph_range()

    def update_overlay(self, pattern, ind):
        [x, y] = pattern.get_pattern()
        if x is not None:
            self.overlays[ind].setData(x, y)
        else:
            self.overlays[ind].setData([], [])
        self.update_graph_range()

    def set_overlay_color(self, ind, color):
        self.overlays[ind].setPen(pg.mkPen(color=color, width=1))
        self.legend.setItemColor(ind + 2, color)

    def rename_overlay(self, ind, name):
        self.legend.renameItem(ind + 2, name)

    def move_overlay_up(self, ind):
        new_ind = ind - 1
        self.overlays.insert(new_ind, self.overlays.pop(ind))
        self.overlay_names.insert(new_ind, self.overlay_names.pop(ind))
        self.overlay_show.insert(new_ind, self.overlay_show.pop(ind))

        color = self.legend.legendItems[ind + 2][1].opts['color']
        label = self.legend.legendItems[ind + 2][1].text
        self.legend.legendItems[ind + 2][1].setAttr('color', self.legend.legendItems[new_ind + 2][1].opts['color'])
        self.legend.legendItems[ind + 2][1].setText(self.legend.legendItems[new_ind + 2][1].text)
        self.legend.legendItems[new_ind + 2][1].setAttr('color', color)
        self.legend.legendItems[new_ind + 2][1].setText(label)

    def move_overlay_down(self, cur_ind):
        self.overlays.insert(cur_ind + 2, self.overlays.pop(cur_ind))
        self.overlay_names.insert(cur_ind + 2, self.overlay_names.pop(cur_ind))
        self.overlay_show.insert(cur_ind + 2, self.overlay_show.pop(cur_ind))

        color = self.legend.legendItems[cur_ind + 2][1].opts['color']
        label = self.legend.legendItems[cur_ind + 2][1].text
        self.legend.legendItems[cur_ind + 2][1].setAttr('color', self.legend.legendItems[cur_ind + 3][1].opts['color'])
        self.legend.legendItems[cur_ind + 2][1].setText(self.legend.legendItems[cur_ind + 3][1].text)
        self.legend.legendItems[cur_ind + 3][1].setAttr('color', color)
        self.legend.legendItems[cur_ind + 3][1].setText(label)

    ##########  END OF OVERLAY STUFF  ##################


    #### control phases #### 

    def add_phase(self, name, positions, intensities, baseline, color):
        i = len(self.phases)
        self.phases.append(PhasePlot(self.pattern_plot, \
                        self.phases_legend, positions, intensities, \
                        name, baseline, line_width=2,color=color,ind=i))
        

    def set_phase_color(self, ind, color):
        self.phases[ind].set_color(color)
        self.phases_legend.setItemColor(ind, color)

    def hide_phase(self, ind):
        self.phases[ind].hide()
        self.phases_legend.hideItem(ind)

    def show_phase(self, ind):
        self.phases[ind].show()
        self.phases_legend.showItem(ind)

    def rename_phase(self, ind, name):
        self.phases_legend.renameItem(ind, name)

    def update_phase_intensities(self, ind, positions, intensities, baseline=.5):
        if len(self.phases):
            self.phases[ind].update_intensities(positions, intensities, baseline)

    def update_phase_line_visibility(self, ind):

        if self.xAxis is not None:
            x_range = [min(self.xAxis), max(self.xAxis)]
        else:
            x_range = [0,10e-6]
        
        
        self.phases[ind].update_visibilities(x_range)

    def update_phase_line_visibilities(self):
        if self.xAxis is not None:
            x_range = [min(self.xAxis), max(self.xAxis)]
        else:
            x_range = [0,10e-6]
        for phase in self.phases:
            phase.update_visibilities(x_range)

    def del_phase(self, ind):
        self.phases[ind].remove()
        del self.phases[ind]

    #### END control phases ####
