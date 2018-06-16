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
#    ref_amp = 0.25 
    ref_amp = 0.75
    DUT_amp = sqrt(((((ref_amp/2/sqrt(2))**2)/50)/4)*50)*2*sqrt(2)
    for this_ch in range(2):
        a[this_ch].digital_ndarray(y,rate=100e6)
        a[this_ch].output = True
    for this_ch in range(2):
        a[this_ch].burst = True
        #setting ref channel to amplitude after power splitter
        if this_ch == 0: 
            a[this_ch].ampl=DUT_amp
        #setting DUT channel to amplitude before power splitter
        elif this_ch == 1: 
            a[this_ch].ampl=ref_amp
        else:
            print "Channel not recognized"

datalist = []
print "about to load GDS"
#raw_input("Turn on RF amp") 

with GDS_scope() as g:
    g.timscal(5e-6)  #setting time scale to 5 micros/div
    if ref_amp == 0.25:
        for this_ch in range(2):
            g[this_ch].voltscal = 20e-3 #setting volt scale to 20 mV/div
    elif ref_amp == 0.75:
        for this_ch in range(2):
            g[this_ch].voltscal = 50e-3 #setting volt scale to 50 mV/div
    print "loaded GDS"
    for j in range(1,3):
        print "trying to grab data from channel",j
        datalist.append(g.waveform(ch=j))
data = concat(datalist,'ch').reorder('t')
j = 1
try_again = True
raw_input("Enter to continue:")
while try_again:
    data_name = 'capture%d'%j
    data.name(data_name)
    try:
        data.hdf5_write('180616_chirp_test.h5')
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
