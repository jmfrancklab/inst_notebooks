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
    a.CH1.digital_ndarray(y)
    print "The frequency is",a.CH1.freq
    print "CH1 burst set to",a.CH1.burst
    print "now, burst on"
    a.CH1.burst = True
    print "CH1 burst set to",a.CH1.burst
    print "now, output on"
    a.CH1.output = True
with GDS_scope() as g:
    data = g.waveform(ch=2)

fl.plot(data)
with GDS_scope() as g:
    data2 = g.waveform(ch=2)

fl.plot(data2)
ylim(-1,1)
xlim(0.000003,0.000007)

with GDS_scope() as g:
    data3 = g.waveform(ch=2)
data3
fl.plot(data3)
ylim(-1,1)
xlim(0.000004,0.0000045)

fl.show()

