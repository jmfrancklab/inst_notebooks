from Instruments import *
from pyspecdata import *
import time
from serial.tools.list_ports import comports
import serial
from scipy import signal

raw_input("Warning --> Detach from amplifier before proceeding further (set AFG before hooking up, since it generates cw)")

acquire = False

fl = figlist_var()

print "These are the instruments available:"
SerialInstrument(None)
print "done printing available instruments"

with SerialInstrument('GDS-3254') as s:
    print s.respond('*idn?')
    
with SerialInstrument('AFG-2225') as s:
    print s.respond('*idn?')

def gen_pulse(freq=15e6, width=4e-6, ch1_only=True):
    with AFG() as a:
        a.reset()
        rate = freq*4
        total_samples = width*rate
        total_samples = int(total_samples/4 + 0.5)*4 # convert to multiple of 4
        assert total_samples < 4097, "Your pattern length (%d) exceeds the max (4096 samples at %g MHz)"%(total_samples,rate)
        y = zeros(total_samples)
        y[0::4]=0
        y[1::4]=1
        y[2::4]=0
        y[3::4]=-1
        y[-1]=0
        if ch1_only:
            ch_list = [0]
        else:
            ch_list = [0,1]
        for this_ch in ch_list:
            a[this_ch].digital_ndarray(y, rate=rate)
           # a[this_ch].ampl=1e0
            print "now, output on"
            a[this_ch].output = True
        for this_ch in range(2):
            a[this_ch].burst = True
        # if we run a.check_idn() here, it pops out of burst mode
gen_pulse()

if acquire:
    #print "If this doesn't work, you want to set your trigger level to 100 mV and set time/div to ~1us"
    datalist = []
    print "about to load GDS"
    with GDS_scope() as g:
    #    g.timscal(5e-6)  #setting time scale to 500 ns/div
    #    g.voltscal(1,500e-3) #setting volt scale on channel 1 to 500 mV/div
        print "loaded GDS"
        for j in range(1,3):
            print "trying to grab data from channel",j
            datalist.append(g.waveform(ch=j))
    data = concat(datalist,'ch').reorder('t')
    j = 1
    try_again = True
    while try_again:
        data_name = 'capture%d_171109'%j
        data.name(data_name)
        try:
            data.hdf5_write('scope_data.h5')
            try_again = False
        except:
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
# else:
#    with GDS_scope() as g:
#        g.timscal(5e-6)  #setting time scale to 500 ns/div
