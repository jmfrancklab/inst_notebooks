from pyspecdata import *
fl = figlist_var()
import os
import sys
import matplotlib.style
import matplotlib as mpl

mpl.rcParams['image.cmap'] = 'jet'

def load_noise(date,id_string,captures):
    cap_len = len(captures)
    filename = date+'_'+id_string+'.h5'
    try:
        s = nddata_hdf5(filename+'/accumulated_'+date,
                directory=getDATADIR(exp_type='test_equip'))
        s.set_units('t','s')
    except:
        print "accumulated data was not found, pulling individual captures"
        for j in xrange(1,cap_len+1):
            j_str = str(j)
            d = nddata_hdf5(filename+'/capture'+j_str+'_'+date,
                directory=getDATADIR(exp_type='test_equip'))
            d.set_units('t','s')
            if j == 1:
                channels = ((ndshape(d)) + ('capture',cap_len)).alloc()
                channels.setaxis('t',d.getaxis('t')).set_units('t','s')
                channels.setaxis('ch',d.getaxis('ch'))
            print "loading signal %s into capture %s "%(j_str,j_str)
            channels['capture',j-1]=d        
        s = channels
        s.labels('capture',captures)
        s.name('accumulated_'+date)
        s.hdf5_write(filename,
                directory=getDATADIR(exp_type='test_equip'))
    return s


gain_factor_dcasc12 = 114008.55204672
captures = linspace(0,100,100)
for date,id_string,numchan,gain_factor in [
        ('180625','network_22MHz_100M_2',2,gain_factor_dcasc12),
        ]:
    s = load_noise(date,id_string,captures)['ch',0]
    s.ft('t',shift=True)
    s = abs(s['t':(0,30e6)]).run(log10)
    width = 0.01e6
    s.convolve('t',width)
    fl.next('image')
    fl.image(s.real,interpolation='bicubic')
fl.show()
