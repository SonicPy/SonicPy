import imp
import numpy as np
from . SelectedEchoesModel import SelectedEchoesModel

import time

class ProjectModel( ):
    ''' model for saving and restoring projects '''

    def __init__(self ):
        
        self.echoes  = SelectedEchoesModel()
        self.settings = {
                            'f_start'       :20,
                            'f_step'        :2,
                            'f_filter_order':3,
                            'tukey_alpha'   :0.2,
                            'freq_range'    :0.1,
                            'us_folder'     :'',
                            'output_folder' :''
                        }
       
        

    def _set_setting(self, setting, value ):
        
        self.settings[setting] = value