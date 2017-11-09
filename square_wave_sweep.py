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
    x = r_[-6:6:200j]
    y = zeros_like(x)
    #create duplicate of x as an array container and fill each index with 0
    y[0::4]=0
    y[1::4]=1
    y[2::4]=0
    y[3::4]=-1
    y[-1]=0
    #in the new array container, now assign 3 and -3 to each alternating index
    a.CH1.digital_ndarray(y, rate=60e6)
    a.CH2.digital_ndarray(y, rate=60e6)
    print "CH1 burst set to",a.CH1.burst
    print "now, burst 1 on"
    a.CH1.burst = True
    print "CH2 burst set to",a.CH2.burst
    print "now, burst 2 on"
    a.CH2.burst = True
    print "CH1 burst set to",a.CH1.burst
    print "The CH1 frequency is",a.CH1.freq
    print "now, output 1 on"
    a.CH1.output = True
    print "CH2 burst set to",a.CH2.burst
    print "The CH2 frequency is",a.CH2.freq
    print "now output 2 on"
    a.CH2.output = True


print "If this doesn't work, you want to set your trigger level to 100 mV and set time/div to ~1us"
with GDS_scope() as g:
    data = g.waveform(ch=2)
fl.plot(data)
fl.show()

