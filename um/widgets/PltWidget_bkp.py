'''class plotWindow_adv(QtWidgets.QWidget):
    widget_closed = QtCore.pyqtSignal()

    def __init__(self, title='', left_label='', bottom_label=''):
        super().__init__()

        self._layout = QtWidgets.QVBoxLayout()  
        self._layout.setContentsMargins(0,0,0,0)
        self.setWindowTitle(title)
        self.win = PltWidget()
        self.win.setLogMode(False,False)
        #self.win.vLineFast.setObjectName(title+'vLineFast')
        self.win.setWindowTitle(title)
        self.win.setBackground(background=(20,20,20))
        
        self.win.setLabel('left',left_label)
        self.win.setLabel('bottom', bottom_label)
        
        self._layout.addWidget(self.win)
        self.setLayout(self._layout)
        #self.resize(600,400)
        self.plots = []
        self.cursor2 = self.win.viewBox.plotMouseCursor2Signal
        self.cursor1 = self.win.viewBox.plotMouseCursorSignal

    
        self.points_minima1 = self.add_scatter_plot(color=(0, 225, 0),opacity=150, symbolSize=12)
        self.points_maxima1 = self.add_scatter_plot(color=(0, 225, 0),opacity=150, symbolSize=12)

        self.points_minima2 = self.add_scatter_plot(color=(225, 0, 0),opacity=150, symbolSize=12)
        self.points_maxima2 = self.add_scatter_plot(color=(225, 0, 0),opacity=150, symbolSize=12)

        self.point_cursor1 = self.add_scatter_plot(color=(0, 225, 0),opacity=150, symbolSize=12)
        self.point_cursor2 = self.add_scatter_plot(color=(225, 0, 0),opacity=150, symbolSize=12)

        self.optimum_type1=None
        self.optimum_type2=None

        self.win.create_graphics()
        self.win.legend.setParentItem(self.win.viewBox)
        self.win.legend.anchor(itemPos=(1, 0), parentPos=(1, 0), offset=(-10, -10))
        self.legend_items = []

    def set_plot_label(self, text, plot_ind):
        self.win.legend.renameItem(plot_ind, text)
    
    def set_plot_label_color(self, color, plot_ind):
        self.win.legend.setItemColor(plot_ind, color)



    def set_optima(self, optimum = None,optimum_type=None):
        
        if optimum is not None:
            self.points_minima1.setData(*optimum)
        self.optimum_type1=optimum_type

    def set_optima2(self, optimum = None,optimum_type=None):
        
        if optimum is not None:
            self.points_minima2.setData(*optimum)
        self.optimum_type2=optimum_type
        

    def set_cursor(self, pos, val=None):
        self.win.viewBox.set_vLine_pos(pos)
        if val is not None:
            self.point_cursor1.setData([pos],[val])

    def set_cursor2(self, pos, val=None):
        self.win.viewBox.set_vLine2_pos(pos)
        if val is not None:
            self.point_cursor2.setData([pos],[val])

    def get_cursor_pos(self):
        return self.win.viewBox.cursorPoints[0]

    def get_cursor2_pos(self):
        return self.win.viewBox.cursorPoints[1]
        
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

    def clear(self):
        n = len(self.plots)
        for i in range(n):
            self.win.legend.removeItem(self.plots[-1])
            self.win.removeItem(self.plots[-1])
            self.plots.remove(self.plots[-1])
        
    def setPlotMouseMode(self, mode):
        if mode:
            mode = ViewBox.RectMode
        else:
            mode = ViewBox.PanMode
        self.win.viewBox.setMouseMode(mode)        

    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.widget_closed.emit()

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()
        '''

        
