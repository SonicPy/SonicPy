# -*- coding: utf8 -*-

# DISCLAIMER
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Principal author: R. Hrubiak (hrubiak@anl.gov)
# Copyright (C) 2018-2019 ANL, Lemont, USA

# Based on code from Dioptas - GUI program for fast processing of 2D X-ray diffraction data

import os
import numpy as np
from PyQt5 import QtWidgets, QtCore
import copy
from models.PhaseModel import PhaseLoadError
from utilities.HelperModule import get_base_name
from controllers.PhaseInPatternController import PhaseInPatternController

from widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog, CifConversionParametersDialog
from models.PhaseModel import PhaseModel
from widgets.PhaseWidget import PhaseWidget
import utilities.hpMCAutilities as mcaUtil

class PhaseController(object):
    """
    IntegrationPhaseController handles all the interaction between the phase controls in the IntegrationView and the
    PhaseData object. It needs the PatternData object to properly handle the rescaling of the phase intensities in
    the pattern plot and it needs the calibration data to have access to the currently used wavelength.
    """

    def __init__(self, plotWidget, plotController, directories):
        """
        :param integration_widget: Reference to an IntegrationWidget
        :param dioptas_model: reference to DioptasModel object

        :type integration_widget: IntegrationWidget
        :type dioptas_model: DioptasModel
        """

        
        
        self.directories = directories
        
        #self.roi_controller = roiController
        self.plotController = plotController

        
        self.pattern_widget = plotWidget
        self.phase_widget = PhaseWidget()
        
        self.phase_model = PhaseModel()

        self.phase_in_pattern_controller = \
                    PhaseInPatternController(self.plotController, 
                                            phaseController=self, 
                                            pattern_widget=plotWidget, 
                                            phase_model=self.phase_model)
     
        self.phase_lw_items = []
        self.create_signals()
        self.update_vs_step()
        self.update_vp_step()
        self.update_d_step()
        
        self.phases = []
        

    

    def show_view(self):
        self.active = True

        self.phase_widget.raise_widget()

    def create_signals(self):
        # Button Callbacks
        self.connect_click_function(self.phase_widget.add_btn, self.add_btn_click_callback)
        self.connect_click_function(self.phase_widget.delete_btn, self.remove_btn_click_callback)
        self.connect_click_function(self.phase_widget.clear_btn, self.clear_phases)
        
        self.connect_click_function(self.phase_widget.save_list_btn, self.save_btn_clicked_callback)
        self.connect_click_function(self.phase_widget.load_list_btn, self.load_btn_clicked_callback)

        # P-T callbacks
        self.phase_widget.vp_step_msb.editingFinished.connect(self.update_vp_step)
        self.phase_widget.vs_step_msb.editingFinished.connect(self.update_vs_step)
        self.phase_widget.d_step_msb.editingFinished.connect(self.update_d_step)
        self.phase_widget.vp_sb_value_changed.connect(self.phase_model.set_vp)
        self.phase_widget.vs_sb_value_changed.connect(self.phase_model.set_vs)
        self.phase_widget.d_sb_value_changed.connect(self.phase_model.set_d)
        
        
        # File drag and drop
        self.phase_widget.file_dragged_in.connect(self.file_dragged_in)

        # Color and State
        self.phase_widget.color_btn_clicked.connect(self.color_btn_clicked)
        self.phase_widget.show_cb_state_changed.connect(self.phase_model.set_phase_visible)
        self.phase_widget.apply_to_all_cb.stateChanged.connect(self.apply_to_all_callback)

        # TableWidget
        self.phase_widget.phase_tw.horizontalHeader().sectionClicked.connect(self.phase_tw_header_section_clicked)
        
        # Signals from phase model
        self.phase_model.phase_added.connect(self.phase_added)
        self.phase_model.phase_removed.connect(self.phase_removed)
        self.phase_model.phase_changed.connect(self.phase_changed)
        
    def file_dragged_in(self,files):
        self.add_btn_click_callback(filenames=files)

  
    def connect_click_function(self, emitter, function):
        emitter.clicked.connect(function)

    def add_btn_click_callback(self, *args, **kwargs):
        """
        Loads a new phase from vpvs file.
        :return:
        """
        self._add_phase('file1.vpvs')
        '''
        filenames = kwargs.get('filenames', None)

        if filenames is None:
            filenames = open_files_dialog(None, "Load Phase(s).",
                                          self.directories.phase )

            
        if len(filenames):
            self.directories.phase = os.path.dirname(str(filenames[0]))
            progress_dialog = QtWidgets.QProgressDialog("Loading multiple phases.", "Abort Loading", 0, len(filenames),
                                                        None)
            progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            progress_dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            progress_dialog.show()
            QtWidgets.QApplication.processEvents()
            for ind, filename in enumerate(filenames):
                filename = str(filename)
                progress_dialog.setValue(ind)
                progress_dialog.setLabelText("Loading: " + os.path.basename(filename))
                QtWidgets.QApplication.processEvents()

                self._add_phase(filename)

                if progress_dialog.wasCanceled():
                    break
            progress_dialog.close()
            QtWidgets.QApplication.processEvents()
        '''

    def _add_phase(self, filename):
        #try:
        if filename.endswith("vpvs"):
            self.phase_model.add_vpvs(filename)

        '''    
        elif filename.endswith(".cif"):
            self.cif_conversion_dialog.exec_()
            self.phase_model.add_cif(filename,
                                            self.cif_conversion_dialog.int_cutoff,
                                            self.cif_conversion_dialog.min_d_spacing)
           #except:
            #self.integration_widget.show_error_msg(
            #    'Could not load:\n\n{}.\n\nPlease check if the format of the input file is correct.'. \
            #        format(e.filename))
        #    mcaUtil.displayErrorMessage('phase')
        '''
      

    def phase_added(self):
        color = self.phase_model.phase_colors[-1]
        self.phase_widget.add_phase(get_base_name(self.phase_model.phase_files[-1]),
                                    '#%02x%02x%02x' % (int(color[0]), int(color[1]), int(color[2])))


    def phase_changed(self, ind):
        phase_name = get_base_name(self.phase_model.phases[ind].filename)
        if self.phase_model.phases[ind].params['modified']:
            phase_name += '*'
        self.phase_widget.rename_phase(ind, phase_name)
        self.phase_widget.set_phase_vp(ind, self.phase_model.phases[ind].params['vp'])
        self.phase_widget.set_phase_vs(ind, self.phase_model.phases[ind].params['vs'])
        
        #self.phase_widget.vs_sbs[ind].setEnabled(self.phase_model.phases[ind].has_thermal_expansion())


    def add_phase_plot(self):
        """
        Adds a phase to the Pattern view.
        :return:
        """
        axis_range = self.plotController.getRange()
        
        x_range = axis_range[0]
        y_range = axis_range[1]
        self.phases = [positions, intensities, baseline] = \
            self.phase_model.get_rescaled_reflections(
                -1, 'pattern_placeholder_var',
                x_range, y_range)
                
        color = self.pattern_widget.add_phase(self.phase_model.phases[-1].name,
                                              positions,
                                              intensities,
                                              baseline)
        #print(color)
        return color
        


    def remove_btn_click_callback(self):
        """
        Deletes the currently selected Phase
        """
        cur_ind = self.phase_widget.get_selected_phase_row()
        if cur_ind >= 0:
            self.phase_model.del_phase(cur_ind)

    def phase_removed(self, ind):
        self.phase_widget.del_phase(ind)
        
       

    def load_btn_clicked_callback(self):
        filename = open_file_dialog(self.phase_widget, caption="Load Phase List",
                                    directory=self.directories.phase ,
                                    filter="*.txt")

        if filename == '':
            return
        with open(filename, 'r') as phase_file:
            if phase_file == '':
                return
            for line in phase_file.readlines():
                line = line.replace('\n', '')
                phase, use_flag, color, name, vp, vs = line.split(',')
                self.add_btn_click_callback(filenames=[phase])
                row = self.phase_widget.phase_tw.rowCount() - 1
                self.phase_widget.phase_show_cbs[row].setChecked(bool(use_flag))
                btn = self.phase_widget.phase_color_btns[row]
                btn.setStyleSheet('background-color:' + color)
                self.phase_model.set_color(row,color)
                self.phase_widget.phase_tw.item(row, 2).setText(name)
                self.phase_widget.set_phase_vp(row, float(vp))
                self.phase_model.set_vp(row, float(vp))
                vs = float(vs)

                if vs is not '':
                    self.phase_widget.set_phase_vs(row, vs)
                    self.phase_model.set_vs(row, vs)


    def save_btn_clicked_callback(self):
        if len(self.phase_model.phase_files) < 1:
            return
        filename = save_file_dialog(self.phase_widget, "Save Phase List.",
                                    '',
                                    'Text (*.txt)')

        if filename == '':
            return

        with open(filename, 'w') as phase_file:
            for file_name, phase_cb, color_btn, row in zip(self.phase_model.phase_files,
                                                           self.phase_widget.phase_show_cbs,
                                                           self.phase_widget.phase_color_btns,
                                                           range(self.phase_widget.phase_tw.rowCount())):
                phase_file.write(file_name + ',' + str(phase_cb.isChecked()) + ',' +
                                 color_btn.styleSheet().replace('background-color:', '').replace(' ', '') + ',' +
                                 self.phase_widget.phase_tw.item(row, 2).text() + ',' +
                                 self.phase_widget.phase_tw.item(row, 3).text().split(' ')[0] + ',' +
                                 self.phase_widget.phase_tw.item(row, 4).text().split(' ')[0] + '\n')

    def clear_phases(self):
        """
        Deletes all phases from the GUI and phase data
        """
        while self.phase_widget.phase_tw.rowCount() > 0:
            self.remove_btn_click_callback()
            

    def update_vp_step(self):
        value = self.phase_widget.vp_step_msb.value()
        self.phase_widget.vp_sb.setSingleStep(value)

  

    def update_vs_step(self):
        value = self.phase_widget.vs_step_msb.value()
        self.phase_widget.vs_sb.setSingleStep(value)

    def update_d_step(self):
        value = self.phase_widget.d_step_msb.value()
        self.phase_widget.d_sb.setSingleStep(value)


    def phase_selection_changed(self, row, col, prev_row, prev_col):
        cur_ind = row
        vp = self.phase_model.phases[cur_ind].params['vp']
        vs = self.phase_model.phases[cur_ind].params['vs']

        self.phase_widget.vp_sb.blockSignals(True)
        self.phase_widget.vp_sb.setValue(vp)
        self.phase_widget.vp_sb.blockSignals(False)

        self.phase_widget.vs_sb.blockSignals(True)
        self.phase_widget.vs_sb.setValue(vs)
        self.phase_widget.vs_sb.blockSignals(False)
        self.update_vs_control_visibility(row)

        

    def update_vs_control_visibility(self, row_ind=None):
        if row_ind is None:
            row_ind = self.phase_widget.get_selected_phase_row()

        if row_ind == -1:
            return

        if self.phase_model.phases[row_ind-1].has_thermal_expansion():
            self.phase_widget.vs_sb.setEnabled(True)
            self.phase_widget.vs_step_msb.setEnabled(True)
        else:
            self.phase_widget.vs_sb.setDisabled(True)
            self.phase_widget.vs_step_msb.setDisabled(True)

    def color_btn_clicked(self, ind, button):
        previous_color = button.palette().color(1)
        new_color = QtWidgets.QColorDialog.getColor(previous_color, self.pattern_widget)
        if new_color.isValid():
            color = new_color.toRgb()
        else:
            color = previous_color.toRgb()
        self.phase_model.set_color(ind, (color.red(), color.green(), color.blue()))
        button.setStyleSheet('background-color:' + str(color.name()))

    def apply_to_all_callback(self):
        self.phase_model.same_conditions = self.phase_widget.apply_to_all_cb.isChecked()

    def phase_tw_header_section_clicked(self, ind):
        if ind != 0:
            return

        current_checkbox_state = False
        # check whether any checkbox is checked, if one is true current_checkbox_state will be True too
        for cb in self.phase_widget.phase_show_cbs:
            current_checkbox_state = current_checkbox_state or cb.isChecked()

        # assign the the opposite to all checkboxes
        for cb in self.phase_widget.phase_show_cbs:
            cb.setChecked(not current_checkbox_state)



