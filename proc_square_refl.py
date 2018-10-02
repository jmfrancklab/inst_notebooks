from pyspecdata import *
from scipy.optimize import leastsq
#import logging
#init_logging(level=logging.DEBUG)
#{{{ boolean statement for processing data before modification to generate chirp
#   that sets voltage of ref (CH1 of scope) and DUT (CH2 of scope) to same value
corrected_volt = True
#}}}
fl = figlist_var()
#with figlist_var() as fl:
#    fl.next('$S_{11}$ : phase', legend=True)
#expno=0
for date, id_string,corrected_volt in [
        #('180806','pulse_reflection',True),
        #('181001','sprobe_t2',True),
        ('181001','sprobe_t4',True),
        ]:
    d = nddata_hdf5(date+'_'+id_string+'.h5/capture1',
                directory=getDATADIR(exp_type='test_equip'))
    d.set_units('t','s')
    d.name('Amplitude $/$ $V$')
    fl.next('Raw signal', legend=True)
    fl.plot(d['ch',0],alpha=0.5,label='control')
    fl.plot(d['ch',1],alpha=0.5,label='reflection')
    # {{{ find the analytic signal
    d.ft('t',shift=True)
    d = d['t':(0,None)] # throw out negative frequencies and low-pass
    max_frq = abs(d['ch',0]).argmax('t').data # to get the max frequency
    print max_frq
    d.reorder('ch', first=False) # move ch dimension last
    d.ift('t')
    d *= 2
    # }}}
    # see PEP-8 https://www.python.org/dev/peps/pep-0008/#other-recommendations
    decay = abs(d['ch',1]).C
    fl.next('Analytic signal', legend=True)
    fl.plot(abs(d['ch',0]), alpha=0.5, label='control')
    fl.plot(abs(d['ch',1]), alpha=0.5, label='reflection')
    # guess the start of the pulse
    ranges = abs(d['ch',0]).contiguous(lambda x:
            x > 0.5*x.data.max())
    assert ranges.shape[0] == 1, "seems to be more than one pulse"
    pulse_start,pulse_stop = ranges[0,:]
    # {{{ apply a linear phase to find the frequency
    fl.next('test frequency axis')
    frq_test = r_[-0.1e6:0.1e6:200j]+max_frq
    f_shift = nddata(frq_test,'f_test')
    test_array = d['ch',0].C * exp(-1j*2*pi*f_shift*d.fromaxis('t'))
    test_array.sum('t').run(abs)
    fl.plot(test_array)
    center_frq = test_array.argmax('f_test').data
    print "found center frequency at %0.5f MHz"%(center_frq/1e6)
    # }}}
    # {{{ switch to frequency domain, and relabel using the center frequency
    d.ft('t')
    d.setaxis('t',lambda x: x-center_frq)
    # }}}
    # {{{   try the phasing trick on the pulse
    #       because the frequency domain should be causal and therefore a
    #       sum of lorentzians
    #
    #       if the pulse is causal (starts at 0), then its FT is a
    #       superposition of Lorentzians
    #
    #       this works because the sum of the abs of the real part of
    #       a Lorentzian with correct zero-order phase is a minimum
    #       for the correctly phased Lorentzian -- anything that
    #       mixes in the dispersive part increases the sum of the abs
    #       of the real
    def apply_ph1(ph1,d_orig):
        retval = d_orig.C
        retval *= exp(-1j*2*pi*ph1*retval.fromaxis('t')) # ph1 is cycles per SW
        d_ph = retval.C.sum('t')
        d_ph /= abs(d_ph)
        retval /= d_ph
        return retval
    fl.next('test time axis')
    t_shift_testvals = r_[-1e-6:1e-6:1000j]+pulse_start
    t_shift = nddata(t_shift_testvals,'t_shift')
    test_data = d['ch',0].C * exp(-1j*2*pi*t_shift*d.fromaxis('t'))
    test_data_ph = test_data.C.sum('t')
    test_data_ph /= abs(test_data_ph)
    test_data /= test_data_ph
    test_data.run(real).run(abs).sum('t')
    fl.plot(test_data)
    pulse_start = test_data.argmin('t_shift').data
    # }}}
    d.ift('t')
    d.setaxis('t',lambda x: x-pulse_start)
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
    # {{{ to plot the transfer function, we need to pick an impulse
    # of finite width, or else we get a bunch of noise
    transf_range = (-0.5e-6,3e-6)
    fl.next('the transfer function')
    impulse = exp(-d.fromaxis('t')**2/2/(0.03e-6)**2)
    ## the following gives a possibility for a causal impulse
    #impulse = exp(-abs(d.fromaxis('t'))/0.01e-6)
    #impulse['t':(None,0)] = 0
    fl.plot(impulse['t':transf_range], alpha=0.5, color='k', label='impulse')
    # {{{ not sure if needed -- I'm making sure the frequency axes
    # line up, since the default is to FT back to the same FT
    # startpoint
    d.ft_clear_startpoints('t', t='current')
    impulse.ft_clear_startpoints('t', t='current')
    # }}}
    d.ft('t', shift=True)
    transf = d['ch',1]/d['ch',0]
    impulse.ft('t', shift=True)
    response = impulse*transf
    response.ift('t')
    response = response['t':transf_range]
    fl.plot(response.real, alpha=0.5, label='response, real')
    fl.plot(response.imag, alpha=0.5, label='response, imag')
    fl.plot(abs(response), alpha=0.3, linewidth=3, label='response, abs')
    # }}}
    #expno += 1 
    from_raw = False
    from_ph = True
    if from_raw:
        fl.next('decay')
        fl.plot(abs(decay))
        max_time = decay.getaxis('t')[list(abs(decay).data).index(amax(abs(decay).data))]
        decay = decay['t':(max_time,None)].C
        decay.ft('t')
        decay *= exp(-1j*2*pi*max_time*decay.fromaxis('t'))
        decay.ift('t')
        fl.next('decay')
        fl.plot(abs(decay),':')
        fl.show();quit()
        start = decay.getaxis('t')[0]
        decay.setaxis('t',decay.fromaxis('t') - start)
        #max_time = decay.getaxis('t')[list(abs(decay).data).index(amax(abs(decay).data))]
        #print max_time;quit()
        fl.next('decay 2')
        fl.plot(abs(decay),':',human_units=False)
        Q = 1
        #fl.plot(exp(-decay.getaxis('t')*center_frq/(2*Q)))
    if from_ph:
        decay = d['ch',1].C
        decay.ift('t')
        fl.next('plotting the decay')
        fl.plot(abs(decay))
        max_time = decay.getaxis('t')[list(abs(decay).data).index(amax(abs(decay).data))]
        decay.ft('t')
        decay *= exp(1j*2*pi*max_time*decay.fromaxis('t'))
        decay.ift('t')
        fl.plot(abs(decay),':')
        decay = abs(decay)['t':(0,6e-6)]
        fl.plot(decay,':',c='k')
        fl.next('decay')
        fl.plot(decay,human_units=False)
        fl.next('fitting')
        x = decay.getaxis('t')
        ydata = decay.data
        fl.plot(x,ydata, alpha=0.2, human_units=False)
        fitfunc = lambda p, x: decay.data[0]*exp(-x*2*pi*center_frq/(2*p[0]))
        fl.plot(x, fitfunc(r_[30.],x), ':', label='initial fit, Q=30', human_units=False)
        errfunc = lambda p_arg, x_arg, y_arg: fitfunc(p_arg, x_arg) - y_arg
        p0 = [30.]
        p1, success = leastsq(errfunc, p0[:], args=(x, ydata))
        Q = p1[0]
        x_fit = linspace(x.min(), x.max(), 5000)
        fl.plot(x_fit, fitfunc(p1, x_fit),':',c='k', label='final fit, Q=%d'%Q)
        print "Q:",Q
    fl.show()

