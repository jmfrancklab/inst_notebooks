from pyspecdata import *

mixdown = 15e6
capture_num = 1
f_axis = linspace(100e3,500e3,100) # must match sweep_frequencies_sqw

for j,thisfreq in enumerate(f_axis):
    data_name = 'capture%d_F%04.3fMHz'%(capture_num,(thisfreq*50)/1e6)
    d = nddata_hdf5(
            '171116_100fsweep.h5/%s'%data_name,
            directory=getDATADIR(exp_type='test_equip')
            ).set_units('t','s') # why are units not already set?
    d.ft('t',shift=True)
    d = d['t':(0,40e6)] # analytic signal and low-pass
    d.ift('t')
    d *= d.fromaxis('t',
            lambda x: exp(-1j*2*pi*mixdown*x))
    if j == 0:
        collated = ndshape(d)
        collated += ('f_pulse',len(f_axis))
        collated = collated.alloc(format=None)
        # {{{ note to self: this should NOT be required
        #     need to add/move labels to ndshape
        collated.setaxis('t', d.getaxis('t')).setaxis(
                        'ch', d.getaxis('t')).setaxis(
                        'f_pulse', f_axis)
        # }}}
    collated['f_pulse',j] = d
with figlist_var(filename='sweep_171116.pdf') as fl:
    collated.reorder('ch') # move ch first (outside)
    fl.next('analytic signal, raw')
    fl.image(collated)
