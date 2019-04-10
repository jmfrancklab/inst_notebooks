#{{{ Program doc
r'''Use this program to collect 100 snapshots of noise in
    about 1 min. This is to generate the Power Spectral
    Density of the device/system. Set up for testing the
    noise of the spectrometer is as follows (also
    see AAB-LAB-2, 9/26/2018):
    *Attach 50 Ohm terminator to a Tee, then connect this
    to the DUT.
    DUT (Tee-port) --> DPX --> LNA1 --> LNA2 --> LP --> CH1 (GDS)
    Important settings on GDS are:
    (1) Set to vertical scale to 50 mV/div
    (2) Set horizontal scale to 20 us/div (100 MSPS)
    These parameters were determined to be ideal for capturing
    noise on earliest version of spectrometer (using Probe v1.0)
'''
#}}}
from Instruments import *
from pyspecdata import *
import time
from timeit import default_timer as timer
from serial.tools.list_ports import comports
import serial
from scipy import signal

acquire = False
fl = figlist_var()

#print "These are the instruments available:"
#SerialInstrument(None)
#print "done printing available instruments"
#
#with SerialInstrument('GDS-3254') as s:
#    print s.respond('*idn?')
def collect(date,id_string,captures):
    capture_length = len(captures)
    start = timer()
    datalist = []
    print "about to load GDS"
    with GDS_scope() as g:
        print "loaded GDS"
        for x in xrange(1,capture_length+1):
            print "entering capture",x
            ch1_waveform = g.waveform(ch=1)
            data = concat([ch1_waveform],'ch').reorder('t')
            if x == 1:
                channels = ((ndshape(data)) + ('capture',capture_length)).alloc(dtype=float64)
                channels.setaxis('t',data.getaxis('t')).set_units('t','s')
                channels.setaxis('ch',data.getaxis('ch'))
            channels['capture',x-1] = data
            time.sleep(1)
            #{{{ in case pulled from inactive channel
            if not isfinite(data.getaxis('t')[0]):
                j = 0
                while not isfinite(data.getaxis('t')[0]):
                    data.setaxis('t',datalist[j].getaxis('t'))
                    j+=1
                    if j == len(datalist):
                        raise ValueError("None of the time axes returned by the scope are finite, which probably means no traces are active??")
            #}}}
    s = channels
    s.labels('capture',captures)
    s.name('accumulated_'+date)
    s.hdf5_write(date+'_'+id_string+'.h5')
    print "name of data",s.name()
    print "units should be",s.get_units('t')
    print "shape of data",ndshape(s)
    return start

date = '190410'
id_string = 'noise_50Ohm_AMP_TXD_RX_2'
captures = linspace(1,100,100)

print "Starting collection..."
start = collect(date,id_string,captures)
end = timer()

print "Collection time:",(end-start),"s"
