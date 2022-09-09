#!/usr/bin/env python

from audioop import avg
import os
import time
from PyQt5.QtCore import QObject, pyqtSignal
from ua.models.OutputModel import OutputModel
from ua.models.EchoesResultsModel import EchoesResultsModel
from ua.widgets.OutputWidget import OutputWidget

from ua.controllers.OverViewController import OverViewController
from ua.controllers.UltrasoundAnalysisController import UltrasoundAnalysisController
from ua.controllers.ArrowPlotController import ArrowPlotController

from PyQt5 import QtWidgets, QtCore

############################################################

class OutputController(QObject):

    condition_selected_signal = pyqtSignal(str)

    def __init__(self, overview_controller : OverViewController, 
                    correlation_controller: UltrasoundAnalysisController, 
                        arrow_plot_controller: ArrowPlotController, app=None, 
                            results_model : EchoesResultsModel = EchoesResultsModel()):
        super().__init__()
        self.echoes_results_model = results_model
        self.overview_controller = overview_controller
        self.correlation_controller = correlation_controller
        self.arrow_plot_controller = arrow_plot_controller
        
        self.model = OutputModel(results_model)

        self.widget = OutputWidget()

        self.make_connections()
        if app is not None:
            self.setStyle(app)
        
    def make_connections(self): 
        
        self.widget.output_tw.itemSelectionChanged.connect(self.option_tw_selection_changed_callback)

    def option_tw_selection_changed_callback(self, *args):
        row = self.widget.get_selected_output_row()
        conds = self.model.conds
        condition = conds[row]
        self.condition_selected_signal.emit(condition)


    def new_result(self, condition, wave_type, result):

        
        if len(result):
            
            times = []
            times_e = []
            for opt in result:
                t = result[opt]['time_delay']
                t_e = result[opt]['time_delay_std']
                times.append(t)
                times_e.append(t_e)
            time = sum(times) / len(times) * 1e3
            time_e = sum(times_e) / len(times_e ) * 1e3
            conds = self.model.conds
            ind = conds.index(condition)
            if wave_type == 'P':
                self.widget.set_output_tp(ind, time)
                self.widget.set_output_t_e_p(ind, time_e)
            if wave_type == 'S':
                self.widget.set_output_ts(ind, time)
                self.widget.set_output_t_e_s(ind, time_e)

    def update_conditions(self):
        conds = self.get_all_conditions()
        self.model.reset()
        self.model.set_conds(conds)
        self.widget.clear_output()
        for c in conds:
            self.widget.add_condition(c)

    def get_all_conditions(self):
        conds = self.overview_controller.get_conditions_list()
        return conds

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