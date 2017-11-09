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
    for this_ch in range(2):
        a[this_ch].digital_ndarray(y, rate=60e6)
        print "CH%d burst set to"%(this_ch+1),a[this_ch].burst
        print "The frequency is",a[this_ch].freq
        print "now, output on"
        a[this_ch].output = True
    for this_ch in range(2):
        a[this_ch].burst = True
    #    print "setting burst on ch %d"%(this_ch+1)
    #    print "CH%d burst set to"%(this_ch+1),a[this_ch].burst
    #a.CH1.burst = True
    ##a.write('SOUR1:BURS:STAT ON')
    ##a.demand("SOUR1:BURS:STAT?",1)
    #a.CH2.burst = True
    #time.sleep(2)
    ##a.write('SOUR2:BURS:STAT ON')
    ##a.demand("SOUR2:BURS:STAT?",1)
exit()


print "If this doesn't work, you want to set your trigger level to 100 mV and set time/div to ~1us"
with GDS_scope() as g:
    data = g.waveform(ch=2)
fl.plot(data)
fl.show()

