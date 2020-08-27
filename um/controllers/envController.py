

from um.models.epicsModel import epicsModel

class envController():

    def __init__(self, isMain = False, offline = False):
        
        self.epics_model = epicsModel()
        if not offline:
            self.epics_model.connect_pvs()