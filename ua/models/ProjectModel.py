import imp
import numpy as np
from . SelectedEchoesModel import SelectedEchoesModel

import time

class ProjectModel( ):
    ''' model for saving and restoring projects '''

    def __init__(self ):
        
        self.echoes  = SelectedEchoesModel()
        self.settings = {}
       
     

    def _set_setting(self, setting, value ):
        
        self.settings[setting] = value