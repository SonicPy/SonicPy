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
from PyQt5 import QtWidgets

from um.widgets.UtilityWidgets import open_files_dialog
from um.widgets.OverlayWidget import OverlayWidget
from um.models.OverlayModel import OverlayModel

# imports for type hinting in PyCharm -- DO NOT DELETE
#from ...widgets.integration import IntegrationWidget
#from ...model.DioptasModel import DioptasModel


class OverlayController(object):
    """
    IntegrationOverlayController handles all the interaction between the Overlay controls of the integration view and
    the corresponding overlay data in the Pattern Model.
    """

    def __init__(self, mcc, plotWidget):
        """
        :param widget: Reference to IntegrationWidget object
        :param pattern_model: Reference to PatternModel object

        :type widget: IntegrationWidget
        :type dioptas_model: DioptasModel
        """
        
        self.overlay_widget = OverlayWidget()
        self.model = mcc
        self.overlay_model = OverlayModel()
        self.pattern_widget = plotWidget.pg
      
        self.overlay_lw_items = []
        self.create_signals()
        self.active = False

    def create_signals(self):
        self.connect_click_function(self.overlay_widget.add_btn, self.add_overlay_btn_click_callback)
        self.connect_click_function(self.overlay_widget.delete_btn, self.delete_btn_click_callback)
        self.connect_click_function(self.overlay_widget.move_up_btn, self.move_up_overlay_btn_click_callback)
        self.connect_click_function(self.overlay_widget.move_down_btn, self.move_down_overlay_btn_click_callback)
        self.overlay_widget.clear_btn.clicked.connect(self.clear_overlays_btn_click_callback)

        self.overlay_widget.overlay_tw.currentCellChanged.connect(self.overlay_selected)
        self.overlay_widget.color_btn_clicked.connect(self.color_btn_clicked)
        self.overlay_widget.show_cb_state_changed.connect(self.show_cb_state_changed)
        self.overlay_widget.name_changed.connect(self.rename_overlay)

        self.overlay_widget.scale_step_msb.editingFinished.connect(self.update_scale_step)
        self.overlay_widget.offset_step_msb.editingFinished.connect(self.update_overlay_offset_step)
        self.overlay_widget.scale_sb.valueChanged.connect(self.scale_sb_changed)
        self.overlay_widget.offset_sb.valueChanged.connect(self.offset_sb_changed)

        self.overlay_widget.waterfall_btn.clicked.connect(self.waterfall_btn_click_callback)
        self.overlay_widget.waterfall_reset_btn.clicked.connect(self.overlay_model.reset_overlay_offsets)

        self.overlay_widget.set_as_bkg_btn.clicked.connect(self.set_as_bkg_btn_click_callback)
        self.overlay_widget.widget_closed.connect(self.widget_closed)
        self.overlay_widget.file_dragged_in.connect(self.file_dragged_in)

        # creating the quick-actions signals

        #self.connect_click_function(self.overlay_widget.qa_set_as_overlay_btn, self.set_current_pattern_as_overlay)
        #self.connect_click_function(self.overlay_widget.qa_set_as_background_btn, self.set_current_pattern_as_background)

        # pattern_data signals
        self.overlay_model.overlay_removed.connect(self.overlay_removed)
        self.overlay_model.overlay_added.connect(self.overlay_added)
        self.overlay_model.overlay_changed.connect(self.overlay_changed)

        

    def file_dragged_in(self,files):
        
        self.add_overlay_btn_click_callback(filenames=files)    

    def showWidget(self):
        self.overlay_widget.raise_widget()
        self.active = True
        #print(self.active)

    def widget_closed(self):
        self.active = False
        #print(self.active)

    def connect_click_function(self, emitter, function):
        emitter.clicked.connect(function)

    def update_x_scale(self,unit):
        self.overlay_model.set_x_scale(unit)

    

    def add_overlay_btn_click_callback(self,**kwargs):
        """

        """
        filenames = kwargs.get('filenames', None)

        if filenames is None:
            filenames = open_files_dialog(self.overlay_widget, "Load Overlay(s).",
                                      self.model.working_directories.savedata)  

        
        if len(filenames):
            
            for filename in filenames:
                filename = str(filename)
                self.overlay_model.add_overlay_file(filename)
            self.model.working_directories.savedata = os.path.dirname(str(filenames[0]))

    def overlay_added(self):
        """
        callback when overlay is added to the PatternData
        """
        color = self.pattern_widget.add_overlay(self.overlay_model.overlays[-1])
        det_mode = self.overlay_model.overlays[-1].det_mode
        det_setting = self.overlay_model.overlays[-1].get_det_setting()
        self.overlay_widget.add_overlay(self.overlay_model.overlays[-1].name,
                                               '#%02x%02x%02x' % (int(color[0]), int(color[1]), int(color[2])),det_mode,det_setting)

    def delete_btn_click_callback(self):
        """
        Removes the currently in the overlay table selected overlay from the table, pattern_data and pattern_view
        """
        cur_ind = self.overlay_widget.get_selected_overlay_row()
        if cur_ind < 0:
            return
        '''
        if self.model.pattern_model.background_pattern == self.overlay_model.overlays[cur_ind]:
            self.model.pattern_model.background_pattern = None
        '''
        self.overlay_model.remove_overlay(cur_ind)

    def overlay_removed(self, ind):
        """
        callback when overlay is removed from PatternData
        :param ind: index of overlay removed
        """
        self.pattern_widget.remove_overlay(ind)
        self.overlay_widget.remove_overlay(ind)

        # if no more overlays are present the set_as_bkg_btn should be unchecked
        if self.overlay_widget.overlay_tw.rowCount() == 0:
            self.overlay_widget.set_as_bkg_btn.setChecked(False)

    def move_up_overlay_btn_click_callback(self):
        cur_ind = self.overlay_widget.get_selected_overlay_row()
        if cur_ind < 1:
            return
        new_ind = cur_ind - 1

        self.overlay_widget.move_overlay_up(cur_ind)
        self.overlay_model.overlays.insert(new_ind, self.overlay_model.overlays.pop(cur_ind))
        self.pattern_widget.move_overlay_up(cur_ind)

        if self.overlay_widget.show_cbs[cur_ind].isChecked():
            self.pattern_widget.legend.showItem(cur_ind + 1)
        else:
            self.pattern_widget.legend.hideItem(cur_ind + 1)

        if self.overlay_widget.show_cbs[new_ind].isChecked():
            self.pattern_widget.legend.showItem(cur_ind)
        else:
            self.pattern_widget.legend.hideItem(cur_ind)

    def move_down_overlay_btn_click_callback(self):
        cur_ind = self.overlay_widget.get_selected_overlay_row()
        if cur_ind < 0 or cur_ind >= self.overlay_widget.overlay_tw.rowCount() - 1:
            return

        self.overlay_widget.move_overlay_down(cur_ind)
        self.overlay_model.overlays.insert(cur_ind + 1, self.overlay_model.overlays.pop(cur_ind))
        self.pattern_widget.move_overlay_down(cur_ind)

        if self.overlay_widget.show_cbs[cur_ind].isChecked():
            self.pattern_widget.legend.showItem(cur_ind + 1)
        else:
            self.pattern_widget.legend.hideItem(cur_ind + 1)

        if self.overlay_widget.show_cbs[cur_ind + 1].isChecked():
            self.pattern_widget.legend.showItem(cur_ind + 2)
        else:
            self.pattern_widget.legend.hideItem(cur_ind + 2)

    def clear_overlays_btn_click_callback(self):
        """
        removes all currently loaded overlays
        """
        while self.overlay_widget.overlay_tw.rowCount() > 0:
            self.delete_btn_click_callback()

    def update_scale_step(self):
        """
        Sets the step size for scale spinbox from the step text box.
        """
        value = self.overlay_widget.scale_step_msb.value()
        self.overlay_widget.scale_sb.setSingleStep(value)

    def update_overlay_offset_step(self):
        """
        Sets the step size for the offset spinbox from the offset_step text box.
        """
        value = self.overlay_widget.offset_step_msb.value()
        self.overlay_widget.offset_sb.setSingleStep(value)

    def overlay_selected(self, row, *args):
        """
        Callback when the selected row in the overlay table is changed. It will update the scale and offset values
        for the newly selected overlay and check whether it is set as background or not and check the
        the set_as_bkg_btn appropriately.
        :param row: selected row in the overlay table
        """
        cur_ind = row
        self.overlay_widget.scale_sb.blockSignals(True)
        self.overlay_widget.offset_sb.blockSignals(True)
        self.overlay_widget.scale_sb.setValue(self.overlay_model.overlays[cur_ind].scaling)
        self.overlay_widget.offset_sb.setValue(self.overlay_model.overlays[cur_ind].offset)

        self.overlay_widget.scale_sb.blockSignals(False)
        self.overlay_widget.offset_sb.blockSignals(False)
        '''
        if self.model.pattern_model.background_pattern == self.overlay_model.overlays[cur_ind]:
            self.overlay_widget.set_as_bkg_btn.setChecked(True)
        else:
            self.overlay_widget.set_as_bkg_btn.setChecked(False)
        '''

    def color_btn_clicked(self, ind, button):
        """
        Callback for the color buttons in the overlay table. Opens up a color dialog. The color of the overlay and
        its respective button will be changed according to the selection
        :param ind: overlay ind
        :param button: button to color
        """
        previous_color = button.palette().color(1)
        new_color = QtWidgets.QColorDialog.getColor(previous_color, self.overlay_widget)
        if new_color.isValid():
            color = str(new_color.name())
        else:
            color = str(previous_color.name())
        self.pattern_widget.set_overlay_color(ind, color)
        button.setStyleSheet('background-color:' + color)

    def scale_sb_changed(self, value):
        """
        Callback for scale_sb spinbox.
        :param value: new scale value
        """
        cur_ind = self.overlay_widget.get_selected_overlay_row()
        self.overlay_model.set_overlay_scaling(cur_ind, value)
        #if self.overlay_model.overlays[cur_ind] == self.model.pattern_model.background_pattern:
        #    self.model.pattern_changed.emit()

    def offset_sb_changed(self, value):
        """
        Callback gor the offset_sb spinbox.
        :param value: new value
        """
        cur_ind = self.overlay_widget.get_selected_overlay_row()
        self.overlay_model.set_overlay_offset(cur_ind, value)
        #if self.overlay_model.overlays[cur_ind] == self.model.pattern_model.background_pattern:
        #    self.model.pattern_changed.emit()

    def overlay_changed(self, ind):
        self.pattern_widget.update_overlay(self.overlay_model.overlays[ind], ind)
        cur_ind = self.overlay_widget.get_selected_overlay_row()
        if ind == cur_ind:
            self.overlay_widget.offset_sb.blockSignals(True)
            self.overlay_widget.scale_sb.blockSignals(True)
            self.overlay_widget.offset_sb.setValue(self.overlay_model.get_overlay_offset(ind))
            self.overlay_widget.scale_sb.setValue(self.overlay_model.get_overlay_scaling(ind))
            self.overlay_widget.offset_sb.blockSignals(False)
            self.overlay_widget.scale_sb.blockSignals(False)

    def waterfall_btn_click_callback(self):
        separation = self.overlay_widget.waterfall_separation_msb.value()
        self.overlay_model.overlay_waterfall(separation)

    def set_as_bkg_btn_click_callback(self):
        """
        Callback for the set_as_bkg_btn QPushButton. Will try to either set the currently selected overlay as
        background or unset if it already. Any other overlay which was set before as bkg will
        """
        cur_ind = self.overlay_widget.get_selected_overlay_row()
        if cur_ind is -1:  # no overlay selected
            self.overlay_widget.set_as_bkg_btn.setChecked(False)
            return

        if not self.overlay_widget.set_as_bkg_btn.isChecked():
            ## if the overlay is not currently a background
            # it will unset the current background and redisplay
            #self.model.pattern_model.background_pattern = None
            pass
        else:
            # if the overlay is currently the active background
            #self.model.pattern_model.background_pattern = self.overlay_model.overlays[cur_ind]
            if self.overlay_widget.show_cb_is_checked(cur_ind):
                self.overlay_widget.show_cb_set_checked(cur_ind, False)

    def set_current_pattern_as_overlay(self):
        return
        self.overlay_model.add_overlay_pattern(self.model.pattern)

    def set_current_pattern_as_background(self):
        return
        self.overlay_model.add_overlay_pattern(self.model.pattern)
        #self.model.pattern_model.background_pattern = self.overlay_model.overlays[-1]

        self.overlay_widget.set_as_bkg_btn.setChecked(True)
        self.overlay_widget.show_cb_set_checked(-1, False)

    def overlay_set_as_bkg(self, ind):
        cur_selected_ind = self.overlay_widget.get_selected_overlay_row()
        self.overlay_widget.set_as_bkg_btn.setChecked(ind == cur_selected_ind)
        # hide the original overlay
        if self.overlay_widget.show_cb_is_checked(ind):
            self.overlay_widget.show_cb_set_checked(ind, False)

    def overlay_unset_as_bkg(self, ind):
        self.overlay_widget.show_cb_set_checked(ind, True)
        #if self.model.pattern_model.bkg_ind == -1:
        #    self.overlay_widget.set_as_bkg_btn.setChecked(False)

    def show_cb_state_changed(self, ind, state):
        """
        Callback for the checkboxes in the overlay tablewidget. Controls the visibility of the overlay in the pattern
        view
        :param ind: index of overlay
        :param state: boolean value whether the checkbox was checked or unchecked
        """
        if state:
            self.pattern_widget.show_overlay(ind)
        else:
            self.pattern_widget.hide_overlay(ind)

    def rename_overlay(self, ind, name):
        """
        Callback for changing the name in the overlay tablewidget (by double clicking the name and entering a new one).
        This will update the visible name in the pattern view
        :param ind: index of overlay for which the name was changed
        :param name: new name
        """
        self.pattern_widget.rename_overlay(ind, name)
        self.overlay_model.overlays[ind].name = name
