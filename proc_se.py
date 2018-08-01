from pyspecdata import *
from pyspecdata.plot_funcs.image import imagehsv
import os
import sys
import matplotlib.style
import matplotlib as mpl
import argparse
#import logging

mpl.rcParams['image.cmap'] = 'jet'
fl = figlist_var()
#init_logging(level='debug')

raw_input("Did you set max_window argument correctly??")

parser = argparse.ArgumentParser(description='basic command-line options')
parser.add_argument('--window', '-w',
        help='the maximum size of the window that encompasses all the pulses',
        default=15e-6,
        type=float,
        dest='max_window')
parser.add_argument('--carrier', '-c',
        help='the carrier frequency',
        default=14.4289e6,
        type=float,
        dest='carrier_f')
args = parser.parse_args(sys.argv[1:])
#print args.max_window # this would work
globals().update(vars(args)) # this directly inserts the info above into
#                              namespace of global variables

for date,id_string,numchan,indirect_range in [
        #('180712','SE_exp',2)
        #('180712','SE_exp_2',2)
        #('180712','SE_exp_3',2)
        #('180713','SE_exp',2)
        #('180714','SE_exp',2), # 25 cycle measurement, B0 = 3395.75 G
        #('180714','SE_exp_offres',2) # 25 cycle measurement, B0 = 3585.85 G 
        #('180716','SE_test',2) # 1 cycle measurement with 8x GDS avg, B0 = 3395.75 G
        #('180716','SE_test_2',2) # 1 cycle measurement with 4x GDS avg, B0 = 3395.75 G
        #('180720','nutation_control',2)
        #('180723','nutation_control',2)
        #('180723','se_nutation',2,linspace(1.13e-6,6.13e-6,20))
        #('180723','se_nutation_2',2,linspace(1.5e-6,15e-6,40))
        #('180724','check_field',2,None),
        #('180724','check_field_2',2,None)
        #('180724','se_nutation',2,linspace(3.25e-6,15.25e-6,10))
        #('180724','90_nutation_control',2,linspace(1e-6,50e-6,5))
        #('180724','90_nutation',2,linspace(1e-6,50e-6,25)) # use -w 60e-6
        ('180725','90_nutation',2,linspace(1e-6,30e-6,30)) # use -w 60e-6
        #('180725','90_nutation_focused',2,linspace(6e-6,9e-6,30))
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
    logger.info("*** Code for phase cycling based on 'fix_phase_cycling_180712.py' ***")
    logger.info("WARNING: Need to define time slices for pulses on a by-dataset basis ***")

    s_raw = s.C.reorder('t',first=False)

    s.ft('t',shift=True)
    s = s['t':(0,None)]
    s.setaxis('t',lambda f: f-carrier_f)
    s.ift('t')

    single_90 = True 
    confirm_triggers = False 
    #{{{ confirm that different phases trigger differently due to differing rising edges
    if confirm_triggers:
        print ndshape(s)
        print ndshape(s_raw)
        subset = s['ch',1]['t':(1e-6,100e-6)]
        fl.next('raw data')
        if not single_90:
            fl.plot(s_raw['ch',1]['indirect',0]['ph2',0].reorder('t').real)
            onephase = subset.C.smoosh(['ph2','indirect'], noaxis = True, dimname='repeat').reorder('t')
            onephase_raw = s_raw['ch',1].C.smoosh(['ph2','indirect'], noaxis=True, dimname='repeat').reorder('t')
            print "dimensions of re-grouped raw data",ndshape(onephase_raw)
        if single_90:
            fl.plot(s_raw['ch',1]['indirect',-1].reorder('t').real)
            onephase = subset.C.reorder('t')
            onephase.rename('indirect','repeat')
            onephase_raw = s_raw['ch',1].C.reorder('t')
            onephase_raw.rename('indirect','repeat')
        colors = ['r','g','b','c']
        for k in xrange(ndshape(onephase)['ph1']):
            for j in xrange(ndshape(onephase)['repeat']):
                fl.next('compare rising edge')
                # need to define time slice for rising edge
                fl.plot(abs(onephase['repeat',j]['t':(26.2e-6,26.6e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
                fl.next('compare falling edge')
                # need to define time slice for falling edge
                fl.plot(abs(onephase['repeat',j]['t':(26.2e-6,26.6e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
                fl.next('compare rising edge, raw')
                fl.plot((onephase_raw['repeat',j]['t':(27.1e-6,27.9e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
                fl.next('compare falling edge, raw')
                fl.plot((onephase_raw['repeat',j]['t':(27.1e-6,27.9e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
        print ndshape(onephase)
        #}}}
    #{{{ shifting the axis so that 0 is centered on the pulses
    # before we even slice, we need an idea of where the pulse is
    def average_time(d):
        pulse_slice = d['ch',1].real
        normalization = (pulse_slice**2).integrate('t')
        return (pulse_slice**2 * pulse_slice.fromaxis('t')).integrate('t')/normalization
    if single_90:
        avg_t = average_time(s_raw['t':(0e-6,30e-6)]).data.mean()
    if not single_90:
        avg_t = average_time(s_raw['t':(6.5e-6,9.3e-6)]).data.mean()
    pulse_slice = s_raw['t':(avg_t-max_window/2,avg_t+max_window/2)]
    #{{{ NOTE: make sure that pulse_slice includes each pulse during a nutation measurement
        # you can test that with the following:
    #fl.image(pulse_slice)
    #fl.show();quit()
    #}}}
    avg_t = average_time(pulse_slice)
    print avg_t
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
    analytic = s_raw.C.ft('t')['t':(13e6,16e6)]
    analytic.setaxis('t',lambda f: f-carrier_f)
    analytic.set_units('indirect','s')
    phase_factor = analytic.fromaxis('t',lambda x: 1j*2*pi*x)
    phase_factor *= avg_t
    #     this time, optionally include the Cavanagh shifts
    if is_nutation:
        logger.debug(strm('the nutation axis is',analytic.getaxis('indirect')))
        # we want to move forward by (2/pi-1/2)*t90
        logger.debug(strm('correction before pulse shift',phase_factor))
        phase_factor += -1j*2*pi*(2/pi-0.5)*analytic.fromaxis('indirect')*analytic.fromaxis('t')
        logger.debug(strm('and after pulse shift',phase_factor))
    analytic *= exp(phase_factor)
    analytic.ift('t')
    # }}}
    #{{{ checking phase shifted trigger
    if confirm_triggers:
        if not single_90:
            onephase_raw_shift = s_raw['ch',1].C.smoosh(['ph2','indirect'],noaxis=True,dimname='repeat').reorder('t')
            onephase_raw_shift.name('Amplitude').set_units('V')
        if single_90:
            onephase_raw_shift = s_raw['ch',1].C.reorder('t')
            onephase_raw_shift.rename('indirect','repeat')
        for k in xrange(ndshape(onephase_raw)['ph1']):
            for j in xrange(ndshape(onephase_raw)['repeat']):
                fl.next('compare rising edge: uncorrected')
                fl.plot((onephase_raw_shift['repeat',j]['ph1',k]['t':(-1.4e-6,-1.1e-6)].C.reorder('t',first=True)+2*k),color=colors[k],alpha=0.3)
                fl.next('compare falling edge: uncorrected')
                fl.plot((onephase_raw_shift['repeat',j]['ph1',k]['t':(1.0e-6,1.4e-6)].C.reorder('t',first=True)+2*k),color=colors[k],alpha=0.3)
        raw_corr = s_raw.C.ft('t')
        phase_factor = raw_corr.fromaxis('t',lambda x: 1j*2*pi*x)
        phase_factor *= avg_t
        raw_corr *= exp(phase_factor)
        raw_corr.ift('t',pad=30*1024)
        if not single_90:
            onephase_rawc = raw_corr['ch',1].C.smoosh(['ph2','indirect'],noaxis=True, dimname='repeat').reorder('t')
        if single_90:
            onephase_rawc = raw_corr['ch',1].C.reorder('t')
            onephase_rawc.rename('indirect','repeat')
        for k in xrange(ndshape(onephase_rawc)['ph1']):
            for j in xrange(ndshape(onephase_rawc)['repeat']):
                fl.next('compare rising edge: corrected')
                fl.plot(onephase_rawc['repeat',j]['ph1',k]['t':(-1.4e-6,-1.1e-6)].C.reorder('t',first=True),color=colors[k],alpha=0.3)
                fl.next('compare falling edge: corrected')
                fl.plot(onephase_rawc['repeat',j]['ph1',k]['t':(1.0e-6,1.4e-6)].C.reorder('t',first=True),color=colors[k],alpha=0.3)
     #}}}
    # with time-shifted, phase corrected raw data, now take analytic
    # measured phase is phase of each 90 after time-shifting and phase correcting
    # set the phase of the 90 pulse for EACH INDIVIDUAL SCAN to make sure it's correct
    measured_phase = analytic['t':(-max_window/2,max_window/2)].mean('t',return_error=False)
    measured_phase /= abs(measured_phase)
    logger.info(strm("measured phase",measured_phase))
    # expected phase is how we expect the phases to cycle, and how it is programmed in the pulse sequence
    expected_phase = nddata(exp(r_[0,1,2,3]*pi/2*1j),[4],['ph1'])
    # phase correcting analytic signal by difference between expected and measured phases
    analytic *= expected_phase/measured_phase
    print ndshape(analytic)
    analytic.reorder(['indirect','t'],first=False)
    print ndshape(analytic)
    fl.next('analytic signal, ref ch')
    fl.image(analytic)
    fl.next('coherence domain, ref ch')
    if not single_90:
        coherence_domain = analytic.C.ift(['ph1','ph2'])
    if single_90:
        coherence_domain = analytic.C.ift(['ph1'])
    fl.image(coherence_domain['ch',1])
    s_analytic = analytic['ch',0].C
    if not single_90:
        s_analytic.ift(['ph1','ph2'])
    if single_90:
        s_analytic.ift(['ph1'])
    fl.next('coherence, sig ch, t domain')
    fl.image(s_analytic)
    print ndshape(s_analytic)
    s_analytic.ft('t')
    fl.next('coherence, sig ch, f domain')
    fl.image(s_analytic)
    s_analytic.ift('t')
    if not single_90:
        signal = s_analytic['ph1',1]['ph2',0]
    if single_90:
        signal = (s_analytic['ph1',-1])
    fl.next(r'$\mid$signal(t)$\mid$ as function of $\tau_{90}$')
    signal.rename('indirect',r'$\tau_{90}$')
    fl.image(abs(signal)['t':(35e-6,None)])
    fl.show();quit()
