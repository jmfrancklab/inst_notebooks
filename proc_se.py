from pyspecdata import *
from pyspecdata.plot_funcs.image import imagehsv
import os
import sys
import matplotlib.style
import matplotlib as mpl

mpl.rcParams['image.cmap'] = 'jet'
fl = figlist_var()

shift_time = True

for date,id_string,numchan in [
        #('180708','spin_echo',2),
        ('180710','SE_test_phcyc_2',2),
        #('180711','SE_phcyc_control',2),
        #('180711','SE_phcyc_test',2),
        ]:
    filename = date+'_'+id_string+'.h5'
    nodename = 'this_capture'

    s = nddata_hdf5(filename+'/'+nodename,
            directory = getDATADIR(exp_type='test_equip'))
    #s.reorder('ch','ph1','ph2','average','t')
    if shift_time:
        s = s.mean('average',return_error=False)
        s1 = s['ch',1] # pull ref ch
        s1.set_units('t','s')
        s1.name('Amplitude $/$ $V$')
                #{{{ will plot time domain signal for each phase, before manipulation
        for ph2 in xrange(0,2):
            for ph1 in xrange(4):
                print ph1,ph2,ndshape(s1['ph1',ph1]['ph2',ph2])
                #fl.next('Phase Cycled Spin Echo, Before Time Shift')
                #fl.plot(s1['ph1',ph1]['ph2',ph2],label='ph1 %d, ph2 %d'%(ph1,ph2),alpha=0.25)
                #}}}
        # Calculating analytic signal
        s1.ft('t',shift=True)
        s1 = s1['t':(0,None)]
        s1.ift('t')
        s1 = abs(s1)
        # Slice for the 90 pulse
        s1 = s1['t':(0,15e-6)]
        print ndshape(s1)
        #{{{ block for calculating time shift
        pulse_slice_list = []
        time_slice_list = []
        for ph2 in xrange(0,2):
            for ph1 in xrange(4):
                #{{{ use to check threshold is appropriate for pulse slice
                #fl.next('Checking threshold')
                #fl.plot(s1['ph1',ph1]['ph2',ph2])
                #}}}
                pulse_slice_list = (s1['ph1',ph1]['ph2',ph2]).contiguous(lambda x: x > 0.05*x.data.max())
                print "Pulse slices for time shifting"
                print pulse_slice_list
                # calculating average time for each 90 pulse
        for x in xrange(len(pulse_slice_list)):
            temp = tuple(pulse_slice_list[x])
            time_diff = temp[1] - temp[0]
            time_slice_list.append(time_diff)
        time_avg = sum(time_slice_list)/len(time_slice_list)
        print "**** time average to be applied for time shifting ***"
        print time_avg
            #}}}
        s1_shift = s['ch',1].C
        s1_shift.ft('t',shift=True)
        # performing the time shift (in the frequency domain)
        s1_shift *= s1_shift.fromaxis('t',lambda f: exp(-1j*2*pi*f*time_avg))
        s1_shift.ift('t')
        s1_shift.set_units('t','s')
        s1_shift.name('Amplitude $/$ $V$')
                #{{{ will plot time domain signal for each phase, time shifted
        for ph2 in xrange(0,2):
            for ph1 in xrange(4):
                print ph1,ph2,ndshape(s1_shift['ph1',ph1]['ph2',ph2])
                #fl.next('Phase Cycled Spin Echo, After Time Shift')
                #fl.plot(s1_shift['ph1',ph1]['ph2',ph2],label='ph1 %d, ph2 %d'%(ph1,ph2),alpha=0.25)
                #}}}
        s1_shift.ft('t')
        # filtering
        s1_shift = s1_shift['t':(0,15.5e6)]
        # mix down by carrier f 
        s1_shift.setaxis('t',lambda x: x - 14.43e6)
        s1_shift.ift('t')
        fl.next('ph1 ph2')
        fl.image(s1_shift)
        s1_noshift = s['ch',1].C
        s1_noshift.set_units('t','s')
        s1_noshift.name('Amplitude $/$ $V$')
        s1_noshift.ft('t')
        # filtering
        s1_noshift = s1_noshift['t':(0,15.5e6)]
        # mix down by carrier f 
        s1_noshift.setaxis('t',lambda x: x - 14.43e6)
        s1_noshift.ift('t')
        fl.next('ph1 ph2 no shift')
        fl.image(s1_noshift)
        s1_shift.ft(['ph1','ph2'])
        fl.next('ft ph1,ph2')
        fl.image(s1_shift)
        s1_noshift.ft(['ph1','ph2'])
        fl.next('ft ph1,ph2 no shift')
        fl.image(s1_noshift)
        fl.show()
        quit()
            #{{{ block for calculating zero-order correction
        shiftedp_slice_list = []
        shiftedt_slice_list = []
        for ph2 in xrange(0,2):
            for ph1 in xrange(4):
                #{{{ see comment below
                    # initially used this to re-calculate pulse length, but that is not needed
                    # since it should be the same as previous time average; however, this looks
                    # really weird
                #s1_shift.ft('t')
                #s1_shift = s1_shift['t':(0,None)]
                #s1_shift.ift('t')
                #s1_shift = abs(s1_shift)
                #s1_shift = s1_shift['t':(0,15e-6)]
                #fl.next('Checking threshold time shifted pulse')
                #fl.plot(s1_shift['ph1',ph1]['ph2',ph2])
                #}}}
                shiftedp_slice_list = (s1_shift['ph1',ph1]['ph2',ph2]).contiguous(lambda x: x > 0.5*x.data.max())
                print "Pulse slices for zero order phase correction"
                print shiftedp_slice_list
                # calculating average time for each time-shifted 90 pulse
        for x in xrange(len(shiftedp_slice_list)):
            temp = tuple(shiftedp_slice_list[x])
            time_diff = temp[1] - temp[0]
            shiftedt_slice_list.append(time_diff)
        time_avg = sum(shiftedt_slice_list)/len(shiftedt_slice_list)
        print "**** time average to be applied for zero order phase correction ****"
        print time_avg
            #}}}


    if not shift_time:
        s.reorder('ph1','ph2','average','t')
        s.set_units('t','s')
        print ndshape(s)
        s.mean('average',return_error=False) 
        # {{{ for 180709_spin_echo.h5 - only the last average slice has data, pull it
        #fl.next('raw data')
        #fl.image(s['average',0:-1])
        ##s = s['average',-1]
        # }}}
        print ndshape(s)
        #s.reorder('ph1','ph2','ch','t')
        s_shift = s.C
        s = abs(s)
        s.ft('t',shift=True)
        s = s['t':(0,None)]
        s.ift('t')
        for ph2 in xrange(0,2):
            for ph1 in xrange(4):
                print ph1,ph2,ndshape(s['ph1',ph1]['ph2',ph2])
                fl.next('analytic, unfiltered')
                fl.plot(s['ph1',ph1]['ph2',ph2],label='ph1 %d, ph2 %d'%(ph1,ph2),alpha=0.25)
        print "done printing"
        for ph1 in xrange(0,6,3):
            s_shift['ph1',ph1].setaxis('t',lambda x: x+0)
        s_shift = abs(s_shift)
        s_shift.ft('t',shift=True)
        s_shift = s_shift['t':(0,None)]
        s_shift.ift('t')
        for ph2 in xrange(0,2):
            for ph1 in xrange(4):
                print ph1,ph2,ndshape(s_shift['ph1',ph1]['ph2',ph2])
                fl.next('analytic, unfiltered, shifted')
                fl.plot(s_shift['ph1',ph1]['ph2',ph2],label='ph1 %d, ph2 %d'%(ph1,ph2),alpha=0.25)
        print 'this has worked'
        fl.show()
        quit()
        #for ph2 in xrange(0,2):
        #    for ph1 in xrange(4):
        #        fl.next('analytic, unfiltered freq domain')
        #        fl.plot(s['ph1',ph1]['ph2',ph2],alpha=0.1,linestyle=':')
        #s.ift('t')
        for ph2 in xrange(0,2):
            for ph1 in xrange(4):
                fl.next('analytic, unfiltered time domain')
                fl.plot(s['ph1',ph1]['ph2',ph2],alpha=0.1,linestyle=':')
                print "trying to plot"
                fl.show()
        quit()
        # band pass filtering
        #s['t':(None,10e6)] = 0
        #s['t':(20e6,None)] = 0
        s = s['t':(0,15.5e6)]
        # mixing down
            #{{{ the 0.33/4e-6 comes from looking at the low pass filtered,
            #       phase FT'd image, and seeing how the color following the pulses
            #       changes, which relays the coherence level difference via color plot (see
            #       doi:10.1063/1.3243850 for more details) -- for '180708_spin_echo.h5',
            #       the color changes from blue --> green, which indicates a shift of 2pi/3
            #       or 0.33; this is the phase shift for the 180 pulses. Best seen on ref ch.
            #}}}
        #s.setaxis('t',lambda x: x-14.5e6+0.33/4e-6)
        #s.setaxis('t',lambda x: x-14.5e6+0.33/4e-6)
        #s.setaxis('t',lambda x: x-14.4247e6-0.02/((2*2.63)*1e-6))
        s.setaxis('t',lambda x: x-14.4247e6-0.25/time_avg)
        print ndshape(s)
        s.ift('t')
        #s.ft(['ph1','ph2'])
        fl.next('filtered')
        fl.image(s['ch',1])
        #fl.next('filtered, cropped')
        #fl.image(s['ch',0].cropped_log())
        fl.show()
        quit()
        #fl.plot(s['ph1',0]['ph2',0])
        #fl.plot(s['ph1',1]['ph2',0])
        #fl.plot(s['ph1',2]['ph2',0])
        #fl.plot(s['ph1',3]['ph2',0])
        #fl.plot(s['ph1',0]['ph2',1])

