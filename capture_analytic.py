#{{{ Program doc
r'''
Use this program to capture a scope trace and display the analytic signal
(frequency is hard-coded in here)

Can capture a series of differently named datasets that are written to the same
hdf5 file (filename also hard coded, one dataset per node).  Give a list of the
dataset names.  Any dataset that doesn't exist will be captured from the scope.
To clear/overwrite the last dataset in the list, give -f as an argument, as
well.
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
filename = '181212_JFAB_pulse_trial2.h5'
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
