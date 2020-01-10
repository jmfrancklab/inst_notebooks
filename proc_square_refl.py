from pyspecdata import *
from scipy.optimize import leastsq

fl = figlist_var()

for date, id_string,corrected_volt in [
        #('180806','pulse_reflection',True),
        #('181001','sprobe_t2',True),
        #('181001','sprobe_t4',True),
        #('181103','probe',True),
        #('200110','pulse_2',True),
        ('200110','alex_probe',True),
        ]:
    d = nddata_hdf5(date+'_'+id_string+'.h5/capture1',
                directory=getDATADIR(exp_type='test_equip'))
    d.set_units('t','s')
    d.name('Amplitude $/$ $V$')
    fl.next('Raw signal %s'%id_string)
    if date == '200110':
        d['ch',0] *= 0.5
    fl.plot(d['ch',0],alpha=0.5,label='control')
    fl.plot(d['ch',1],alpha=0.5,label='reflection')
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
    fl.next('Analytic signal %s'%id_string)
    fl.plot(abs(d['ch',0]), alpha=0.5, label='control')
    fl.plot(abs(d['ch',1]), alpha=0.5, label='reflection')
    #fl.show();quit()
    # guess the start of the pulse
    ranges = abs(d['ch',0]).contiguous(lambda x:
            x > 0.5*x.data.max()) # returns list of limits for which
                                  # the contiguous condition holds true
    #assert ranges.shape[0] == 1, "seems to be more than one pulse"
    pulse_start,pulse_stop = ranges[0,:]
    # {{{ apply a linear phase to find the frequency
    frq_test = r_[-0.1e6:0.1e6:200j]+max_frq
    f_shift = nddata(frq_test,'f_test')
    # perform and store 200 frequency modulations of signal
    test_array = d['ch',0].C * exp(-1j*2*pi*f_shift*d.fromaxis('t'))
    test_array.sum('t').run(abs)
    fl.next('test frequency axis')
    fl.plot(test_array,'.')
    # when modulating by same frequency of the waveform,
    # abs(sum(waveform)) will be a maximum
    center_frq = test_array.argmax('f_test').data 
    print "found center frequency at %0.5f MHz"%(center_frq/1e6)

    d.ft('t')
    d.setaxis('t', lambda x: x - center_frq)
    def apply_ph1(ph1,d_orig):
        retval = d_orig.C
        retval *= eixp(-1j*2*pi*ph1*retval.fromaxis('t')) # ph1 is cycles per SW
        d_ph = retval.C.sum('t')
        d_ph /= abs(d_ph)
        retval /= d_ph
        return retval
    fl.next('test time axis')
    t_shift_testvals = r_[-1e-6:1e-6:1000j]+pulse_start
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
    d.ft('t')
    transf = d['ch',1]/d['ch',0]
    impulse.ft('t')
    response = impulse*transf
    response.ift('t')
    response = response['t':transf_range]
    fl.plot(response.real, alpha=0.5, label='response, real')
    fl.plot(response.imag, alpha=0.5, label='response, imag')
    fl.plot(abs(response), alpha=0.3, linewidth=3, label='response, abs')
    decay = d['ch',1].C
    decay.ift('t')
    fl.next('Plotting the decay slice')
    fl.plot(abs(decay),alpha=0.2,label='Phased analytic reflection')
    max_time = decay.getaxis('t')[list(abs(decay).data).index(amax(abs(decay).data))]
    decay.ft('t')
    decay *= exp(1j*2*pi*max_time*decay.fromaxis('t'))
    decay.ift('t')
    fl.plot(abs(decay),':',alpha=0.2,label='Shifted phased analytic reflection')
    decay = abs(decay)['t':(0,6e-6)]
    fl.plot(decay,':',c='k',label='Decay slice')
    fl.next('Fitting decay %s'%id_string)
    x = decay.getaxis('t')
    ydata = decay.data
    fl.plot(x,ydata, alpha=0.2, human_units=False)
    fitfunc = lambda p, x: p[0]*exp(-x*2*pi*center_frq*(2*p[1]))
    fl.plot(x, fitfunc(r_[0.1,1.0],x), ':', label='initial fit, Q=30', human_units=False)
    errfunc = lambda p_arg, x_arg, y_arg: fitfunc(p_arg, x_arg) - y_arg
    if date == '181103':
        p0 = [0.5,100.0]
    elif date == '200110':
        p0 = [0.1,40.0]
    p1, success = leastsq(errfunc, p0[:], args=(x, ydata))
    print success
    Q = 1./p1[1]
    x_fit = linspace(x.min(), x.max(), 5000)
    fl.plot(x_fit, fitfunc(p1, x_fit),':',c='k', label='final fit, Q=%d'%Q)
    xlabel(r't / $s$')
    ylabel(r'Amplitude / $V$')
    print "Q:",Q
fl.show();quit()
