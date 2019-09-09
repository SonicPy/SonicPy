#-------------------------------------------------------------------------------
#  Get a screen catpure from DPO4000 series scope and save it to a file

# python        2.7         (http://www.python.org/)
# pyvisa        1.4         (http://pyvisa.sourceforge.net/)
# numpy         1.6.2       (http://numpy.scipy.org/)
# MatPlotLib    1.0.1       (http://matplotlib.sourceforge.net/)
#-------------------------------------------------------------------------------

import visa
import numpy as np
from struct import unpack
import pylab

rm = visa.ResourceManager()
resources = rm.list_resources()
visa_resource_name = resources[0]
scope = rm.open_resource(visa_resource_name)


scope.write('DATA:SOU CH1')
scope.write('DATA:start 1')
scope.write('DATA:stop 100000')
scope.write('DATA:WIDTH 2')
scope.write('DATA:ENC SRI')


ymult = float(scope.ask('WFMPRE:YMULT?'))
yzero = float(scope.ask('WFMPRE:YZERO?'))
yoff = float(scope.ask('WFMPRE:YOFF?'))
xincr = float(scope.ask('WFMPRE:XINCR?'))


scope.write('CURVE?')
data = scope.read_raw()
headerlen = 8
header = data[:headerlen]
ADC_wave = data[headerlen:-1]

ADC_wave = np.fromstring(ADC_wave, dtype=np.int16)

Volts = (ADC_wave - yoff) * ymult  + yzero

Time = np.arange(0, xincr * len(Volts), xincr)

pylab.plot(Time, Volts)
pylab.show()
