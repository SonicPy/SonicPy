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



import numpy as np

from PyQt5 import QtCore
from models.vpvs import vpvs

from utilities.HelperModule import calculate_color


class PhaseLoadError(Exception):
    def __init__(self, filename):
        super(PhaseLoadError, self).__init__()
        self.filename = filename

    def __repr__(self):
        return "Could not load {0} as vpvs file".format(self.filename)


class PhaseModel(QtCore.QObject):
    phase_added = QtCore.Signal()
    phase_removed = QtCore.Signal(int)  # phase ind
    phase_changed = QtCore.Signal(int)  # phase ind
    phase_reloaded = QtCore.Signal(int)  # phase ind

    reflection_added = QtCore.Signal(int)
    reflection_deleted = QtCore.Signal(int, int)  # phase index, reflection index

    num_phases = 0

    def __init__(self):
        super().__init__()
        self.phases = []
        self.reflections = []
        self.phase_files = []
        self.phase_colors = []
        self.phase_visible = []

        self.same_conditions = True

    def send_added_signal(self):
        self.phase_added.emit()

    def add_vpvs(self, filename):
        """
        Adds a vpvs file
        :param filename: filename of the vpvs file
        """
        try:
            vpvs_object = vpvs()
            vpvs_object.load_file(filename)
            self.phase_files.append(filename)
            self.add_vpvs_object(vpvs_object)
        except (ZeroDivisionError, UnboundLocalError, ValueError):
            raise PhaseLoadError(filename)


    def add_vpvs_object(self, vpvs_object):
        """
        Adds a vpvs object to the phase list.
        :param vpvs_object: vpvs object
        :type vpvs_object: vpvs
        """
        self.phases.append(vpvs_object)
        self.reflections.append([])
        self.phase_colors.append(calculate_color(PhaseModel.num_phases + 9))
        self.phase_visible.append(True)
        PhaseModel.num_phases += 1
        if self.same_conditions and len(self.phases) > 2:
            self.phases[-1].compute_d(self.phases[-2].params['pressure'], self.phases[-2].params['temperature'])
        else:
            self.phases[-1].compute_d()
        self.get_lines_d(-1)
        self.phase_added.emit()
        self.phase_changed.emit(len(self.phases) - 1)

    def save_phase_as(self, ind, filename):
        """
        Save the phase specified with ind as a vpvs file.
        """
        self.phases[ind].save_file(filename)
        self.phase_changed.emit(ind)
    
    def del_phase(self, ind):
        """
        Deletes the a phase with index ind from the phase list
        """
        del self.phases[ind]
        del self.reflections[ind]
        del self.phase_files[ind]
        del self.phase_colors[ind]
        del self.phase_visible[ind]
        self.phase_removed.emit(ind)

    def reload(self, ind):
        """
        Reloads a phase specified by index ind from it's original source filename
        """
        self.clear_reflections(ind)
        self.phases[ind].reload_file()
        for _ in range(len(self.phases[ind].reflections)):
            self.reflection_added.emit(ind)
        self.get_lines_d(ind)
        self.phase_changed.emit(ind)

    def set_pressure(self, ind, pressure):
        """
        Sets the pressure of a phase with index ind. In case same_conditions is true, all phase pressures will be
        updated.
        """
        if self.same_conditions:
            for j in range(len(self.phases)):
                self._set_pressure(j, pressure)
                self.phase_changed.emit(j)
        else:
            self._set_pressure(ind, pressure)
            self.phase_changed.emit(ind)

    def _set_pressure(self, ind, pressure):
        self.phases[ind].compute_d(pressure=pressure)
        self.get_lines_d(ind)

    def set_temperature(self, ind, temperature):
        """
        Sets the temperature of a phase with index ind. In case same_conditions is true, all phase temperatures will be
        updated.
        """
        if self.same_conditions:
            for j in range(len(self.phases)):
                self._set_temperature(j, temperature)
                self.phase_changed.emit(j)
        else:
            self._set_temperature(ind, temperature)
            self.phase_changed.emit(ind)

    def _set_temperature(self, ind, temperature):
        if self.phases[ind].has_thermal_expansion():
            self.phases[ind].compute_d(temperature=temperature)
            self.get_lines_d(ind)

    def set_pressure_temperature(self, ind, pressure, temperature):
        self.phases[ind].compute_d(temperature=temperature, pressure=pressure)
        self.get_lines_d(ind)
        self.phase_changed.emit(ind)

    def set_pressure_all(self, P):
        for phase in self.phases:
            phase.compute_d(pressure=P)

    

    def set_param(self, ind, param, value):
        """
        Sets one of the vpvs parameters for the phase with index ind to a certain value. Automatically emits the
        phase_changed signal.
        """

        self.phases[ind].params[param] = value
        self.phases[ind].compute_v0()
        self.phases[ind].compute_d0()
        self.phases[ind].compute_d()
        self.get_lines_d(ind)
        self.phase_changed.emit(ind)

    def set_color(self, ind, color):
        """
        Changes the color of the phase with index ind.
        :param ind: index of phase
        :param color: tuple with RGB values (0-255)
        """
        self.phase_colors[ind] = color
        self.phase_changed.emit(ind)

    def set_phase_visible(self, ind, bool):
        """
        Sets the visible flag (bool) for phase with index ind.
        """
        self.phase_visible[ind] = bool
        self.phase_changed.emit(ind)

    def get_lines_d(self, ind):
        reflections = self.phases[ind].get_reflections()
        res = np.zeros((len(reflections), 5))
        for i, reflection in enumerate(reflections):
            res[i, 0] = reflection.d
            res[i, 1] = reflection.intensity
            res[i, 2] = reflection.h
            res[i, 3] = reflection.k
            res[i, 4] = reflection.l
        self.reflections[ind] = res
        return res

    def set_temperature_all(self, T):
        for phase in self.phases:
            phase.compute_d(temperature=T)

    def update_all_phases(self):
        for ind in range(len(self.phases)):
            self.get_lines_d(ind)

    # need to modify this for EDXD mode
    def get_phase_line_positions(self, ind):
        positions = self.reflections[ind][:, 0]

        return positions
        

    def get_phase_line_intensities(self, ind, positions, pattern, x_range, y_range):
        
        max_pattern_intensity = y_range[1]

        baseline = 1
        phase_line_intensities = self.reflections[ind][:, 1]
        # search for reflections within current pattern view range
        phase_line_intensities_in_range = phase_line_intensities[(positions > x_range[0]) & (positions < x_range[1])]

        # rescale intensity based on the lines visible
        if len(phase_line_intensities_in_range):
            scale_factor = (max_pattern_intensity - baseline) / \
                           np.max(phase_line_intensities_in_range)
        else:
            scale_factor = 1
        if scale_factor <= 0:
            scale_factor = 0.01

        phase_line_intensities = scale_factor * self.reflections[ind][:, 1] + baseline
        return phase_line_intensities, baseline

    def get_rescaled_reflections(self, ind, pattern, x_range,
                                 y_range):
        positions = self.get_phase_line_positions(ind)
        intensities, baseline = self.get_phase_line_intensities(ind, positions, pattern, x_range, y_range)
        return positions, intensities, baseline

    
    def add_reflection(self, ind):
        """
        Adds an empty reflection to the reflection table of a phase with index ind
        """
        self.phases[ind].add_reflection()
        self.get_lines_d(ind)
        self.reflection_added.emit(ind)

    def delete_reflection(self, phase_ind, reflection_ind):
        """
        Deletes a reflection from a phase with index phase index.
        """
        reflection_ind = int(reflection_ind)
        self.phases[phase_ind].delete_reflection(reflection_ind)
        self.get_lines_d(phase_ind)
        self.reflection_deleted.emit(phase_ind, reflection_ind)
        self.phase_changed.emit(phase_ind)

    def delete_multiple_reflections(self, phase_ind, indices):
        """
        Deletes multiple reflection from a phase with index phase index.
        """
        indices = np.array(sorted(indices))
        for reflection_ind in indices:
            self.delete_reflection(phase_ind, reflection_ind)
            indices -= 1

    def clear_reflections(self, phase_ind):
        """
        Deletes all reflections from a phase with index phase_ind
        """
        for ind in range(len(self.phases[phase_ind].reflections)):
            self.delete_reflection(phase_ind, 0)

    def update_reflection(self, phase_ind, reflection_ind, reflection):
        """
        Updates the reflection of a phase with a new vpvs_reflection
        :param phase_ind: index of the phase
        :param reflection_ind: index of the refection
        :param reflection: updated reflection
        :type reflection: vpvs_reflection
        """
        self.phases[phase_ind].reflections[reflection_ind] = reflection
        self.phases[phase_ind].params['modified'] = True
        self.phases[phase_ind].compute_d0()
        self.phases[phase_ind].compute_d()
        self.get_lines_d(phase_ind)
        self.phase_changed.emit(phase_ind)    

    def reset(self):
        """
        Deletes all phases within the phase model.
        """
        for ind in range(len(self.phases)):
            self.del_phase(0)


    