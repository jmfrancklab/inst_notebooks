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
from sys import argv

start = time.time()
fl = figlist_var()

args = sys.argv[1:]
filename = '181212_JFAB_pulse.h5'
if '-f' in args:
    force_acq = True
    args.pop(args.index('-f'))
else:
    force_acq = False
datalist = []
print "about to load datasets",args
for j,dataset in enumerate(args):
    print "acquiring/loading dataset",dataset
    if force_acq and j==len(args)-1:
        print "Forcing acquisition of last dataset"
        _,thisnode = h5nodebypath('%s/%s'%(filename,dataset))
        thisnode._f_remove(recursive=True)
    try:
        data = nddata_hdf5('%s/%s'%(filename,dataset))
    except:
        print "didn't find %s: about to load GDS"%dataset
        with GDS_scope() as g:
            print "loaded GDS"
            #g.acquire_mode('average',32)
            #raw_input("Wait for averaging to relax...")
            for j in range(1,3):
                print "trying to grab data from channel",j
                datalist.append(g.waveform(ch=j))
            data = concat(datalist,'ch').reorder('t')
        j = 1
        data.name(dataset)
        data.hdf5_write(filename)
        print "name of data",data.name()
        print "units should be",data.get_units('t')
        print "shape of data",ndshape(data)
    fl.next('raw signal')
    fl.plot(data,alpha=0.5)
    data.ft('t',shift=True)
    data['t':(None,0)] = 0
    print "type is",data.data.dtype
    fl.next('analytic signal -- abs')
    data.ift('t')
    data *= exp(-1j*2*pi*data.fromaxis('t')*14.46e6)
    fl.plot(abs(data['ch',0]),alpha=0.5,label=dataset)
    fl.next('analytic signal -- phase',legend=True)
    fl.plot(data['ch',0].angle/pi/2,',',alpha=0.5,label=dataset)
fl.show()
