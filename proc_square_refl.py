from pyspecdata import *
from scipy.optimize import leastsq
# 2to3 JF 1/31

fl = figlist_var()

for date, id_string,corrected_volt in [
        #('180806','pulse_reflection',True),
        #('181001','sprobe_t2',True),
        #('181001','sprobe_t4',True),
        #('181103','probe',True),
        #('200110','pulse_2',True),
        ('200110','alex_probe',True),
        ]:
    # {{{ load data, set units, show raw data
    d = nddata_hdf5(date+'_'+id_string+'.h5/capture1',
                directory=getDATADIR(exp_type='test_equip'))
    print(d.get_units('t'))
    d.set_units('t','s')
    d.name('Amplitude').set_units('V')
    fl.next('Raw signal %s'%id_string)
    fl.plot(d['ch',0], alpha=0.5, label='control') # turning off human
            #           units forces plot in just V
    fl.plot(d['ch',1], alpha=0.5, label='reflection')
    # }}}
    # {{{ determining center frequency and convert to
    # analytic signal, show analytic signal
    d.ft('t',shift=True)
    d = d['t':(0,None)] # throw out negative frequencies and low-pass
    center_frq = abs(d['ch',0]).argmax('t').item() # to get the max frequency
    print("initial guess at center frequency at %0.5f MHz"%(center_frq/1e6))
    print(center_frq)
    d.ift('t')
    d *= 2
    fl.next('Absolute value of analytic signal, %s'%id_string)
    fl.plot(abs(d['ch',0]), alpha=0.5, label='control')
    # here there was actually a figure list error,
    # where the y scaling wasn't done correctly!
    fl.plot(abs(d['ch',1]), alpha=0.5,
            label='reflection')
    # }}}
    # {{{ determine the start and stop points for both
    # the pulse, as well as the two tuning blips
    pulse_range = abs(d['ch',0]).contiguous(lambda x:
            x > 0.5*x.data.max()) # returns list of limits for which
                                  # the contiguous condition holds true
    #pulse_range = array(j for j in pulse_range if
    #        diff(j).item() > 0.1e-6)
    # RATHER -- use numpy
    def filter_range(thisrange):
        mask = diff(thisrange, axis=1) > 0.1e-6 * ones((1,2))
        thisrange = thisrange[mask].reshape((-1,2))
        return thisrange
    pulse_range = filter_range(pulse_range)
    if not pulse_range.shape[0] == 1:
        print("seems to be more than one pulse -- on starting at "
                + ','.join(('start '+str(j[0])+' length '+str(diff(j)) for j in pulse_range)))
        #fl.show();exit()
    pulse_range = pulse_range[0,:]
    fl.plot(abs(d['ch',0]['t':tuple(pulse_range)]), alpha=0.1, color='k',
            linewidth=10)
    refl_blip_ranges = abs(d['ch',1]).contiguous(lambda x:
            x > 0.05*x.data.max()) # returns list of limits for which
                                  # the contiguous condition holds true
    refl_blip_ranges = filter_range(refl_blip_ranges)
    assert refl_blip_ranges.shape[0] == 2, "seems to be more than two tuning blips "
    for thisrange in refl_blip_ranges:
        fl.plot(abs(d['ch',1]['t':tuple(thisrange)]), alpha=0.1, color='k',
                linewidth=10)
    # }}}
    # {{{ apply a linear phase to find the frequency of
    # the pulse (control)
    f_shift = nddata(r_[-0.1e6:0.1e6:200j]+center_frq,'f_test')
    # perform and store 200 frequency de-modulations of signal
    test_array = d['ch',0] * exp(-1j*2*pi*f_shift*d.fromaxis('t'))
    # when modulating by same frequency of the waveform,
    # abs(sum(waveform)) will be a maximum
    center_frq = test_array.sum('t').run(abs).argmax('f_test').item()
    print("found center frequency at %0.5f MHz"%(center_frq/1e6))
    # }}}
    # JF review stopped here
    # {{{ creates demodulated reflection 
    d.ft('t')
    d.setaxis('t', lambda x: x - center_frq)
    fl.next('test time axis')
    t_shift_testvals = r_[-1e-6:1e-6:1000j]+pulse_range[0]
    t_shift = nddata(t_shift_testvals,'t_shift')
    # perform and store 1000 time shifts 
    test_data = d['ch',0].C * exp(-1j*2*pi*t_shift*d.fromaxis('t'))
    test_data_ph = test_data.C.sum('t')
    test_data_ph /= abs(test_data_ph)
    test_data /= test_data_ph
    test_data.run(real).run(abs).sum('t')
    fl.plot(test_data,'.')
    pulse_start = test_data.argmin('t_shift').data
    d.ift('t')
    # Alex -- modify this so it slices out just the
    # first blip, as well as a little bit more to
    # either side. 
    #AG--I believe this is done in line 146
    # {{{ I have modified the zeroth order phasing --
    # just ignore for now -- JF (though I explain for
    # myself)
    #def zeroth_order_ph(d, plot_name=None):
        #r'''determine the covariance of the datapoints
        #in complex plane, and use to phase the
        #zeroth-order even if the data is both negative
        #and positive'''
        #eigenValues, eigenVectors = eig(cov(c_[
            #d.data.real,
            #d.data.imag].T
            #))
        # next 3 lines from stackexchange -- sort by
        # eigenvalue
        #idx = eigenValues.argsort()[::-1]   
        #eigenValues = eigenValues[idx]
        #eigenVectors = eigenVectors[:,idx]
        # determine the phase angle from direction of the
        # largest principle axis
        #ph0 = arctan2(eigenVectors[1,0],eigenVectors[0,0])
        #if plot_name:
            #eigenVectors *= (eigenValues.reshape(-1,2)*ones((2,1)))/eigenValues.max()*abs(d.data).max()
            #d_forplot = d.C
            #fl.next(plot_name)
            #fl.plot(
                    #d_forplot.data.real,
                    #d_forplot.data.imag,
                    #'.',
                    #alpha=0.25,
                    #label='before'
                    #)
            #d_forplot /= exp(1j*ph0)
            #fl.plot(
                    #d_forplot.data.real,
                    #d_forplot.data.imag,
                    #'.',
                    #alpha=0.25,
                    #label='after'
                    #)
            #fl.plot(0,0,'ko')
            #fl.plot(eigenVectors[0,0],eigenVectors[1,0],'o',
                    #label='first evec')
            #fl.plot(eigenVectors[0,1],eigenVectors[1,1],'o')
        #return exp(1j*ph0)
    # }}}
    #for j in range(2):
        #ph0 = zeroth_order_ph(d['ch',j], plot_name='phasing')
        #d['ch',j] /= ph0
    fl.next('demodulated and phased data')
    #d = d['t':(2e-06,4e-06)]
    for j in range(2):
        fl.plot(d['ch',j], label='channel %d real'%j,
                alpha=0.5)
        fl.plot(d['ch',j].imag, label='channel %d imag'%j,
                alpha=0.5)
    #fl.show();quit()
    d.setaxis('t',lambda x: x-pulse_start)
    print("NOTE!!! the demodulated reflection looks bad -- fix it")
    #fl.show();quit()
    # to use the phase of the reference to set both, we could do:
    # pulse_phase = d['ch',0].C.sum('t')
    # but I don't know if that's reasonable -- rather I just phase both independently:
    pulse_phase = d.C.sum('t')
    pulse_phase /= abs(pulse_phase)
    d /= pulse_phase
    for j,l in enumerate(['control','reflection']):
        fl.next('adjusted analytic '+l)
        fl.plot(d['ch',j].real, alpha=0.3, label='real')
        fl.plot(d['ch',j].imag, alpha=0.3, label='imag')
        fl.plot(abs(d['ch',j]), alpha=0.3, color='k', linewidth=2,
                label='abs')
    #fl.show();quit()
    # }}}
    # {{{ to plot the transfer function, we need to pick an impulse
    # of finite width, or else we get a bunch of noise
    transf_range = (-0.5e-6,3e-6)
    fl.next('the transfer function')
    impulse = exp(-d.fromaxis('t')**2/2/(0.03e-6)**2)
    ## the following gives a possibility for a causal impulse
    #impulse = exp(-abs(d.fromaxis('t'))/0.01e-6)
    #impulse['t':(None,0)] = 0
    fl.plot(impulse['t':transf_range], alpha=0.5, color='k', label='impulse')
    d.ft('t')
    transf = d['ch',1]/d['ch',0]
    impulse.ft('t')
    response = impulse*transf
    response.ift('t')
    response = response['t':transf_range]
    fl.plot(response.real, alpha=0.5, label='response, real')
    fl.plot(response.imag, alpha=0.5, label='response, imag')
    fl.plot(abs(response), alpha=0.3, linewidth=3, label='response, abs')
    #fl.show();quit()
    fl.next('Plotting the decay slice')
    # slice out a range from the start of the first
    # blip up to halfway between the END of the first
    # blip and the start of the second
    d.ift('t')
    decay = d['ch',1]['t':(refl_blip_ranges[0,0],
        0.5*(refl_blip_ranges[0,1]+refl_blip_ranges[1,0]))]
    decay = decay.setaxis('t',lambda x: x-decay.getaxis('t')[0])
    # }}}
    fitfunc = lambda p: p[0]*exp(-decay.fromaxis('t')*p[1])+p[2]
    p_ini = r_[decay['t',0].data.real.max(),1/0.5e-6,0]
    fl.plot(fitfunc(p_ini), ':', label='initial guess')
    residual = lambda p: fitfunc(p).data.real - decay.data.real
    p_opt, success = leastsq(residual, p_ini[:])
    assert success > 0 & success < 5, "fit not successful"
    Q = 1./p_opt[1]*2*pi*center_frq
    fl.plot(fitfunc(p_opt), label='fit')
    fl.plot(decay, label='data')
    fl.plot(decay.imag, label='data (imag, not fit)')
    print(Q)
    fl.show();quit()