'''
class customWidget_adv(QtWidgets.QWidget):
    widget_closed = QtCore.pyqtSignal()
    def __init__(self, fig_params):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0,0,0,0)
        self.fig = plotWindow(*fig_params)
        self._layout.addWidget(self.fig)
        self.cursor_fast = QLabel()
        self.cursor_fast.setFixedWidth(140)
        self.cursor = QLabel()
        self.cursor.setFixedWidth(140)
        self.delta = QLabel()
        self.delta.setFixedWidth(140)
        self.add_cursor_widget()
        self.add_button_widget()
        
        self.setLayout(self._layout)

    def add_cursor_widget(self):
        self.cursor_widget = QWidget()
        self._cursor_widget_layout = QtWidgets.QHBoxLayout()
        self._cursor_widget_layout.setContentsMargins(0,0,0,0)
        self._cursor_widget_layout.addSpacerItem(HorizontalSpacerItem())
        self._cursor_widget_layout.addWidget(self.cursor_fast)
        self._cursor_widget_layout.addWidget(self.cursor)
        self._cursor_widget_layout.addWidget(self.delta)
        self._cursor_widget_layout.addSpacerItem(HorizontalSpacerItem())
        self.cursor_widget.setLayout(self._cursor_widget_layout)
        self._layout.addWidget(self.cursor_widget)
        
    def add_button_widget(self):
        self.button_widget = QtWidgets.QWidget()
        self._button_widget_layout = QtWidgets.QHBoxLayout()
        self._button_widget_layout.setContentsMargins(0,0,0,0)
        self.button_widget.setLayout(self._button_widget_layout)
        self._layout.addWidget(self.button_widget)

    def add_button_widget_item(self, item):
        
        self._button_widget_layout.addWidget(item)
    
    def add_button_widget_spacer(self):
        self._button_widget_layout.addSpacerItem(HorizontalSpacerItem())
    

    def enable_cursors(self):
        self.fig.cursor2.connect(self.update_cursor2)
        self.fig.cursor1.connect(self.update_cursor)
        

    def raise_widget(self):
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()
        self.show()

    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.widget_closed.emit()

    def get_data_value(self, x,optima_type=None):
        
        #xData = self.fig.plots[6].xData
        #pind = get_partial_index(xData,x)
        #yData = self.fig.plots[6].yData
        #pvalue = get_partial_value(yData, pind)
        
        pvalue = nan
        ans = self.get_local_optimum(x,optima_type)
        return ans

    def index_of_nearest(self, values, value):
        items = []
        for ind, v in enumerate(values):
            diff = abs(v-value)
            item = (diff, v, ind)
            items.append(item)
        def getKey(item):
            return item[0]
        s = sorted(items, key=getKey)
        closest = s[0][1]
        closest_ind = s[0][2]
        return closest_ind

    def get_local_optimum(self,x, optima_type=None):
        

        xData = self.fig.plots[0].xData
        if len(xData):
            pind = get_partial_index(xData,x)
            if pind is None:
                return None
            pind1 = int(pind-50)
            pind2 = int(pind +50)
            xr = xData[pind1:pind2]
            yData = self.fig.plots[6].yData
            yr = yData[pind1:pind2]
            # for local maxima
            maxima_ind = argrelextrema(yr, greater)
            maxima_x = xr[maxima_ind]
            maxima_y = yr[maxima_ind]

            minima_ind = argrelextrema(yr, less)
            minima_x = xr[minima_ind]
            minima_y = yr[minima_ind]

            if optima_type == 'minimum':
                optima_pind = self.index_of_nearest(minima_x,x)
                optima_x = minima_x[optima_pind]
                optima_x = array([optima_x])
                optima_y = array([minima_y[optima_pind]])

            if optima_type == 'maximum':
                optima_pind = self.index_of_nearest(maxima_x,x)
                optima_x = maxima_x[optima_pind]
                optima_x = array([optima_x])
                optima_y = array([maxima_y[optima_pind]])
            
            if optima_type is None:
                optima_ind = sort(append(maxima_ind, minima_ind))
                optima_x = xr[optima_ind]
                optima_y = yr[optima_ind]
                optima_pind = int(round(get_partial_index(optima_x,x)))
                optima_x = optima_x[optima_pind]
                if optima_x in minima_x:
                    optima_type='minimum'
                if optima_x in maxima_x:
                    optima_type='maximum'
                optima_x = array([optima_x])
                optima_y = array([optima_y[optima_pind]])
            
            return (optima_x, optima_y), optima_type

    def refresh_cursor_optimum(self):
        p1 = self.fig.get_cursor_pos()
        t1 = self.fig.optimum_type1
        self.update_cursor(p1,t1)
        p2 = self.fig.get_cursor2_pos()
        t2 = self.fig.optimum_type2
        self.update_cursor2(p2,t2)


    def update_cursor2(self, pos, optima_type=None):
        opt = self.get_data_value(pos,optima_type)
        if opt is not None:
            optimum, optimum_type = opt[0], opt[1]
            c = "<span style='color: #FFBBBB'>t1: %0.3e</span>"  % (pos)
            self.cursor_fast.setText(c)
            self.fig.set_cursor2(optimum[0][0])
            self.fig.set_optima2(optimum,optimum_type)
            self.update_delta()
        

    def update_cursor(self, pos, optima_type=None):
        opt = self.get_data_value(pos,optima_type)
        if opt is not None:
            optimum, optimum_type = opt[0], opt[1]
            c = "<span style='color: #BBFFBB'>t2: %0.3e</span>"  % (pos)
            self.cursor.setText(c)
            self.fig.set_cursor(optimum[0][0])
            self.fig.set_optima(optimum,optimum_type)
            self.update_delta()
        

    def update_delta(self):
        c1 = self.fig.get_cursor_pos()
        c2 = self.fig.get_cursor2_pos()
        delta = abs(c1-c2)
        del_str = 'delta t: %.3e' % (delta)
        self.delta.setText(del_str)

    def setText(self, text, plot_ind):

        self.fig.set_plot_label(text,plot_ind)'''

