from math import trunc
import epics
import time

pvname = "16bmb:scope_file:FullFileName_RBV"

pv = epics.PV(pvname)

pvname2 = "16bmb:scope_file:WriteMessage"

pv2 = epics.PV(pvname2)


#pv.put("fu")
#time.sleep(1)
char_val = pv.get(as_string=True)
char_val2 = pv2.get(as_string=True)

print(char_val)
print(char_val2)