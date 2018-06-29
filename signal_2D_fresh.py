from pyspecdata import *
import os
import sys
import matplotlib.style
import matplotlib as mpl
from logging import DEBUG

init_logging(level=DEBUG)

mpl.rcParams['image.cmap'] = 'jet'

date,id_string,numchan,gain_factor = ('180628','spin_echo_exp2_cont2',1,1)
filename = date+'_'+id_string+'.h5'
nodename = "accumulated_"+date
## {{{ to store a truncated file
#filename = date+'_'+id_string+'.h5'
#s = nddata_hdf5(filename+'/'+nodename,
#        directory=getDATADIR(exp_type='test_equip'))['capture',0:100]
#s.set_units('t','s')
#s.name('test')
#s.hdf5_write('test_data_180629.h5',
#        directory=getDATADIR(exp_type='test_equip'))
#exit()
## }}}
#filename = 'test_data_180629.h5'
#nodename = 'test'
with figlist_var() as fl:
    s = nddata_hdf5(filename+'/'+nodename,
            directory=getDATADIR(exp_type='test_equip'))['ch',0]
    s.set_units('t','s')
    s.ft('t',shift=True)
    s = s['t':(0,15.5e6)]
    s.setaxis('t',lambda x: x - 14.5e6 - 16.95e3)
    fl.next('FT of raw signal')
    fl.image(abs(s))
    s_filt = s.C
    s_filt['t':(None,-1e6)] = 0
    s.ift('t')
    s_filt.ift('t')
    #s *= s.fromaxis('t',lambda x: exp(-1j*2*pi*resonance_freq)
    fl.next('Raw signal')
    fl.image(s)
    logger.info('plotted raw signal')
    fl.next('Filtered')
    fl.image(s_filt)
    logger.info('plotted filtered signal')
    fl.next('filtered, cropped log')
    fl.image(s_filt.C.cropped_log())
    logger.info('plotted cropped log signal')