'''class DetailDisplayWidget(customWidget):
    def __init__(self, fig_params):
        super().__init__(fig_params)
        
        #self.cut_peak_btn = FlatButton('Add')
        #self.cut_peak_btn.setFixedWidth(90)
        #self.cut_peak_btn.setCheckable(True)
        
        self.add_button_widget_item(QtWidgets.QLabel('Pulse echo:'))
        
        #self.add_button_widget_item(self.cut_peak_btn)
        
        self.apply_btn = FlatButton('Apply')
        self.apply_btn.setFixedWidth(90)
        self.add_button_widget_item(self.apply_btn)
        
        self.add_button_widget_spacer()
        
        #self.resize(800,500)
        


        

'''
'''
class CustomViewBox_adv(pg.ViewBox):  
    plotMouseCursorSignal = pyqtSignal(float)
    plotMouseCursor2Signal = pyqtSignal(float)  
    def __init__(self, *args, **kwds):
        super().__init__()
        #pg.ViewBox.__init__(self, *args, **kwds)
        self.cursor_signals = [self.plotMouseCursorSignal, self.plotMouseCursor2Signal]
        self.vLine = pg.InfiniteLine(angle=90, movable=True,pen=mkPen({'color': '00CC00', 'width': 2}),hoverPen=mkPen({'color': '0000FF', 'width': 2}))
        self.vLine.setPos(nan)
        self.addItem(self.vLine, ignoreBounds=True)
        self.vLine2 = pg.InfiniteLine(angle=90, movable=True,pen=mkPen({'color': 'CC0000', 'width': 2}),hoverPen=mkPen({'color': '0000FF', 'width': 2}))
        self.vLine2.setPos(nan)
        self.addItem(self.vLine2, ignoreBounds=True)
        self.cursors = [self.vLine, self.vLine2]
        self.setMouseMode(self.RectMode)
        self.enableAutoRange(self.XYAxes, True)
        
        self.cursorPoints = [0,0]
        # Enable dragging and dropping onto the GUI 
        self.setAcceptDrops(True) 
        #self.vLine.sigPositionChangeFinished.connect(self.cursor_dragged)
        #self.vLine2.sigPositionChangeFinished.connect(self.cursor_dragged)
        self.vLine.sigPositionChangeFinished.connect(self.cursor_dragged)
        self.vLine2.sigPositionChangeFinished.connect(self.cursor_dragged)


    ## reimplement right-click to zoom out
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            
            pos = ev.pos()  ## using signal proxy turns original arguments into a tuple
            mousePoint = self.mapToView(pos)
            self.cursorPoints[0]=mousePoint.x()
            self.plotMouseCursorSignal.emit(mousePoint.x())  
            
        elif ev.button() == QtCore.Qt.LeftButton: 
            pos = ev.pos()  ## using signal proxy turns original arguments into a tuple
            mousePoint = self.mapToView(pos)
            self.cursorPoints[1]=mousePoint.x()
            self.plotMouseCursor2Signal.emit(mousePoint.x())   

    def set_vLine2_pos(self, pos):
        self.vLine2.blockSignals(True)
        self.vLine2.setPos(pos)
        self.cursorPoints[1] = pos
        self.vLine2.blockSignals(False)

    def set_vLine_pos(self, pos):
        self.vLine.blockSignals(True)
        self.vLine.setPos(pos)
        self.cursorPoints[0] = pos
        self.vLine.blockSignals(False)


    def cursor_dragged(self, cursor):
        ind = self.cursors.index(cursor)
        pos = cursor.getXPos()
        self.cursorPoints[ind]=pos
        sig = self.cursor_signals[ind]
        sig.emit(pos)
'''