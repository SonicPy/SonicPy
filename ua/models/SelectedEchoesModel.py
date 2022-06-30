import numpy as np

import time

class SelectedEchoesModel( ):
    ''' 
    model for storing selected and analyzed echoes
    echoes can be used for plotting correlation times vs inverse frequency
    as well as for savign to a project 
     '''

    def __init__(self ):
        
        self.echoes = []
        
       
     

    def add_echo(self, echo ):
        
        self.echoes.append(echo)