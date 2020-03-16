import visa, time, logging, os, struct, sys
from PyTektronixScope import TektronixScope

visa_hostname='hpcat143'
rm = visa.ResourceManager()
resources = rm.list_resources()
r = None
for r in resources:
    if visa_hostname in r:
        break
if r is not None:
    # pyvisa code:
    instrument = rm.open_resource(r)
    ID = instrument.ask('*IDN?')
    print(ID)

DPO5000 = TektronixScope(instrument)    
    

DPO5000.set_vertical_scale(1)
DPO5000.set_aquisition_type(20)
DPO5000.select_channel(1)
sel = DPO5000.is_channel_selected(1)
print('CH1 ON: ' + str(sel))
DPO5000.start_acq()
DPO5000.stop_acq()
x, y = DPO5000.read_data_one_channel('CH1',data_start=1, data_stop=100000,x_axis_out=True)
print ('datapoints acquired: ' + str(len(y)))



    
    