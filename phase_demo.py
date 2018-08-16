from pyspecdata import *
# if we are on resonance, the Hermitian test is a good test of ph0, but not really ph1
# the sum abs real test is a good test of how to phase an FID, but doesn't work
# if you start to include the FID mirror when doing an echo
with figlist_var() as fl:
    use_echo = False # a default, do not set here
    construct_freq_domain = False
    w = 10.
    if construct_freq_domain:
        # {{{ construct in frequency domain
        SW = 100.
        t = r_[-SW/2:SW/2:501j]
        d = nddata(w/(1j*2*pi*t+w),['t']).labels('t',t)
        # }}}
        fl.next('show time domain')
        d.set_ft_prop('t',['time','not','aliased'],True)
        d.ift('t')
        fl.plot(d)
        d.ft('t')
    else:
        # {{{ construct in time domain
        offset = 0.
        use_echo = True
        if use_echo:
            d = nddata(r_[-5:5:1001j],'t')
            d = exp(-abs(d)*w+1j*2*pi*offset*d.fromaxis('t'))
        else:
            d = nddata(r_[0:5.:501j],'t')
            d = exp(-d*w+1j*2*pi*offset*d.fromaxis('t'))
            d.data[0] /= 2 # comes from the definition of a discrete heaviside
            #                checked that this is not pyspecdata-specific
            #                without this, I get a baseline
        fl.next('show FID')
        fl.plot(d)
        SW = 1./diff(d.getaxis('t')[r_[0,1]]).item()
        d.ft('t',shift=True)
        # }}}
    fl.next('show frequency')
    fl.plot(d.real)
    fl.plot(d.imag)
    # {{{ construct the phases that we use to mess things up
    x = nddata(r_[-0.5:0.5:25j],'ph0')
    ph0 = exp(1j*2*pi*x)
    x = nddata(r_[-5./SW:5./SW:25j],'ph1')
    ph1 = 1j*2*pi*x
    d *= ph0
    d *= exp(ph1*d.fromaxis('t'))
    # }}}
    d.ift('t')
    # in the following, a None slice drops the last point, which is problematic!
    d_absreal = d.C
    if use_echo:
        d_absreal = d['t',lambda x: x>=0].C
        d_absreal.data[0] /= 2
    d_absreal.ft('t')
    fl.next('abs real cost')
    d_absreal.data = abs(d_absreal.data.real)
    d_absreal.sum('t')
    fl.image(d_absreal)
    if not construct_freq_domain:# only the time-domain construction is symmetric
        fl.next('hermitian cost')
        d_herm = d.C
        d_herm.data -= conj(d_herm.data[::-1])
        d_herm.data = abs(d_herm.data)**2
        d_herm.sum('t')
        fl.image(d_herm)
