from Instruments import *
from pyspecdata import *
import time
from serial.tools.list_ports import comports
import serial
from scipy import signal

acquire = False
fl = figlist_var()

print "These are the instruments available:"
SerialInstrument(None)
print "done printing available instruments"

with SerialInstrument('GDS-3254') as s:
    print s.respond('*idn?')
    
def acquire(x):
    datalist = []
    print "about to load GDS"
    with GDS_scope() as g:
        print "loaded GDS"
        ch1_waveform = g.waveform(ch=1)
        ch2_waveform = g.waveform(ch=2)
    data = concat([ch1_waveform,ch2_waveform],'ch').reorder('t')
    #{{{ in case pulled from inactive channel
    if not isfinite(data.getaxis('t')[0]):
        j = 0
        while not isfinite(data.getaxis('t')[0]):
            data.setaxis('t',datalist[j].getaxis('t'))
            j+=1
            if j == len(datalist):
                raise ValueError("None of the time axes returned by the scope are finite, which probably means no traces are active??")
    #}}}
    data_name = 'capture%d_180608'%x
    data.name(data_name)
    data.hdf5_write('180608_testing4_LNA1.h5')
    print "capture number",x
    print "name of data",data.name()
    print "units should be",data.get_units('t')
    print "shape of data",ndshape(data)
    return

def gen_pulse(freq=14.5e6, width=4e-6, ch1_only=True):
    raw_input("Confirm Sample Rate = 2.5 GSPS")
    for x in xrange(0,101):
        print "entering capture",x
        acquire(x)
    return


gen_pulse()

