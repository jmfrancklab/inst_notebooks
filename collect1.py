#{{{ Program doc
r'''Use this program to capture a single S11 (reflection) measurement
    Must use the appropriate set up of the power splitter (PS) and
    reference channel (CH1). Set up as follows (also see AAB-2, 7/12/2018
    yellow tab):
    CH1 (AFG) -*ref*-> CH1 (GDS) *Use coax labeled 'REF'
    CH2 (AFG) --> PS (PORT 1) --> PS (S) --> DUT --> PS (2) --> CH2 (GDS)
    Sends out programmed waveform on both channels of the AFG, with
    the option to correct for amplitude variation (due to use of
    the power splitter), so that the reflection is calculated
    correctly (using *proc_chirp.py*)
    There are two options for a programmed waveform:
        (1) A proper chirp from 5 to 25 MHz,
    and (2) A pulse of a specified frequency
    These options are chosen by the :pulse_90: boolean,
    where True is (2) and False is (1).
'''
#}}}
from Instruments import *
from pyspecdata import *
import time
from serial.tools.list_ports import comports
import serial
from scipy import signal

start = time.time()
fl = figlist_var()

datalist = []
print("about to load GDS")
with GDS_scope() as g:
    print("loaded GDS")
    #g.acquire_mode('average',32)
    input("Wait for averaging to relax...")
    for j in range(1,3):
        print("trying to grab data from channel",j)
        datalist.append(g.waveform(ch=j))
data = concat(datalist,'ch').reorder('t')
j = 1
try_again = True
while try_again:
    data_name = 'capture%d'%j
    data.name(data_name)
    try:
        data.hdf5_write('181212_JFAB_pulse_ph0.h5')
        try_again = False
    except Exception as e:
        print(e)
        print("name taken, trying again...")
        j += 1
        try_again = True
print("name of data",data.name())
print("units should be",data.get_units('t'))
print("shape of data",ndshape(data))
end = time.time()
fl.next('Dual-channel data')
fl.plot(data)
fl.show()
#
