#!/usr/bin/env python

import os
from PyQt5.QtCore import QObject, pyqtSignal
from ua.models.MultipleFrequenciesModel import MultipleFrequenciesModel
from ua.models.EchoesResultsModel import EchoesResultsModel
from ua.widgets.MultipleFrequenciesWidget import MultipleFrequenciesWidget

from ua.controllers.OverViewController import OverViewController
from ua.controllers.UltrasoundAnalysisController import UltrasoundAnalysisController
from ua.controllers.ArrowPlotController import ArrowPlotController

############################################################

class MultipleFrequencyController(QObject):

    
    def __init__(self, overview_controller : OverViewController, 
                    correlation_controller: UltrasoundAnalysisController, 
                        arrow_plot_controller: ArrowPlotController, app=None, 
                            results_model : EchoesResultsModel = EchoesResultsModel()):
        super().__init__()
        self.echoes_results_model = results_model
        self.overview_controller = overview_controller
        self.correlation_controller = correlation_controller
        self.arrow_plot_controller = arrow_plot_controller
        
        self.model = MultipleFrequenciesModel(results_model)

        self.widget = MultipleFrequenciesWidget()

        if app is not None:
            self.setStyle(app)
        
    def make_connections(self): 
        
        pass

    def file_selected(self, data):

        fname = data['fname']
        fbase = data['freq']
        cond = data['cond']

        if self.model.cond != cond:

            f_start = self.overview_controller.widget.freq_start.value()
            f_step = self.overview_controller.widget.freq_step.value()
            self.model.set_condition(cond)
            self.widget.condition_val.setText(str(self.model.cond))

            freqs = self.overview_controller.model.fps_cond[cond]
            
            files = {}
            for freq_ind in freqs:
                file = freqs[freq_ind]
                freq_ind_int = int(freq_ind)
                freq_val = f_start + freq_ind_int * f_step
                files[freq_val] = file

            self.model.set_files(files)

            all_freqs = list(self.model.files.keys())
            max_f = max(all_freqs)
            min_f = min(all_freqs)
            count = len(all_freqs)
            text_out = str(count)+" available frequencies from " +str(min_f)+" to " +str(max_f)
            self.widget.frequency_sweep_widget_lbl.setText(text_out)
        
        self.update_analysis(data)

    def update_analysis(self,data):

        fname = data['fname']
        fbase = data['freq']
        cond = data['cond']

        echo_type = ''
        if  self.correlation_controller.display_window.p_wave_btn.isChecked():
            echo_type = "P"
        elif self.correlation_controller.display_window.s_wave_btn.isChecked():
            echo_type = "S"


        echoes_p, echoes_s = self.echoes_results_model.get_echoes()

    
        if fname in echoes_p:
            echo_p = echoes_p[fname]
            bounds_p = echo_p['echo_bounds']
            self.correlation_controller.display_window.lr1_p.setRegion(bounds_p[0])
            self.correlation_controller.display_window.lr2_p.setRegion(bounds_p[1])
        
        if fname in echoes_s:
            echo_s = echoes_s[fname]
            bounds_s = echo_s['echo_bounds']
            self.correlation_controller.display_window.lr1_s.setRegion(bounds_s[0])
            self.correlation_controller.display_window.lr2_s.setRegion(bounds_s[1])

        f_start = self.overview_controller.widget.freq_start.value()
        f_step = self.overview_controller.widget.freq_step.value()
        
        f_freq_ind = int(fbase)
        freq = f_start + f_freq_ind * f_step

        self.correlation_controller.update_data_by_dict(data)
        
        # setting frequency input normally triggers calculation of correlation so set with out triggeing signals        
        self.correlation_controller.display_window.freq_ebx.blockSignals(True)
        self.correlation_controller.display_window.freq_ebx.setValue(freq)
        self.correlation_controller.display_window.freq_ebx.blockSignals(False)
        
        
        self.correlation_controller.calculate_data()

        echoes_by_condition = self.echoes_results_model.get_echoes_by_condition(cond, echo_type)
        self.arrow_plot_controller.set_wave_type(echo_type)
        self.arrow_plot_controller.set_condition( cond) 
        self.arrow_plot_controller.refresh_model()
        self.arrow_plot_controller.set_frequency_cursor(freq)


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