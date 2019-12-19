########### taken from DIOPTAS:

from PyQt5.QtGui import QColor, QPen
import pyqtgraph as pg
from utilities.HelperModule import calculate_color
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor

class PhasePlot(object):
    num_phases = 0

    def __init__(self, plot_item, legend_item, positions, intensities, name=None, baseline=1, line_style='solid', default_visible=True,color=None,line_width=0.9, ind = 0):
        self.plot_item = plot_item
        self.legend_item = legend_item
        self.visible = True
        self.line_items = []
        self.legend_items = []
        self.legend_points = []
        self.line_visible = []
        self.pattern_x_range = []
        self.index = ind
        if color is None:
            self.color = calculate_color(self.index + 9)
            PhasePlot.num_phases += 1
        else:
            self.color=color

        self.width = line_width
        self.set_line_style(line_style)
        self.ref_legend_line = pg.PlotDataItem(pen=self.pen)
        self.name = ''
        
        self.default_visible = default_visible
        self.create_items(positions, intensities, name, baseline)
        

    def set_line_style(self, style):
        # takes style input as 'solid' or 'dashed'
        if style == 'dash':
            self.line_style = QtCore.Qt.DashLine
        elif style == 'solid':   
            self.line_style = QtCore.Qt.SolidLine
        self.pen = pg.mkPen(color=self.color, width=self.width, style=self.line_style)     

    def make_pen(self, ind):
        if ind > 1:
                wd = 2
        else: 
            wd = 4
        oe = ind % 2
        if oe == 0:
            st=QtCore.Qt.SolidLine 
        else:
            st=QtCore.Qt.DashLine 
        pen_str = {'color': self.color, 'width': wd, 'style':st}
        l_pen =   pg.mkPen(pen_str)    
        return l_pen

    def make_label(self, ind):
        if ind > 1:
            pref = u'2'
        else: 
            pref = u''
        oe = ind % 2
        if oe == 0:
            mode = u'<sub>P</sub>'
        else:
            
            mode = u'<sub>S</sub>'

        label = pref + u'R' + mode+str(self.index)
        return label

    def create_items(self, positions, intensities, name=None, baseline=1):
        # create new ones on each Position:
        self.line_items = []
        list_baseline = isinstance(baseline, list)
        for ind, position in enumerate(positions):
            if list_baseline:
                baseline_i=baseline[ind]
            else: baseline_i=baseline
            
            l_pen =   self.make_pen(ind)  
            

            self.line_items.append(pg.PlotDataItem(x=[position, position],
                                                   y=[baseline_i, intensities[ind]],
                                                   pen=l_pen, 
                                                   antialias=False))
              
            curvePoint = pg.CurvePoint(self.line_items[ind]) 
            curvePoint.setPos(1)
            
            lbl = pg.TextItem('', anchor=(0.5, 1.0))
            lbl.setColor(self.color)
            lbl.setHtml(self.make_label(ind))
           
            lbl.setParentItem(curvePoint)
            self.legend_items.append(lbl)

            self.legend_points.append(curvePoint)

            if self.default_visible:
                self.plot_item.addItem(self.line_items[ind])
                self.plot_item.addItem(curvePoint)



            self.line_visible.append(self.default_visible )
        #print(self.legend_items)

        if name is not None:
            try:
                self.legend_item.addItem(self.ref_legend_line, name)
                self.name = name
            except IndexError:
                pass

    def add_line(self):
        new_ind = len(self.line_items)
        new_pen = self.make_pen(new_ind)
        self.line_items.append(pg.PlotDataItem(x=[0, 0],
                                               y=[1, 1],
                                               pen=new_pen, antialias=False))
        self.line_visible.append(True)
        self.plot_item.blockSignals(True)
        
        self.plot_item.addItem(self.line_items[-1])
        self.plot_item.blockSignals(False)

    def remove_line(self, ind=-1):
        self.plot_item.removeItem(self.line_items[ind])
        del self.line_items[ind]
        del self.line_visible[ind]

    def clear_lines(self):
        for dummy_ind in range(len(self.line_items)):
            self.remove_line()

    def update_intensities(self, positions, intensities, baseline=1):
        if self.visible:
            list_baseline = isinstance(baseline, list)
            for ind, intensity in enumerate(intensities):
                if list_baseline:
                    baseline_i=baseline[ind]
                else: baseline_i=baseline
                self.line_items[ind].setData(y=[baseline_i, intensity],
                                            x=[positions[ind], positions[ind]])
                self.legend_points[ind] = pg.CurvePoint(self.line_items[ind]) 
                self.legend_points[ind].setPos(1)
                self.legend_items[ind].setParentItem(self.legend_points[ind])
            
    def update_visibilities(self, pattern_range):
        if self.visible:
            for ind, line_item in enumerate(self.line_items):
                data = line_item.getData()
                position = data[0][0]
                legend_item = self.legend_items[ind]
                if position >= pattern_range[0] and position <= pattern_range[1]:
                    if not self.line_visible[ind]:
                        self.plot_item.addItem(line_item)
                        self.plot_item.addItem(legend_item)
                        self.line_visible[ind] = True
                        self.legend_points[ind] = pg.CurvePoint(line_item) 
                        self.legend_points[ind].setPos(1)
                        legend_item.setParentItem(self.legend_points[ind])
                else:
                    if self.line_visible[ind]:
                        self.plot_item.removeItem(line_item)
                        self.plot_item.removeItem(legend_item)
                        self.line_visible[ind] = False

    def set_color(self, color):
        self.color = color
        self.pen = pg.mkPen(color=color, width=self.width, style=self.line_style)
        self.ref_legend_line.setPen(self.pen)
        
        for ind, line_item in enumerate(self.line_items):
            ind = self.line_items.index(line_item)
            pen = self.make_pen(ind)

            line_item.setPen(pen)
            self.legend_items[ind].setColor(self.color)
        

    def hide(self):
        if self.visible:
            self.visible = False
            for ind, line_item in enumerate(self.line_items):
                if self.line_visible[ind]:
                    self.plot_item.removeItem(line_item)

    def show(self):
        if not self.visible:
            self.visible = True
            for ind, line_item in enumerate(self.line_items):
                if self.line_visible[ind]:
                    self.plot_item.addItem(line_item)

    def remove(self):
        try:
            self.legend_item.removeItem(self.ref_legend_line)
        except IndexError:
            pass
            #print('this phase had no lines in the appropriate region')
        for ind, item in enumerate(self.line_items):
            if self.line_visible[ind]:
                self.plot_item.removeItem(item)

####### ^^^ taken from DIOPTAS