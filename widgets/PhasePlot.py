########### taken from DIOPTAS:

from PyQt5.QtGui import QColor, QPen
import pyqtgraph as pg
from utilities.HelperModule import calculate_color
from pyqtgraph import QtCore, mkPen, mkColor, hsvColor

class PhasePlot(object):
    num_phases = 0

    def __init__(self, plot_item, legend_item, positions, intensities, name=None, baseline=1, line_style='solid', default_visible=True,color=None,line_width=0.9):
        self.plot_item = plot_item
        self.legend_item = legend_item
        self.visible = True
        self.line_items = []
        self.line_visible = []
        self.pattern_x_range = []
        self.index = PhasePlot.num_phases
        if color == None:
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

    def create_items(self, positions, intensities, name=None, baseline=1):
        # create new ones on each Position:
        self.line_items = []
        list_baseline = isinstance(baseline, list)
        for ind, position in enumerate(positions):
            if list_baseline:
                baseline_i=baseline[ind]
            else: baseline_i=baseline

            self.line_items.append(pg.PlotDataItem(x=[position, position],
                                                   y=[baseline_i, intensities[ind]],
                                                   pen=self.pen, 
                                                   antialias=False))
            if self.default_visible:
                self.plot_item.addItem(self.line_items[ind])
            self.line_visible.append(self.default_visible )

        if name is not None:
            try:
                self.legend_item.addItem(self.ref_legend_line, name)
                self.name = name
            except IndexError:
                pass

    def add_line(self):
        
        self.line_items.append(pg.PlotDataItem(x=[0, 0],
                                               y=[1, 1],
                                               pen=self.pen, antialias=False))
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
            
    def update_visibilities(self, pattern_range):
        if self.visible:
            for ind, line_item in enumerate(self.line_items):
                data = line_item.getData()
                position = data[0][0]
                if position >= pattern_range[0] and position <= pattern_range[1]:
                    if not self.line_visible[ind]:
                        self.plot_item.addItem(line_item)
                        self.line_visible[ind] = True
                else:
                    if self.line_visible[ind]:
                        self.plot_item.removeItem(line_item)
                        self.line_visible[ind] = False

    def set_color(self, color):
        self.pen = pg.mkPen(color=color, width=self.width, style=self.line_style)
        for line_item in self.line_items:
            line_item.setPen(self.pen)
        self.ref_legend_line.setPen(self.pen)

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