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
        ]:
    filename = date+'_'+id_string+'.h5'
    nodename = 'this_capture'

    s = nddata_hdf5(filename+'/'+nodename,
            directory = getDATADIR(exp_type='test_equip'))
    #s.reorder('ch','ph1','ph2','average','t')
    if shift_time:
        s = s.mean('average',return_error=False)
        s1 = s['ch',1] # pull ref ch
        s1 = s1['t':(0,12e-6)] # slice out all but 90 pulse
        s1 = abs(s1)
        s1.ft('t',shift=True)
        s1 = s1['t':(0,None)]
        s1.ift('t')
        fl.next('check')
        fl.plot(s1['ph1',0]['ph2',0])
        print ndshape(s1)
        pulse_slice_list = []
        for ph2 in xrange(0,2):
            for ph1 in xrange(4):
                pulse_slice_list = (s1['ph1',ph1]['ph2',ph2]).contiguous(lambda x: x>0.1*x.data.max())
                print pulse_slice_list
                for x in xrange(len(pulse_slice_list)):
                    s1['ph1',ph1]['ph2',ph2]['t':tuple(pulse_slice_list[x])] = 0
                time_values = s1['ph1',ph1]['ph2',ph2].fromaxis('t')
                print (ndshape(time_values)['t'])
                print time_values.sum(['t'])
                time_avg = sum(time_values['t'])/ndshape(time_values)['t']
                print "****ph1=",ph1,"ph2=",ph2,"****"
                print ndshape(s1)
                print time_avg
                #print "ph1=%d, ph2=%d"%(ph1,ph2)+" pulse slice=",pulse_slice
        quit()
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
        s.setaxis('t',lambda x: x-14.4247e6)
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

