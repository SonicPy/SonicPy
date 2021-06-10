from math import trunc
import epics
import time

pvname = "16bmb:mca_file:FullFileName_RBV"

pv = epics.PV(pvname)




pv.put("fu")
time.sleep(1)
char_val = pv.get(as_string=True)

print(char_val)