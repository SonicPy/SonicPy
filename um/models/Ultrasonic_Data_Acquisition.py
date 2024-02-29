"""
Python procedure to acquire ultrasonic data using an arbitrary function generator and an oscilloscope at given load and temperature conditions.

Author: Zhicheng Jing
Date: 11/15/2017

Frequencies of the signals to be collected: 20MHz, 25MHz, 30MHz, 40MHz, 50MHz, 60MHz
One or two cycles of sine waves are used depending on frequency.

Using PyVISA, TekVISA needs to be installed.
Use OpenChoice Instrument Manager to seach oscilloscope and arbitrary waveform generator first.
"""
import visa
import time

t0 = time.clock()
rm = visa.ResourceManager()

"""
Enter Instruments addresses below.
"""
print()
mso = rm.open_resource('TCPIP::164.54.160.209::INSTR')
print(mso.query("*IDN?"))
afg = rm.open_resource('TCPIP::164.54.160.214::INSTR')
print(afg.query("*IDN?"))

"""
Function to ask the AFG to send waveform signals with defined frequency, Vpp, and cycles.
"""
def Sending_Signal(FreqM,Vpp,NCycles):
    afg.write(":output1:state off")
    afg.write(":source1:burst:ncycles 1")
    if(NCycles==2):
        afg.write(":source1:function:shape user1")
        afg.write(":source1:frequency {}".format(FreqM*1.0e6/2.0))
    else:
        afg.write(":source1:function:shape sin")
        afg.write(":source1:frequency {}".format(FreqM*1.0e6))
    afg.write(":source1:voltage {}".format(Vpp))
    afg.write(":source1:phase 0.0e0")
    afg.write(":source1:voltage:offset 0.0e0")
    afg.write(":output1:state on")
    print()
    print('Sending ',NCycles,'cylce(s)',int(FreqM),'MHz signal with Vpp =',Vpp,"V.")

"""
Function to ask the MSO to take acquisition of a single sequence of 1000 waveforms and save the averaged waveform to a specified file location.
"""

def Taking_Signal(FreqM,Run_Number,Load,Temp):
    mso.write(":acquire:state stop")
    mso.write("acquire:stopafter sequence")
    mso.write(":acquire:state run")
    while(mso.query_ascii_values(':acquire:state?',converter='b')[0]==1):
        time.sleep(1.0)
    time.sleep(2.0)
    mso.write(":save:waveform:fileformat auto")
    mso.write(":save:waveform ch1, 'C:/Data/13IDD/2017-3/CWRU/{R}/{R}_{L}ton_{T}K_{F}MHz.csv'".format(R=Run_Number,L=Load,T=Temp,F=int(FreqM)))
    print('Waveform data at ',int(FreqM),'MHz saved.')
    time.sleep(2.0)


"""
Enter Run Number and the peak-to-peak voltage of the input signals.
"""
Run_Number = 'T2117'
Vpp = 1.0

"""
Prompt for load and temperature information to be saved in file Names.
"""
Load = input("Enter load: ")
Temp = input("Enter Temp: ")

print()
print(Run_Number, ",",Load,"tons, and",Temp,"K, correct?")

flag = input('Enter <[y]/n>? ')

"""
Main loop to swith between different frequencies.
The loop would not start if wrong information for Run Number, Load, or Temperature is discovered.
FreqM_T is the threshold frequency above which two cycles of sine waves will be sent instead of one cycle.
"""
FreqM_T = 17.0

for FreqM in (20.0, 25.0, 30.0, 40.0, 50.0, 60.0):
    if flag in {"no","n"}:
        print()
        print("Ultrasonic data collection stopped.")
        break
    if(FreqM>FreqM_T):
        NCycles = 2
    else:
        NCycles = 1
    Sending_Signal(FreqM,Vpp,NCycles)
    Taking_Signal(FreqM,Run_Number,Load,Temp)

""""
Set the AFG and MSO back to continuous monitoring mode with a 2-cycle 30MHz input signal.
"""
afg.write(":source1:burst:ncycles 1")
afg.write(":source1:function:shape user1")
afg.write(":source1:frequency {}".format(30.0e6/2.0))
afg.write(":output1:state on")

mso.write("acquire:stopafter runstop")
mso.write(":acquire:state run")

"""
Calculate the total execution time of the program.
"""
t1 = time.clock()
print()
print('Total execution time = ',t1-t0,'seconds.')
