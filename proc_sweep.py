from pyspecdata import *

mixdown = 15e6
capture_num = 1
f_axis = linspace(100e3,500e3,100) # must match sweep_frequencies_sqw

for j,thisfreq in enumerate(f_axis):
    data_name = 'capture%d_F%04.3fMHz'%(capture_num,(thisfreq*50)/1e6)
    d = nddata_hdf5(
            '171120_circuit_sweep.h5/%s'%data_name,
            '171220_series_chirp.h5/%s'%data_name,
            directory=getDATADIR(exp_type='test_equip')
            ).set_units('t','s') # why are units not already set?
    d.ft('t',shift=True)
    d = d['t':(0,25e6)] # throw out negative frequencies and low-pass
    if j == 0:
        collated = ndshape(d)
        collated += ('f_pulse',len(f_axis))
        collated = collated.alloc(format=None)
        # {{{ note to self: this should NOT be required
        #     need to add/move labels to ndshape
        collated.setaxis('t', d.getaxis('t')).setaxis(
                'ch', d.getaxis('t')).setaxis(
                        'f_pulse', f_axis*50.)
        collated.set_units('t','Hz').set_units('f_pulse','Hz')
        #collated.set_ft_prop('t') #shouldn't be required
        # }}}
    # we should really do a lot of the above inside the acquisition routine
    collated['f_pulse',j] = d
with figlist_var(filename='sweep_171116.pdf') as fl:
    collated.reorder('ch') # move ch first (outside)
    collated.ift('t')
    collated_unmixed = collated.copy()
    collated *= collated.fromaxis('t',
            lambda x: exp(-1j*2*pi*mixdown*x))
    fl.next('analytic signal, raw')
    collated *= collated.fromaxis(['t','f_pulse'],
            lambda t,f: exp(-1j*2*pi*f*t))
    fl.next('analytic signal, mixed down')
    fl.image(collated)
    ratio = collated['ch',1]/collated['ch',0]
    fl.next('ratio ch2 to ch1')
    fl.image(ratio)
    fl.next('ratio, abs over safe range')
    fl.image(abs(ratio['t':(11.6e-6,13e-6)]))
    fl.next('ratio, sum over safe range')
    avg_over_t = ratio['t':(11.6e-6,13e-6)].runcopy(mean,'t')
    fl.plot(abs(avg_over_t))
    ylim(0,1)
    ylabel('amplitude (solid line)')
    fl.next('ratio, sum over safe range', twinx=1)
    fl.plot(avg_over_t.angle/pi,'.')
    ylabel('phase (dots)')
    # {{{ because I have amplitudes that blow up, do the following:
    #     (maybe I should be dividing in the frequency domain?
    ratio /= abs(ratio)
    ratio *= abs(collated['ch',1])
    # }}}
    fl.next('phase difference ch2 to ch1')
    fl.image(ratio)
    fl.next('phase difference ch2 to ch1, frequency domain')
    collated_unmixed.ft('t')
    fl.image(collated_unmixed['ch',1]/collated_unmixed['ch',0]*abs(collated_unmixed['ch',0]))
    fl.next('ratio in frequency domain -- mixed down')
    collated.set_ft_prop('t',['time','not','aliased'], True)
    collated.ft_clear_startpoints('t',f=-12.5e6,t='current')
    collated.ft('t')
    fdomain_ratio = collated['ch',1]/collated['ch',0]*abs(collated['ch',1])
    fl.image(fdomain_ratio['t':(-5e6,5e6)])
    fl.next('ratio in frequency domain -- mixed down, error')
    collated.set_error(ones_like(collated.data))
    fdomain_ratio = collated['ch',1]/collated['ch',0]
    fl.image(abs(fdomain_ratio['t':(-5e6,5e6)].get_error()))

