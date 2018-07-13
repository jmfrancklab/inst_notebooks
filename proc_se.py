from pyspecdata import *
from pyspecdata.plot_funcs.image import imagehsv
import os
import sys
import matplotlib.style
import matplotlib as mpl

mpl.rcParams['image.cmap'] = 'jet'
fl = figlist_var()

carrier_f = 14.4247e6

for date,id_string,numchan in [
        #('180711','SE_phcyc_control',2)
        #('180712','SE_phcyc_test',2)
        #('180712','SE_phcyc_test_2',2)
        ('180712','SE_phcyc_test_3',2)
        ]:
    filename = date+'_'+id_string+'.h5'
    nodename = 'this_capture'

    s = nddata_hdf5(filename+'/'+nodename,
            directory = getDATADIR(exp_type='test_equip'))
    print "*** Current version based on 'fix_phase_cycling_180712.py' ***"
    print "WARNING: Need to define time slices for pulses on a by-dataset basis ***"
    raw_input("Enter to proceed")
    s.set_units('t','s')
    s_raw = s.C.reorder('t',first=False)

    #{{{ confirm that different phases trigger differently due to differing rising edges
    fl.next('raw data')
    fl.plot(s_raw['ch',1]['average',0]['ph2',0]['t':(24e-6,30e-6)].reorder('t').real)
    print ndshape(s)
    print ndshape(s_raw)

    s.ft('t',shift=True)
    s = s['t':(0,None)]
    s.setaxis('t',lambda f: f-carrier_f)
    s.ift('t')

    fl.next('phcyc')
    # subset of interest in the data, undergoes processing to analytic signal
    subset = s['ch',1]['t':(20e-6,100e-6)]
    fl.image(subset,black=True)
    onephase = subset.C.smoosh(['ph2','average'], noaxis = True, dimname='repeat').reorder('t')
    print "dimensions of data subset of interest",ndshape(onephase)
    # perform same analysis used on subset for raw data, to compare
    onephase_raw = s_raw['ch',1].C.smoosh(['ph2','average'], noaxis=True, dimname='repeat').reorder('t')
    print "dimensions of re-grouped raw data",ndshape(onephase_raw)
    colors = ['r','g','b','c']
    for k in xrange(ndshape(onephase)['ph1']):
        for j in xrange(ndshape(onephase)['repeat']):
            fl.next('compare rising edge')
            # need to define time slice for rising edge
            fl.plot(abs(onephase['repeat',j]['t':(24.85e-6,25e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
            fl.next('compare falling edge')
            # need to define time slice for falling edge
            fl.plot(abs(onephase['repeat',j]['t':(27.4e-6,27.8e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
            fl.next('compare rising edge, raw')
            fl.plot((onephase_raw['repeat',j]['t':(24.85e-6,25e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
            fl.next('compare falling edge, raw')
            fl.plot((onephase_raw['repeat',j]['t':(27.4e-6,27.8e-6)]['ph1',k].C.reorder('t',first=True)),color=colors[k],alpha=0.3)
    print ndshape(onephase)
    # the above should confirm that pulses are triggered differently due to their different rising edges
    #}}}
    #{{{ applying time-shift (i.e., defining new, more convenient x-axis below)
    # note, pulse length used below is manually determined
    pulse_slice = s_raw['t':(24.87e-6,27.65e-6)]['ch',1].real
    normalization = (pulse_slice**2).integrate('t')
    # this creates an nddata of the time averages for each 90 pulse
    average_time = (pulse_slice**2 * pulse_slice.fromaxis('t')).integrate('t')/normalization
    average_time.reorder('average',first=False)
    # shift the time axis down by the average time, so that 90 is centered around t=0
    s_raw.setaxis('t', lambda t: t-average_time.data.mean())
    # check that this centers 90 around 0 on time axis
    print "*** Check that time-shifted data plots 90 pulse around 0 ***"
    fl.next('time-shifted data')
    fl.image(s_raw)
    #}}}

    pulse_slice = s_raw['t':(-1.6e-6,1.6e-6)]['ch',1].real
    # re-determine nddata of the time averages for the newly centered data
    average_time = (pulse_slice**2 * pulse_slice.fromaxis('t')).integrate('t')/normalization
    average_time.reorder('average',first=False)
    # take analytic, and apply phase correction based on the time averages 
    analytic = s_raw.C.ft('t',shift=True)['t':(0,None)]
    analytic.setaxis('t',lambda f: f-carrier_f)
    phase_factor = analytic.fromaxis('t',lambda x: 1j*2*pi*x)
    phase_factor *= average_time
    phase_factor.run(lambda x: exp(x))
    analytic *= phase_factor
    analytic.ift('t')
    # verify that we have phased the measured signal
    fl.next('analytic signal, phased, time domain')
    fl.image(analytic)

    # beginning phase correction now
    # note, this may be the same as the raw signal plotted in beginning of program
    onephase_raw_shift = s_raw['ch',1].C.smoosh(['ph2','average'],noaxis=True,dimname='repeat').reorder('t')
    for k in xrange(ndshape(onephase_raw)['ph1']):
        for j in xrange(ndshape(onephase_raw)['repeat']):
            fl.next('compare rising edge: uncorrected')
            fl.plot((onephase_raw_shift['repeat',j]['ph1',k]['t':(-1.5e-6,-1.1e-6)].C.reorder('t',first=True)+2*k),color=colors[k],alpha=0.3)
            fl.next('compare falling edge: uncorrected')
            fl.plot((onephase_raw_shift['repeat',j]['ph1',k]['t':(1.1e-6,1.5e-6)].C.reorder('t',first=True)+2*k),color=colors[k],alpha=0.3)
    raw_corr = s_raw.C.ft('t',shift=True)
    # sign on 1j matters here, difference between proper cycling or off cycling
    phase_factor = raw_corr.fromaxis('t',lambda x: 1j*2*pi*x)
    phase_factor *= average_time
    phase_factor.run(lambda x: exp(x))
    raw_corr *= phase_factor
    # here zero filling or else signal amplitude will vary due to changes made in the f dimension 
    raw_corr.ift('t',pad=30*1024)
    onephase_rawc = raw_corr['ch',1].C.smoosh(['ph2','average'],noaxis=True, dimname='repeat').reorder('t')
    print "*** shape of raw, corrected re-grouped data ***"
    print ndshape(onephase_rawc)
    for k in xrange(ndshape(onephase_rawc)['ph1']):
        for j in xrange(ndshape(onephase_rawc)['repeat']):
            fl.next('compare rising edge: corrected')
            fl.plot(onephase_rawc['repeat',j]['ph1',k]['t':(-1.5e-6,-1.1e-6)].C.reorder('t',first=True),color=colors[k],alpha=0.3)
            fl.next('compare falling edge: corrected')
            fl.plot(onephase_rawc['repeat',j]['ph1',k]['t':(1.1e-6,1.5e-6)].C.reorder('t',first=True),color=colors[k],alpha=0.3)
    
    # with time-shifted, phase corrected raw data, now take analytic
    analytic = raw_corr['ch',1].C.ft('t')['t':(0,15.5e6)].setaxis('t', lambda f: f-carrier_f).ift('t').reorder(['average','t'],first=False)
    # measured phase is the result obtained from data after time-shifting and phase correcting
    measured_phase = analytic['t':(-2e6,2e6)].mean('t',return_error=False).mean('ph2',return_error=True).mean('average',return_error=True)
    measured_phase /= abs(measured_phase)
    # expected phase is how we expect the phases to cycle, and how it is programmed in the pulse sequence
    expected_phase = nddata(exp(r_[0,1,2,3]*pi/2*1j),[4],['ph1'])
    # phase correcting analytic signal by difference between expected and measured phases
    analytic *= expected_phase/measured_phase
    fl.next('analytic signal')
    fl.image(analytic['t':(-2e-6,75e-6)])
    # switch to coherence domain
    fl.next('coherence domain')
    coherence_domain = analytic.C.ift(['ph1','ph2'])
    fl.image(coherence_domain['t':(-2e-6,75e-6)])
fl.show()
quit()
