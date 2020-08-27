
from epics import caput, caget, PV
from epics.utils import BYTES2STR
import numpy as np
#from epics.clibs import *
import copy
import time
import os
from .. import env_path

class epicsModel():
    """
    Creates a new epicsMca.

    Inputs:
        record_Name:
        The name of the EPICS MCA record for the MCA object being created, without
        a trailing period or field name.
        
    Keywords:
        environment_file:
        This keyword can be used to specify the name of a file which
        contains the names of EPICS process variables which should be saved
        in the header of files written with Mca.write_file().
        If this keyword is not specified then this function will attempt the
        following:
            - If the system environment variable MCA_ENVIRONMENT is set then
                it will attempt to open that file
            - If this fails, it will attempt to open a file called
                'catch1d.env' in the current directory.
                This is done to be compatible with the data catcher program.
        This is an ASCII file with each line containing a process variable
        name, followed by a space and a description field.

    Example:
    >>> from epicsMca import *
    >>> mca = epicsMca('13IDC:mca1')
    >>> print mca.data
    """
    def __init__(self):
        
        # Construct the names of the PVs for the environment
        
        self.environment_file = env_path
        
        self.env_pvs = []  
        self.environment = []


    def connect_pvs(self):

       
        if os.path.exists(self.environment_file):
            self.read_environment_file(self.environment_file)
            for env in self.environment:
                self.env_pvs.append(PV(env.name))
        print (self.env_pvs)


    def get_environment(self):
        """
        Reads the current values of the environment PVs.  Returns a list of
        McaEnvironment objects with Mca.get_environment().
        """
        try:
            if (len(self.env_pvs) > 0):
                
                for i in range(len(self.environment)):
                    pv = self.env_pvs[i]
                    val = pv.get()
                    if type(val) == float:
                        val = round(val,12) # python rounding bug workaround
                    self.environment[i].value = val
        except:
            pass
        #env = super().get_environment()
        env = self.environment
        return env


    def write_ascii(self, filename, environment):
        """
            environment:
                A list of epicsEnvironment objects.
        """

        fp = open(filename, 'w')

        for e in environment:
            fp.write('ENVIRONMENT: '       + str(e.name) +
                                    '="'  + str(e.value) +
                                    '" (' + str(e.description) + ')\n')

        fp.close()


    def read_ascii_file(self, filename):

        try:
            fp = open(filename, 'r')
        except:
            return [None, False]

        try:

            while(1):
                line = fp.readline()
                if (line == ''): break
                pos = line.find(' ')
                if (pos == -1): pos = len(line)
                tag = line[0:pos]
                value = line[pos:].strip()
                values = value.split()

                if (tag == 'ENVIRONMENT:'):
                    env = McaEnvironment()
                    p1 = value.find('=')
                    env.name = value[0:p1]
                    p2 = value[p1+2:].find('"')
                    env.value = value[p1+2: p1+2+p2]
                    env.description = value[p1+2+p2+3:-1]
                    environment.append(env)

            r = {}
       
            r['environment'] = environment
            return [r, True]
        except:
            return [None, False]

    def read_environment_file(self, file):
        """
        Reads a file containing the "environment" PVs.  The values and desriptions of these
        PVs are stored in the data files written by Mca.write_file().

        Inputs:
            file:
                The name of the file containing the environment PVs. This is an ASCII file
                with each line containing a process variable name, followed by a
                space and a description field.
        """
        self.environment = []
        try:
            fp = open(file, 'r')
            lines = fp.readlines()
            fp.close()
        except:
            return
        for line in lines:
            env = epicsEnvironment()
            pos = line.find(' ')
            if (pos != -1):
                env.name = line[0:pos]
                env.description = line[pos+1:].strip()
            else:
                env.name = line.strip()
                env.description = ' '
            self.environment.append(env)



class epicsEnvironment():
    """
    The "environment" or related parameters for an eperiment.  These might include
    things like motor positions, temperature, anything that describes the
    experiment.

    An experiment object has an associated list of epicsEnvironment objects, since there
    are typically many such parameters required to describe an experiment.

    Fields:
        .name         # A string name of this parameter, e.g. "13IDD:m1"
        .value        # A string value of this parameter,  e.g. "14.223"
        .description  # A string description of this parameter, e.g. "X stage"
    """
    def __init__(self, name='', value='', description=''):
        self.name = name
        self.value = value
        self.description = description