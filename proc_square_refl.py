from pyspecdata import *
#import logging
#init_logging(level=logging.DEBUG)
#{{{ boolean statement for processing data before modification to generate chirp
#   that sets voltage of ref (CH1 of scope) and DUT (CH2 of scope) to same value
corrected_volt = True
#}}}
with figlist_var(filename='chirp.pdf') as fl:
#    fl.next('$S_{11}$ : phase', legend=True)
    expno=0
    for date, id_string,corrected_volt in [
            ('180806','pulse_reflection',True),
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
        d.ift('t')
        d.ft('t')
        # }}}
        # {{{   try the phasing trick on the pulse
        #       because the frequency domain should be causal and therefore a
        #       sum of lorentzians
        def apply_ph1(ph1,d_orig):
            retval = d_orig.C
            retval *= exp(-1j*2*pi*ph1*retval.fromaxis('t')) # ph1 is cycles per SW
            d_ph = retval.C.sum('t')
            d_ph /= abs(d_ph)
            retval /= d_ph
            return retval
        fl.next('test time axis')
        t_shift_testvals = r_[-1e-6:1e-6:1000j]+pulse_start
        cost = empty_like(t_shift_testvals)
        for j,t_shift in enumerate(t_shift_testvals):
            cost[j] = sum(abs(apply_ph1(t_shift,d['ch',0]).data.real))
        fl.plot(t_shift_testvals,cost)
        # }}}
        expno += 1 
