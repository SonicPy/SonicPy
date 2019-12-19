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


from utilities.HelperModule import get_partial_index

# imports for type hinting in PyCharm -- DO NOT DELETE
#from ....model.DioptasModel import DioptasModel
#from ....widgets.integration import IntegrationWidget


class PhaseInPatternController(object):
    """
    PhaseInPatternController handles all the interaction between the phases and the pattern view.
    """

    def __init__(self, plotController, phaseController,  pattern_widget, phase_model):
        """
        :param integration_widget: Reference to an IntegrationWidget
        :param dioptas_model: reference to DioptasModel object

        :type integration_widget: IntegrationWidget
        :type dioptas_model: DioptasModel
        """
        #self.phase_controller = phaseController
        self.plotController  = plotController
        self.phase_model = phase_model
        #self.integration_widget = integration_widget
        self.pattern_widget = pattern_widget
        

        self.connect()

    def connect(self):
        self.phase_model.phase_added.connect(self.add_phase_plot)
        self.phase_model.phase_removed.connect(self.pattern_widget.del_phase)

        self.phase_model.phase_changed.connect(self.update_phase_lines)
        self.phase_model.phase_changed.connect(self.update_phase_legend)
        self.phase_model.phase_changed.connect(self.update_phase_color)
        self.phase_model.phase_changed.connect(self.update_phase_visible)
        self.phase_model.phase_changed.connect(self.pattern_widget.update_phase_line_visibilities)

        self.phase_model.reflection_added.connect(self.reflection_added)
        self.phase_model.reflection_deleted.connect(self.reflection_deleted)

        # pattern signals
        #self.pattern_widget.view_box.sigRangeChangedManually.connect(self.update_all_phase_lines)
        #self.pattern_widget.pattern_plot.autoBtn.clicked.connect(self.update_all_phase_lines)
        self.plotController.dataPlotUpdated.connect(self.pattern_data_changed)

       

    
    def add_phase_plot(self):
        """
        Adds a phase to the Pattern Plot
        """
        axis_range = self.plotController.getRange()
        x_range = axis_range[0]
        y_range = axis_range[1]
        
        positions, intensities, baseline = \
           self.phase_model.get_rescaled_reflections(
                -1, 'pattern_placeholder_var',
                x_range, y_range)

        self.pattern_widget.add_phase(self.phase_model.phases[-1].name,
                                      positions,
                                      intensities,
                                      baseline,
                                      self.phase_model.phase_colors[-1])

    def update_phase_lines(self, ind, axis_range=None):
        """
        Updates the intensities of a specific phase with index ind.
        :param ind: Index of the phase
        :param axis_range: list/tuple of visible x_range and y_range -- ((x_min, x_max), (y_min, y_max))
        """
        if axis_range is None:
            axis_range = self.plotController.getRange()

        x_range = axis_range[0]
        y_range = axis_range[1]
        
        
        positions, intensities, baseline = self.phase_model.get_rescaled_reflections(
            ind, 'pattern_placeholder_var',
            x_range, y_range
        )

        self.pattern_widget.update_phase_intensities(ind, positions, intensities, y_range[0])

    def update_all_phase_lines(self):
        for ind in range(len(self.phase_model.phases)):
            self.update_phase_lines(ind)

    def pattern_data_changed(self):
        """
        Function is called after the pattern data has changed.
        """
        self.pattern_widget.update_phase_line_visibilities()

    def update_phase_legend(self, ind):
        name = self.phase_model.phases[ind].name
        parameter_str = ''
        vp = self.phase_model.phases[ind].params['vp']
        vs = self.phase_model.phases[ind].params['vs']
        d = self.phase_model.phases[ind].params['d']
        parameter_str += u'V<sub>P</sub> {:0.2f} m/s, '.format(vp)
        parameter_str += u'V<sub>S</sub> {:0.2f} m/s, '.format(vs)
        parameter_str += 'd {:0.4f} mm'.format(d)
        self.pattern_widget.rename_phase(ind, name + ': ' + parameter_str )

    def update_phase_color(self, ind):
        self.pattern_widget.set_phase_color(ind, self.phase_model.phase_colors[ind])

    def update_phase_visible(self, ind):
        if self.phase_model.phase_visible[ind]:
            self.pattern_widget.show_phase(ind)
        else:
            self.pattern_widget.hide_phase(ind)

    def reflection_added(self, ind):
        self.pattern_widget.phases[ind].add_line()
        self.update_phase_lines(ind)

    def reflection_deleted(self, phase_ind, reflection_ind):
        self.pattern_widget.phases[phase_ind].remove_line(reflection_ind)
