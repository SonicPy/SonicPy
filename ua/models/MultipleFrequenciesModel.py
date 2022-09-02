
import os.path, sys, os
from functools import partial
from ua.models.EchoesResultsModel import EchoesResultsModel

class MultipleFrequenciesModel():
    def __init__(self, results_model: EchoesResultsModel):

        self.results_model = results_model
        self.cond = None
        self.files = {}
        self.fbase = None
        self.fname = ""

        self.f_min_sweep = None
        self.f_max_sweep = None

        self.f_min_broadband = 15
        self.f_max_broadband = 70
        self.step_broadband = 2

    def set_condition(self, cond):
        self.cond = cond

    def set_files(self, files):
        self.files = files

    def set_fbase(self, fbase):
        self.fbase = fbase
    
    def set_fname(self, fname):
        self.fname = fname

    def set_f_min_sweep(self, f_min):
        self.f_min_sweep = f_min

    def set_f_max_sweep(self, f_max):
        self.f_max_sweep = f_max

    def set_f_min_broadband(self, f_min):
        self.f_min_broadband = f_min

    def set_f_max_broadband(self, f_max):
        self.f_max_broadband = f_max

    def set_step_broadband(self, step):
        self.step_broadband = step