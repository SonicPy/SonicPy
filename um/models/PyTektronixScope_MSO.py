# encoding=utf8  

from time import *
import numbers
import numpy as np
import sys
import pyvisa as visa


class TektronixScopeError(Exception):
    """Exception raised from the TektronixScope class

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, mesg):
        self.mesg = mesg
    def __repr__(self):
        return self.mesg
    def __str__(self):
        return self.mesg



class TektronixScope(object):
    """Drive a TektronixScope instrument

    usage:
        scope = TektronixScope(instrument_resource_name)
        X,Y = scope.read_data_one_channel('CH2', t0 = 0, DeltaT = 1E-6, 
                                                            x_axis_out=True)

    Only a few functions are available, and the scope should
    be configured manually. Direct acces to the instrument can
    be made as any Visa Instrument :  scope.ask('*IDN?')
    """    
    def __init__(self, hostname):
        """ Initialise the Scope

        argument : 
            hostname : should be a string 

        """
        
        
        self.hostname = hostname
        self.booster = False

        self.offset = 0
        self.scale = 0
        self.yzero = 0
        self.num_acq = 0
        self.connected = False
        '''
        if not hasattr(instrument, 'write'): 
            if isinstance(instrument, str):
                if visa is not None:
                    rm = visa.ResourceManager()
                    inst = rm.open_resource(inst)
                else:
                    raise Exception('Visa is not install on your system')
            else:
                raise ValueError('First argument should be a string or an instrument')
        '''
        

    def connect(self):
        try:
            hostname = self.hostname
            self.disconnect()
            rm = visa.ResourceManager()
            resources = rm.list_resources()
            #print(resources)
            r = None
            for r in resources:
                if hostname in r:
                    break
            if r is not None:
                # pyvisa code:
                instrument = rm.open_resource(r)
                
                ID = instrument.query('*IDN?')
                #print(ID)
                if ID is not None:
                    if len(ID):
                        tokens = ID.split(',')
                        ID = tokens[1]
                self.instrument = ID
                self._inst = instrument
                self.connected = True
                print(instrument, ' connected')
                
                return True
            else:
                return False
        except:
            
            return False

    def disconnect(self):
        if self.connected:
            try:
                if self._inst is not None:
                    self._inst.close()
                    self._inst = None
                    self.connected = False
                    #print('disconnected')
            except:
                pass
        

    def write(self, cmd):
        #print(cmd)
        if self.connected:
            return self._inst.write(cmd)
        else:
            return None

    def ask(self, cmd):
        #print(cmd)
        if self.connected:
            return self._inst.query(cmd)
        else:
            return None

    def ask_raw(self, cmd):
        #print(cmd)
        if self.connected:
            
            c = str(cmd)
            if hasattr(self._inst, 'ask_raw'):

                return self._inst.query(c)[:-1]
            else:
                self._inst.write(cmd)

                return self._inst.read_raw()
        else:
            return None


###################################
## Method ordered by groups 
###################################

#Acquisition Command Group 

    def clear(self):
        self.write('CLEAR ALL')

    def start_acq(self):
        """Start acquisition"""
        self.write('ACQ:STATE RUN')

    def stop_acq(self):
        """Stop acquisition"""
        self.write('ACQ:STATE STOP')

    def number_acquired(self):
        """
        This query-only command returns the number 
        of waveform acquisitions that have occurred 
        since starting acquisition with the ACQuire:STATE RUN command. 
        This value is reset to zero when any acquisition, horizontal, 
        or vertical arguments that affect the waveform are changed. 
        The maximum number of acquisitions that can be counted is 230–1. 
        The instrument stops counting when this number is reached. 
        This is the same value that displays in the lower right of the screen.
        """
        num_acq = self.ask('ACQuire:NUMACq?')
        return num_acq

    def close(self):
        self._inst.clear()
        self._inst.close()

    def get_state(self):
        """Gets current acquisition state"""
        ans =  self.ask('ACQ:STATE?')
        ans = int(ans)
        return ans

    def set_num_av(self, num_av):
        command = 'ACQ:NUMAV %d;'%(int(num_av))
        self.write(command)

    def get_num_av(self):
        command = 'ACQ:NUMAV?'
        num_av = int(self.ask(command))
        return num_av

    def set_aquisition_type(self, acq_type='average'):
        '''
        possible acq_types are:
        sample, peak, hires, envelope, average
        '''
        command = None
        if acq_type == 'sample':
            command = 'ACQ:MOD SAM'        
        if acq_type == 'peak':
            command = 'ACQ:MOD PEAK'
        if acq_type == 'hires':
            command = 'ACQ:MOD HIR'
        if acq_type == 'envelope':
            command = 'ACQ:MOD ENV'
        if acq_type == 'average':
            command = 'ACQ:MOD AVE'
            
        if command is not None:
            self.write(command)

    def get_aquisition_type(self):
        command = 'ACQ:MOD?'        
        ans = self.ask(command)
        #print(ans)
        types = ['sample', 'peak', 'hires', 'envelope', 'average']
        for t in types:
            if t in ans[:-1].lower():
                return t
        return 'other'
        
        
        
        

#Alias Command Group

#Bus Command Group

#Calibration and Diagnostic Command Group

#Cursor Command Group

#Display Command Group

#Ethernet Command Group

#File System Command Group

#Hard Copy Command Group

#Horizontal Command Group
    def get_horizontal_scale(self):
        return float(self.ask("HORizontal:SCAle?"))

    def set_horizontal_scale(self, val):
        return self.write("HORizontal:SCAle {val}".format(val=val))


#Mark Command Group

#Math Command Group

#Measurement Command Group

#Miscellaneous Command Group

    def get_ID(self):
        return self.ask('*IDN?')

    def load_setup(self):
        l = self.ask('SET?')
        lst = [e.split(' ', 1) for e in l.split(';')[1:]]
        
        dico = {}
        for item in lst:
            if len(item)== 2:

                dico[item[0]]=item[1]
        self.dico = dico

    def get_setup_dict(self, force_load=False):
        """Return the dictionnary of the setup 
        
        By default, the method does not load the setup from the instrument
        unless it has not been loaded before or force_load is set to true.
        """
        if not hasattr(self, 'dico') or force_load:
            self.load_setup()
        return self.dico

    def get_setup(self, name, force_load=False):
        """Return the setup named 'name' 
        
        By default, the method does not load the setup from the instrument
        unless it has not been loaded before or force_load is set to true.
        """
        if not hasattr(self, 'dico') or force_load:
            self.load_setup()
        return self.dico[name]

    def number_of_channel(self):
        """Return the number of available channel on the scope (4 or 2)"""
        if ':CH4:LABEL:NAME' in self.get_setup_dict().keys():
            return 4
        else:
            return 2

    #Save and Recall Command Group

    #Search Command Group

    #Status and Error Command Group

    #Trigger Command Group

    #Vertical Command Group
    def channel_name(self, name):
        """Return and check the channel name
        
        Return the channel CHi from either a number i, or a string 'i', 'CHi'
        
        input : name is a number or a string
        Raise an error if the channel requested if not available 
        """
        n_max = self.number_of_channel()
        channel_list = ['CH%i'%(i+1) for i in range(n_max)]
        channel_listb = ['%i'%(i+1) for i in range(n_max)]
        if isinstance(name, numbers.Number):
            if name > n_max:
                raise TektronixScopeError("Request channel %i while channel \
                                    number should be between %i and %i"%(name, 1, n_max))
            return 'CH%i'%name
        elif name in channel_list:
            return name
        elif name in channel_listb:
            return 'CH'+name
        else:
            raise TektronixScopeError("Request channel %s while channel \
                                    should be in %s"%(str(name), ' '.join(channel_list)))

    def is_channel_selected(self, channel):
        command = 'SEL:%s?'%(self.channel_name(channel))
        ans = self.ask(command)
        ch_sel = ans=='1\n'
        return ch_sel

    def select_channel(self, channel):
        command = 'SEL:%s ON;'%(self.channel_name(channel))
        
        self.write(command)
        ##self.booster = False

    def turn_off_channel(self, channel):
        command = 'SEL:%s OFF;'%(self.channel_name(channel))
        
        self.write(command)

    def get_channel_offset(self, channel):
        return float(self.ask('%s:OFFS?'%self.channel_name(channel)))

    def get_channel_position(self, channel):
        return float(self.ask('%s:POS?'%self.channel_name(channel)))

    def get_vertical_scale(self, channel):
        return float(self.ask('%s:SCA?'%self.channel_name(channel)))

    def set_vertical_scale(self, channel=1, scale=10.0):
        write_str='%s:SCA %.6f;'%(self.channel_name(channel),scale)
        self.write(write_str)
        self.booster = False

    def set_impedance(self, channel, value):
        """Sets the input impedance of the channel"""
        liste_string = ['FIF', 'FIFty','SEVENTYF','SEVENTYFive','MEG','50','75','1.00E+06']
        liste_value = [50, 75, 1.00E6]
        if isinstance(value, str) or isinstance(value, unicode):
            if value.lower() not in map(lambda a:a.lower(),liste_string):
                raise TektronixScopeError("Impedance is %s. It should be in %s"%liste_string)
        elif isinstance(value, numbers.Number):
            if value not in liste_value:
                raise TektronixScopeError("Impedance is %s. It should be in %s"%liste_value)
            else:
                value = str(value) if value<100 else '1.00E+06'
        else:
            raise TektronixScopeError("Impedance is %s. It should be in %s"%liste_string)
        self.write("%s:IMPedance %s"%(self.channel_name(channel), value))
    def get_impedance(self, channel):
        """Returns the input impedance of the channel"""
        return self.ask('%s:IMPedance?'%self.channel_name(channel))

    def set_coupling(self, channel, value):
        """Sets the input coupling of the channel"""
        liste_string = ['AC','DC','GND']
        if isinstance(value, str) or isinstance(value, unicode):
            if value.lower() not in map(lambda a:a.lower(),liste_string):
                raise TektronixScopeError("Coupling is %s. It should be in %s"%liste_string)
        else:
            raise TektronixScopeError("Coupling is %s. It should be in %s"%liste_string)
        self.write("%s:COUPling %s"%(self.channel_name(channel), value))
    def get_coupling(self, channel):
        """Returns the input coupling of the channel"""
        return self.ask('%s:COUPling?'%self.channel_name(channel))



    # Waveform Transfer Command Group
    def set_data_source(self, name):
        name = self.channel_name(name)
        self.write('DAT:SOUR '+str(name))
        self.booster = False

    def get_data_source(self):
        
        ch = self.ask('DAT:SOUR?')[:-1].upper()
        return ch

    def set_data_start(self, data_start):
        """Set the first data points of the waveform record
        If data_start is None: data_start=1
        """
        if data_start is None:
            data_start = 1
        data_start = int(data_start)
        self.write('data:start %i'%data_start)
        self.booster = False

    def get_data_start(self):
        return int(self.ask('data:start?'))

    def get_horizontal_record_length(self):
        return int(self.ask("horizontal:recordlength?"))

    def set_horizontal_record_length(self, val):
        self.write('HORizontal:RECOrdlength %s'%str(val))

    def set_data_stop(self, data_stop):
        """Set the last data points of the waveform record
        If data_stop is None: data_stop= horizontal record length
        """
        if data_stop is None:
            data_stop = self.get_horizontal_record_length()
        self.write('DATA:STOP %i'%data_stop)
        self.booster = False

    def get_data_stop(self):
        return int(self.ask('DATA:STOP?'))

    def get_out_waveform_horizontal_sampling_interval(self):
        return float(self.ask('WFMO:XIN?'))

    def get_out_waveform_horizontal_zero(self):
        return float(self.ask('WFMO:XZERO?'))

    def get_out_waveform_vertical_scale_factor(self):
        return float(self.ask('WFMO:YMUlt?'))

    def get_out_waveform_vertical_position(self):
        return float(self.ask('WFMO:YOFf?'))

    def read_data_one_channel(self, channel=None, data_start=None, 
                              data_stop=None, x_axis_out=False,
                              t0=None, DeltaT = None):
        """Read waveform from the specified channel
        
        channel : name of the channel (i, 'i', 'chi'). If None, keep
            the previous channel
        data_start : position of the first point in the waveform
        data_stop : position of the last point in the waveform
        x_axis_out : if true, the function returns (X,Y)
                    if false, the function returns Y (default)
        t0 : initial position time in the waveform
        DeltaT : duration of the acquired waveform
            t0, DeltaT and data_start, data_stop are mutually exculsive 
        booster : if set to True, accelerate the acquisition by assuming
            that all the parameters are not change from the previous
            acquisition. If parameters were changed, then the output may
            be different than what is expected. The channel is the only
            parameter that is checked when booster is enable
        
        """
        # set booster to false if it the fist time the method is called
        # We could decide to automaticaly see if parameters of the method
        # are change to set booster to false. However, one cannot
        # detect if the setting of the scope are change
        # To be safe, booster is set to False by default.  
        booster = self.booster

        scope = self._inst
       
        
        
        scope.write("HEADER 0")
        scope.write("DATA:SOUR CH1")
        scope.write("DAT:ENC SRI")   # Signed Binary Format, LSB order
        scope.write("DAT:WIDTH 1")

        scope.write("DAT:START 1")
        scope.write("DAT:STOP 1e10") # Set data stop to max
        recordLength = int(scope.query("WFMO:NR_P?"))  # Query how many points are actually available
        scope.write("DAT:STOP {0}".format(recordLength)) # Set data stop to match points available

        # Fetch horizontal scaling factors
        xinc = float(scope.query("WFMO:XINCR?"))
        xzero = float(scope.query("WFMO:XZERO?"))
        pt_off = int(scope.query("WFMO:PT_OFF?"))

        # Fetch vertical scaling factors
        ymult = float(scope.query("WFMO:YMULT?"))
        yzero = float(scope.query("WFMO:YZERO?"))
        yoff = float(scope.query("WFMO:YOFF?"))
        
        #buffer = self.ask_raw('CURVe?')
        # Fetch waveform data
        self._inst.write("curve?")

        # Data is sent back with ieee defined header.  ie. #41000<binary data bytes>\n
        # PyVISA read_binary_values() method will automatically read and parse the ieee block header so you don't have to.
        rawData = self._inst.read_binary_values(datatype='b', is_big_endian=False, container=np.ndarray, header_fmt='ieee', expect_termination=True)
        dataLen = len(rawData)

        # Create numpy arrays of floating point values for the X and Y axis
        t0 = (-pt_off * xinc) + xzero
        xvalues = np.ndarray(dataLen, float)
        yvalues = np.ndarray(dataLen, float)
        for i in range(0,dataLen):
            xvalues[i] = t0 + xinc * i # Create timestamp for the data point
            yvalues[i] = float(rawData[i] - yoff) * ymult + yzero # Convert raw ADC value into a floating point value


        if x_axis_out:
            return xvalues, yvalues
        else:
            return yvalues

    #Zoom Command Group

                   

# unit test:
# should print the device ID and number of point in returned waveform (100000)

def main():
    hostname = '54'
    rm = visa.ResourceManager()
    resources = rm.list_resources()
    #print(resources)
    r = None
    for r in resources:
        if hostname in r:
            break
    if r is not None:
        # pyvisa code:
        instrument = rm.open_resource(r)
        ID = instrument.query('*IDN?')
        #print(ID)
        
        DPO5000 = TektronixScope(hostname)
        DPO5000.connect()
        ADC_wave = DPO5000.read_data_one_channel('CH1',1,100000)

        count_y = ADC_wave.size
        print(count_y)

if __name__ == '__main__':
    main()