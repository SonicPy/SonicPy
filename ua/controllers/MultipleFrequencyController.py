#!/usr/bin/env python

import os
import time
from PyQt5.QtCore import QObject, pyqtSignal
from ua.models.MultipleFrequenciesModel import MultipleFrequenciesModel
from ua.models.EchoesResultsModel import EchoesResultsModel
from ua.widgets.MultipleFrequenciesWidget import MultipleFrequenciesWidget

from ua.controllers.OverViewController import OverViewController
from ua.controllers.UltrasoundAnalysisController import UltrasoundAnalysisController
from ua.controllers.ArrowPlotController import ArrowPlotController

from PyQt5 import QtWidgets, QtCore

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

        self.make_connections()
        if app is not None:
            self.setStyle(app)
        
    def make_connections(self): 
        
        self.widget.frequency_sweep_widget.do_all_frequencies_btn.clicked.connect(self.do_all_frequencies_btn_callback)
        self.widget.broadband_pulse_widget.do_all_frequencies_btn.clicked.connect(self.do_all_frequencies_btn_callback)

    def do_all_frequencies_btn_callback(self):

        mode = self.widget.mode_tab_widget.currentIndex()
        if mode == 0:

            if len(self.model.files):
                progress_dialog = QtWidgets.QProgressDialog("Calculating", "Abort", 0, len(self.model.files), None)
                progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
                progress_dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint)
                progress_dialog.show()
                QtWidgets.QApplication.processEvents()
                self.do_all_frequency_sweep(progress_dialog=progress_dialog)
                progress_dialog.close()
                QtWidgets.QApplication.processEvents()
        elif mode == 1:
            self.do_all_broadband_pulse()
                

    def do_all_frequency_sweep(self, *args, **kwargs):
        files = self.model.files
        cond = self.model.cond
        if 'progress_dialog' in kwargs:
            progress_dialog = kwargs['progress_dialog']
        else:
            progress_dialog = QtWidgets.QProgressDialog()

        
        for d, f in enumerate(files):
            
            #update progress bar only every 2 files to save time
            progress_dialog.setValue(d)
            QtWidgets.QApplication.processEvents()
            fname = files[f]
            data = self.overview_controller.get_data_by_filename(fname)
            self.correlation_controller. update_data_by_dict_silent(data)
            bounds = self.correlation_controller.get_lr_bounds()
            freq = f * 1e6
            self.correlation_controller.calculate_data_silent(freq,bounds)
            self.correlation_controller.save_result(signaling = False)

            if progress_dialog.wasCanceled():
                break
        QtWidgets.QApplication.processEvents()
            

    def do_all_broadband_pulse(self):
        print('do all broadband pulse')

    def file_selected(self, data):

        fname = data['fname']
        fbase = data['freq']
        cond = data['cond']

        if self.model.cond != cond:
            # this code checks what frequencies are available for the selected condition and updates the model

            f_start = self.overview_controller.widget.freq_start.value()
            f_step = self.overview_controller.widget.freq_step.value()
            self.model.set_condition(cond)
            self.model.set_fbase(fbase) 
            self.model.set_fname(fname)
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
            self.widget.frequency_sweep_widget.frequency_sweep_widget_lbl.setText(text_out)
        
        self.recover_selected_regions(fname)
        self.update_analysis(data)
        self.update_arrow_plot(data)

    def recover_selected_regions(self, fname):
        
        echoes_p, echoes_s = self.echoes_results_model.get_echoes()

        # changing a region typically triggers calculations so we disable this connection here and reanable it later
        self.correlation_controller.disconnect_regions()
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
        self.correlation_controller.connect_regions()

    def update_analysis(self,data):

        fbase = data['freq']

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
        

    def update_arrow_plot(self, data):
        fbase = data['freq']
        cond = data['cond']

        echo_type = ''
        if  self.correlation_controller.display_window.p_wave_btn.isChecked():
            echo_type = "P"
        elif self.correlation_controller.display_window.s_wave_btn.isChecked():
            echo_type = "S"

        f_start = self.overview_controller.widget.freq_start.value()
        f_step = self.overview_controller.widget.freq_step.value()
        
        f_freq_ind = int(fbase)
        freq = f_start + f_freq_ind * f_step    

        #echoes_by_condition = self.echoes_results_model.get_echoes_by_condition(cond, echo_type)
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