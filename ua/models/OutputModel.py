
import os.path, sys, os
from functools import partial
from ua.models.EchoesResultsModel import EchoesResultsModel

class OutputModel():
    def __init__(self, results_model: EchoesResultsModel):

        self.results_model = results_model
 
        self.conds = []

    def clear(self):
        self.__init__(self.results_model)

    def reset(self):
        self.__init__(self.results_model)

    def set_conds(self,conds):
        self.conds = conds
    
    def get_conds(self):
        return self.conds
    
    def cond_to_ind(self, cond):

        return self.conds.index(cond)