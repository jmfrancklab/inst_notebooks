from Instruments import *
from pyspecdata import *
import time
from serial.tools.list_ports import comports
import serial
from scipy import signal

fl = figlist_var()

print "These are the instruments available:"
SerialInstrument(None)
print "done printing available instruments"

with SerialInstrument('GDS-3254') as s:
    print s.respond('*idn?')
    
with SerialInstrument('AFG-2225') as s:
    print s.respond('*idn?')

with AFG() as a:
    a.reset()
    t = r_[0:4096]
    y = imag(exp(1j*2*pi*0.25*(1-0.5/4096.*t)*t))
    for this_ch in range(2):
        a[this_ch].digital_ndarray(y,rate=100e6)
        print "now, output on"
        a[this_ch].output = True
    for this_ch in range(2):
        a[this_ch].burst = True

datalist = []
print "about to load GDS"
with GDS_scope() as g:
#     g.timscal(500e-9)  #setting time scale to 500 ns/div
#     g.voltscal(1,500e-3) #setting volt scale on channel 1 to 500 mV/div
    print "loaded GDS"
    for j in range(1,3):
        print "trying to grab data from channel",j
        datalist.append(g.waveform(ch=j))
data = concat(datalist,'ch').reorder('t')
j = 1
try_again = True
while try_again:
    data_name = 'capture%d'%j
    data.name(data_name)
    try:
        data.hdf5_write('180109_adj2.h5')
        try_again = False
    except Exception as e:
        print e
        print "name taken, trying again..."
        j += 1
        try_again = True
print "name of data",data.name()
print "units should be",data.get_units('t')
print "shape of data",ndshape(data)
fl.next('Dual-channel data')
fl.plot(data)
fl.show()
#
