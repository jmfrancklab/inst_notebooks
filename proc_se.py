from pyspecdata import *
from pyspecdata.plot_funcs.image import imagehsv
import os
import sys
import matplotlib.style
import matplotlib as mpl

mpl.rcParams['image.cmap'] = 'BrBG'
fl = figlist_var()
init_logging(level='debug')

carrier_f = 14.4289e6
max_window = 15e-6 # the maximim size of the window that encompasses all the pulses

for date,id_string,numchan in [
        #('180712','SE_exp',2)
        #('180712','SE_exp_2',2)
        #('180712','SE_exp_3',2)
        #('180713','SE_exp',2)
        #('180714','SE_exp',2), # 25 cycle measurement, B0 = 3395.75 G
        #('180714','SE_exp_offres',2) # 25 cycle measurement, B0 = 3585.85 G 
        #('180716','SE_test',2) # 1 cycle measurement with 8x GDS avg, B0 = 3395.75 G
        #('180716','SE_test_2',2) # 1 cycle measurement with 4x GDS avg, B0 = 3395.75 G
        ('180720','nutation_control',2) # 1 cycle measurement with 4x GDS avg, B0 = 3395.75 G
        ]:
    filename = date+'_'+id_string+'.h5'
    nodename = 'this_capture'

    s = nddata_hdf5(filename+'/'+nodename,
            directory = getDATADIR(exp_type='test_equip'))
    s.set_units('t','s')
    logger.debug(strm('dimensions are:',ndshape(s)))
    is_nutation = False
    if 't_90' in s.dimlabels:
        s.rename('t_90','indirect')
        is_nutation = True
        logger.info('This is a nutation curve')
    if 'full_cyc' in s.dimlabels:
        s.rename('full_cyc','indirect')
    if 'average' in s.dimlabels:
        s.rename('average','indirect')
    logger.info("*** Current version based on 'fix_phase_cycling_180712.py' ***")
    logger.info("WARNING: Need to define time slices for pulses on a by-dataset basis ***")

    s_raw = s.C.reorder('t',first=False)

    s.ft('t',shift=True)
    s = s['t':(0,None)]
    s.setaxis('t',lambda f: f-carrier_f)
    s.ift('t')

    confirm_triggers = False
    if confirm_triggers:
        #{{{ confirm that different phases trigger differently due to differing rising edges
        fl.next('raw data')
        fl.plot(s_raw['ch',1]['indirect',0]['ph2',0].reorder('t').real)
        fl.show()
        quit()
        print ndshape(s)
        print ndshape(s_raw)
        #fl.next('phcyc')
        # subset of interest in the data, undergoes processing to analytic signal
        subset = s['ch',1]['t':(1e-6,100e-6)]
        #fl.image(subset,black=True)
        onephase = subset.C.smoosh(['ph2','indirect'], noaxis = True, dimname='repeat').reorder('t')
        print "dimensions of data subset of interest",ndshape(onephase)
        # perform same analysis used on subset for raw data, to compare
        onephase_raw = s_raw['ch',1].C.smoosh(['ph2','indirect'], noaxis=True, dimname='repeat').reorder('t')
        print "dimensions of re-grouped raw data",ndshape(onephase_raw)
        colors = ['r','g','b','c']
        for k in xrange(ndshape(onephase)['ph1']):
            for j in xrange(ndshape(onephase)['repeat']):
                fl.next('compare rising edge')
                # need to define time slice for rising edge
                fl.plot(abs(onephase['repeat',j]['t':(6.47267e-6,6.7e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
                fl.next('compare falling edge')
                # need to define time slice for falling edge
                fl.plot(abs(onephase['repeat',j]['t':(9e-6,9.24785e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
                fl.next('compare rising edge, raw')
                fl.plot((onephase_raw['repeat',j]['t':(6.47267e-6,6.7e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
                fl.next('compare falling edge, raw')
                fl.plot((onephase_raw['repeat',j]['t':(9e-6,9.24785e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
        print ndshape(onephase)
        #}}}
    #{{{ shifting the axis so that 0 is centered on the pulses
    # before we even slice, we need an idea of where the pulse is
    def average_time(d):
        pulse_slice = d['ch',1].real
        normalization = (pulse_slice**2).integrate('t')
        return (pulse_slice**2 * pulse_slice.fromaxis('t')).integrate('t')/normalization
    avg_t = average_time(s_raw['t':(0,50e-6)]).data.mean()
    logger.info(strm('average time of pulses',avg_t))
    pulse_slice = s_raw['t':(avg_t-max_window/2,avg_t+max_window/2)]
    # now that I have a better slice, redo the avg_t
    avg_t = average_time(pulse_slice)
    # this creates an nddata of the time averages for each 90 pulse
    logger.debug(strm('dimensions of average_time:',ndshape(avg_t)))
    # shift the time axis down by the average time, so that 90 is centered around t=0
    s_raw.setaxis('t', lambda t: t-avg_t.data.mean())
    fl.next('check that this centers 90 around 0 on time axis')
    fl.image(s_raw)
    #}}}
    # {{{ now, go ahead and shift each indirect data element relative to the
    # others, so their pulses line up
    # I'm going to do this twice, for maximum accuracy
    # notice that a lot of the code that was
    # here before is gathered into the "average_time" function above
    avg_t = average_time(s_raw['t':(-max_window/2,max_window/2)])
    # the first time I do this, just do it on the raw data
    s_raw.ft('t',shift=True)
    phase_factor = s_raw.fromaxis('t',lambda x: 1j*2*pi*x)
    phase_factor *= avg_t
    s_raw *= exp(phase_factor)
    s_raw.ift('t')
    # }}}
    # {{{ now that my rms noise average will be more balanced,
    #     redetermine the center here, and reshift the pulses next
    avg_t = average_time(s_raw['t':(-max_window/2,max_window/2)])
    s_raw.setaxis('t', lambda t: t-avg_t.data.mean())
    # }}}
    # {{{ since this is the last step, take the analytic signal
    #     and then apply the relative shifts again
    analytic = s_raw.C.ft('t')['t':(0,None)]
    analytic.setaxis('t',lambda f: f-carrier_f)
    phase_factor = analytic.fromaxis('t',lambda x: 1j*2*pi*x)
    phase_factor *= avg_t
    #     this time, optionally include the Cavanagh shifts
    if is_nutation:
        logger.info(strm('the nutation axis is',analytic.getaxis('indirect')))
        phase_factor *= 2*analytic.fromaxis('indirect')/pi
    analytic *= exp(phase_factor)
    analytic.ift('t')
    # }}}
    if confirm_triggers:
        # verify that we have phased the measured signal
        fl.next('analytic signal, phased, time domain (ref ch)')
        fl.image(analytic)

        # beginning phase correction now
        #{{{ plotting time domain uncorrected pulse edges
        # NOTE: this may be the same as the raw signal plotted in beginning of program
        onephase_raw_shift = s_raw['ch',1].C.smoosh(['ph2','indirect'],noaxis=True,dimname='repeat').reorder('t')
        onephase_raw_shift.name('Amplitude').set_units('V')
        for k in xrange(ndshape(onephase_raw)['ph1']):
            for j in xrange(ndshape(onephase_raw)['repeat']):
                fl.next('compare rising edge: uncorrected')
                fl.plot((onephase_raw_shift['repeat',j]['ph1',k]['t':(-1.4e-6,-1.1e-6)].C.reorder('t',first=True)+2*k),color=colors[k],alpha=0.3)
                fl.next('compare falling edge: uncorrected')
                fl.plot((onephase_raw_shift['repeat',j]['ph1',k]['t':(1.0e-6,1.4e-6)].C.reorder('t',first=True)+2*k),color=colors[k],alpha=0.3)
        #}}}
    if confirm_triggers:
        # if we want to display the correction to the raw data, we need to
        # reapply the same shift.  This is not necessary unless we're running with "confirm_triggers"
        raw_corr = s_raw.C.ft('t',shift=True)
        # sign on 1j matters here, difference between proper cycling or off cycling
        phase_factor = raw_corr.fromaxis('t',lambda x: 1j*2*pi*x)
        phase_factor *= avg_t
        #     this time, optionally include the Cavanagh shifts
        if is_nutation:
            logger.info(strm('the nutation axis is',analytic.getaxis('indirect')))
            phase_factor *= 2*analytic.fromaxis('indirect')/pi
        raw_corr *= exp(phase_factor)
        # here zero filling or else signal amplitude will vary due to changes made in the f dimension 
        raw_corr.ift('t',pad=30*1024)
        #{{{ plotting time domain corrected pulse edges
        if full_cyc:
            onephase_rawc = raw_corr['ch',1].C.smoosh(['ph2','full_cyc'],noaxis=True, dimname='repeat').reorder('t')
        if not full_cyc:
            onephase_rawc = raw_corr['ch',1].C.smoosh(['ph2','indirect'],noaxis=True, dimname='repeat').reorder('t')
        onephase_rawc.name('Amplitude').set_units('V')
        for k in xrange(ndshape(onephase_rawc)['ph1']):
            for j in xrange(ndshape(onephase_rawc)['repeat']):
                fl.next('compare rising edge: corrected')
                fl.plot(onephase_rawc['repeat',j]['ph1',k]['t':(-1.4e-6,-1.1e-6)].C.reorder('t',first=True),color=colors[k],alpha=0.3)
                fl.next('compare falling edge: corrected')
                fl.plot(onephase_rawc['repeat',j]['ph1',k]['t':(1.0e-6,1.4e-6)].C.reorder('t',first=True),color=colors[k],alpha=0.3)
        #}}}
    # with time-shifted, phase corrected raw data, now take analytic
    # measured phase is phase of each 90 after time-shifting and phase correcting
    # the following line was wrong for the general case -- we should set the
    # phase of the 90 pulse for EACH INDIVIDUAL SCAN to make sure it's correct
    measured_phase = analytic['t':(-max_window/2,max_window/2)].mean('t',return_error=False)
    measured_phase /= abs(measured_phase)
    logger.info(strm("measured phase",measured_phase))
    # expected phase is how we expect the phases to cycle, and how it is programmed in the pulse sequence
    expected_phase = nddata(exp(r_[0,1,2,3]*pi/2*1j),[4],['ph1'])
    # phase correcting analytic signal by difference between expected and measured phases
    analytic *= expected_phase/measured_phase
    fl.next('analytic signal, ref ch')
    fl.image(analytic)
    fl.show();exit()
    # switch to coherence domain
    fl.next('coherence domain, ref ch')
    coherence_domain = analytic.C.ift(['ph1','ph2'])
    fl.image(coherence_domain['t':(-2e-6,75e-6)])

    # apply same analysis as on reference ch to test ch
    s_analytic = raw_corr['ch',0].C
    print "ph1 axis:",s_analytic.getaxis('ph2')
    print "ph2 axis:",s_analytic.getaxis('ph1')
    # had difficult with setting axis
    s_analytic.setaxis('ph1', r_[0:4]*0.25)
    s_analytic.setaxis('ph2', r_[0:4:2]*0.25)
    s_analytic.setaxis('indirect', lambda x: x * 0.25)
    print "new ph1 axis:",s_analytic.getaxis('ph1')
    print "new ph2 axis:",s_analytic.getaxis('ph2')
    s_analytic.ft('t')
    s_analytic = s_analytic['t':(13e6,16e6)]
    s_analytic.setaxis('t', lambda f: f-carrier_f)
    s_analytic.ift('t')
    if full_cyc:
        s_analytic.reorder(['full_cyc','t'],first=False)
    if not full_cyc:
        s_analytic.reorder(['indirect','t'],first=False)
    s_analytic *= expected_phase/measured_phase
    s_analytic.ift(['ph1','ph2'])
    print ndshape(s_analytic)
    fl.next('coherence domain, test ch')
    fl.image(s_analytic)
    print "before average"
    print ndshape(s_analytic)
    #{{{ generating input-referred voltage
    ##gain_factor_dcasc12 = sqrt(114008.55204672)   #gain in units of V
    ##s_analytic /= gain_factor_dcasc12
    ##if full_cyc:
    ##    s_analytic.mean('full_cyc',return_error=False)
    if not full_cyc:
        s_analytic.mean('indirect',return_error=False)
    #s_analytic /= sqrt(8)
    #}}}
    #{{{ plotting time-domain coherent signal
    print "after average"
    print ndshape(s_analytic)
    s_analytic.name('Amplitude').set_units('V')
    for ph2 in xrange(ndshape(s_analytic)['ph2']):
        for ph1 in xrange(ndshape(s_analytic)['ph1']):
            fl.next(r'$\Delta_{c_{1}}$ = + %d, $\Delta_{c_{2}}$ = + %d'%(ph1,2*ph2))
            fl.plot(s_analytic['ph1',ph1]['ph2',ph2],alpha=0.4) # in order to see units
            #fl.plot(s_analytic['ph1',ph1]['ph2',ph2].real,alpha=0.4,label='real')
            #fl.plot(s_analytic['ph1',ph1]['ph2',ph2].imag,alpha=0.4,label='imag')
            xlim(100,None) #units of 1e-6 seconds
    #}}}
fl.show()
quit()

