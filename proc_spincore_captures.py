from Instruments import *
from pyspecdata import *

fl = figlist_var()
filename = '181212_test_steps.h5'
for this_num in r_[1,2,3,4]:
    dataset = str(this_num)
    data = nddata_hdf5('%s/%s'%(filename,dataset))
    fl.next('raw signal')
    fl.plot(data,alpha=0.5)
    data.ft('t',shift=True)
    data['t':(None,0)] = 0
    print "type is",data.data.dtype
    fl.next('analytic signal -- abs')
    data.ift('t')
    data *= exp(-1j*2*pi*data.fromaxis('t')*5e6)
    fl.plot(abs(data['ch',0]),alpha=0.5,label=dataset)
    fl.next('analytic signal -- phase',legend=True)
    fl.plot(data['ch',0].angle/pi/2,',',alpha=0.5,label=dataset)
fl.show()
