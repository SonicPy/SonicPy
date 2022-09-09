
import os.path, sys, os
from functools import partial
from ua.models.EchoesResultsModel import EchoesResultsModel

class OutputModel():
    def __init__(self, results_model: EchoesResultsModel):

        self.results_model = results_model
 

    