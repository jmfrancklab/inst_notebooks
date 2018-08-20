from pyspecdata import *
from pyspecdata.plot_funcs.image import imagehsv
import os
import sys
import matplotlib.style
import matplotlib as mpl

mpl.rcParams['image.cmap'] = 'jet'
fl = figlist_var()

carrier_f = 14.4289e6

check_time = False 
for date,id_string,numchan,field_axis,cycle_time, in [
        #('180717','SE_sweep_3',2,linspace(3390,3400,420*4),168),
        #('180718','SE_sweep',2,linspace((3395-25/2),(3395+25/2),1050*4),168),
        #('180718','SE_sweep_2',2,linspace((3407-15/2),(3407+15/2),654*4),int(21.3*8)) 
        #('180718','SE_sweep_3',2,linspace((3407-3/2),(3407+3/2),1296*4),int(21.129*8)) 
        #('180718','SE_sweep_4',2,linspace((3407.05-0.1/2),(3407.05+0.1/2),425*4),int(21.3125*8)) 
        #('180719','SE_sweep',2,linspace((3407.3-1.0/2),(3407.3+1.0/2),425*4),int(20.9375*8)) 
        #('180719','SE_sweep_2',2,linspace((3407.3-0.1/2),(3407.3+0.1/2),420*4),int(20.975*8)), 
        #('180719','SE_sweep_3',2,linspace((3407.4-0.1/2),(3407.4+0.1/2),420*4),int(21.875*8)) 
        #('180725','SE_sweep',2,linspace((3407.30-500./2),(3407.30+500./2),2340*4),int(21.865*8)) 
        ('180726','SE_sweep',2,linspace((3407.30-50./2),(3407.30+50./2),2340*4),int(21.8325*8)) 
        ]:
    filename = date+'_'+id_string+'.h5'
    nodename = 'this_capture'
    #{{{ for checking time difference between captures
    # use this to find cycle_time variable, which will print if no AFG error is found
    if check_time:
        timing_node = 'timing_data'
        q = nddata_hdf5(filename+'/'+timing_node,
                directory = getDATADIR(exp_type='test_equip'))
        big_delay = False
        time_diff_list = []
        for x in xrange(ndshape(q)['t']):
            try :
                time_diff = q['t',x+1].data - q['t',x].data
            except :
                time_diff = q['t',x].data - q['t',x-1].data
            time_diff_list.append(time_diff)
            if time_diff > 25:
                big_delay = True
                print "\n\t*** *** ***"
                print "AFG error"
                print "\t*** *** ***\n"
            #print time_diff
        if not big_delay:
            time_diff_nddata = nddata(time_diff_list,[-1],['t']).labels('t',r_[0:len(time_diff_list)])
            avg_delay = time_diff_nddata.mean('t',return_error=False).data
            print "Did not find AFG error"
            print "Average delay between phase cycling steps:",avg_delay,"s"
        quit()
    #}}}
    if not check_time :
        s = nddata_hdf5(filename+'/'+nodename,
                directory = getDATADIR(exp_type='test_equip'))
        s.set_units('t','s')
        s.setaxis('ph1', r_[0:4]*0.25)
        s.setaxis('ph2', r_[0:4:2]*0.25)
        #s.setaxis('full_cyc',r_[0:ndshape(s)['full_cyc']]*0.25)
        s_raw = s.C.reorder('t',first=False)

        s.ft('t',shift=True)
        s = s['t':(0,None)]
        s.setaxis('t',lambda f: f-carrier_f)
        s.ift('t')

        fl.next('raw data') 
        fl.plot(s_raw['ch',1]['full_cyc',0]['ph2',0].reorder('t').real)
        #{{{ applying time-shift (i.e., defining new, more convenient x-axis below)
        # note, pulse length used below is manually determined
        pulse_slice = s_raw['t':(6.47267e-6,14.1078e-6)]['ch',1].real
        normalization = (pulse_slice**2).integrate('t')
        # this creates an nddata of the time averages for each 90 pulse
        average_time = (pulse_slice**2 * pulse_slice.fromaxis('t')).integrate('t')/normalization
        average_time.reorder('full_cyc',first=False)
        # shift the time axis down by the average time, so that 90 is centered around t=0
        s_raw.setaxis('t', lambda t: t-average_time.data.mean())
        # NOTE: check that this centers 90 around 0 on time axis
        #fl.next('time-shifted data')
        #fl.image(s_raw)
        #}}}
        pulse_slice = s_raw['t':(-4e-6,4e-6)]['ch',1].real
        # re-determine nddata of the time averages for the newly centered data
        average_time = (pulse_slice**2 * pulse_slice.fromaxis('t')).integrate('t')/normalization
        print average_time
        average_time.reorder('full_cyc',first=False)
        # take analytic, and apply phase correction based on the time averages 
        analytic = s_raw.C.ft('t',shift=True)['t':(0,None)]
        analytic.setaxis('t',lambda f: f-carrier_f)
        phase_factor = analytic.fromaxis('t',lambda x: 1j*2*pi*x)
        phase_factor *= average_time
        phase_factor.run(lambda x: exp(x))
        analytic *= phase_factor
        analytic.ift('t')
        # verify that we have phased the measured signal
        #fl.next('analytic signal, phased, time domain (ref ch)')
        #fl.image(analytic)

        # beginning phase correction now
        raw_corr = s_raw.C.ft('t',shift=True)
        # sign on 1j matters here, difference between proper cycling or off cycling
        phase_factor = raw_corr.fromaxis('t',lambda x: 1j*2*pi*x)
        phase_factor *= average_time
        phase_factor.run(lambda x: exp(x))
        raw_corr *= phase_factor
        # here zero filling or else signal amplitude will vary due to changes made in the f dimension 
        raw_corr.ift('t',pad=30*1024)
        # with time-shifted, phase corrected raw data, now take analytic
        # measured phase is phase of each 90 after time-shifting and phase correcting
        analytic = raw_corr['ch',1].C.ft('t')['t':(0,16e6)].setaxis('t', lambda f: f-carrier_f).ift('t').reorder(['full_cyc','t'],first=False)
        measured_phase = analytic['t':(-4e-6,4e-6)].mean('t',return_error=False).mean('ph2',return_error=True).mean('full_cyc',return_error=True)
        measured_phase /= abs(measured_phase)
        print "measured phase"
        print measured_phase
        # expected phase is how we expect the phases to cycle, and how it is programmed in the pulse sequence
        expected_phase = nddata(exp(r_[0,1,2,3]*pi/2*1j),[4],['ph1'])
        # phase correcting analytic signal by difference between expected and measured phases
        analytic *= expected_phase/measured_phase
        #fl.next('analytic signal, ref ch')
        #fl.image(analytic['t':(-2e-6,75e-6)])
        # switch to coherence domain
        fl.next('coherence domain, ref ch')
        coherence_domain = analytic.C.ift(['ph1','ph2'])
        fl.image(coherence_domain['t':(-2e-6,75e-6)])

        # apply same analysis as on reference ch to test ch
        s_analytic = raw_corr['ch',0].C.ft('t')['t':(13e6,16e6)].setaxis('t', lambda f: f-carrier_f).ift('t').reorder(['full_cyc','t'],first=False)
        s_analytic *= expected_phase/measured_phase
        #s_analytic.ift(['ph1','ph2'])
        #fl.next('Testing coherence domain')
        #fl.image(s_analytic)
        #fl.show()
        #quit()
        s_analytic.name('Amplitude').set_units('V')
        #{{{ here plotting sweep data several ways
        s_analytic.rename('full_cyc','magnetic_field')
        # slice out region containing spin echo to get clear frequency domain plots
        #s_analytic = s_analytic['t':(110e-6,None)]
        for x in xrange(ndshape(s_analytic)['magnetic_field']):
            s_analytic.getaxis('magnetic_field')[x] = field_axis[x*cycle_time]
            print field_axis[x*cycle_time]
            s_analytic.set_units('magnetic_field','G')
        #{{{ this is specifically because field sweep stopped before program finished for '180718_SE_sweep'
        #s_analytic = s_analytic['magnetic_field':(field_axis[0],field_axis[24*cycle_time])]
        #}}}
        print ndshape(s_analytic)
        s_analytic.ift(['ph1','ph2'])
        #{{{ here I am making a copy of this dataset to plot with frequency axis converted to Gauss
        s_analytic_f = s_analytic.C.ft('t')
        s_analytic_f.setaxis('t', lambda x: x/(gammabar_H)*1e4).set_units('t','G')
        s_analytic_f.rename('t',r'$\frac{\Omega}{2 \pi \gamma_{H}}$')
        s_analytic_f.rename('magnetic_field',r'$B_{0}$')
        #}}}
        fl.next('signal(B) as function of '+r'$B_{0}$ (50 G sweep)')
        fl.image(s_analytic_f['ph1',1]['ph2',0])
        # begin phasing
        signal = s_analytic['ph1',1]['ph2',0].C
        signal.rename('magnetic_field','B0')
        #figure('mesh 1')
        #signal.meshplot(cmap=cm.viridis)
        signal.setaxis('t', lambda t: t - 107.5e-6)
        signal = signal['t':(-12e-6,None)]
        #figure('mesh 2')
        #signal.meshplot(cmap=cm.viridis)
        #figure('abs mesh 2')
        #abs(signal).meshplot(cmap=cm.viridis)
        span = 20
        signal_shift = r_[-6e-6:6e-6:500j]
        rmsd = empty_like(signal_shift)
        for x in xrange(ndshape(signal)['B0']):
            for j,dt in enumerate(signal_shift):
                x = 20
                fl.next('cfsdfsd')
                fl.plot(signal['B0',x])
                fl.show();quit()
                shifted_signal = signal.C
                shifted_signal.ft('t')
                ph1 = -1j*2*pi*dt
                shifted_signal *= exp(ph1*shifted_signal.fromaxis('t'))
                shifted_signal.ift('t')
                temp = shifted_signal['B0',x].C
                index_max = abs(temp).argmax('t', raw_index = True).data
                print index_max
                temp = temp['t',index_max-span:index_max+span+1]
                ph0 = temp.C.sum('t').data
                print ph0
                ph0 /= abs(ph0)
                print ph0
                shifted_signal /= ph0
                deviation = conj(shifted_signal.data[::-1]) - shifted_signal.data
                rmsd[j] = sum(abs(deviation)**2)        
            rmsd_nd = nddata(rmsd,'dt').labels('dt',signal_shift).set_units('dt','s')
            rmsd_nd.name('RMSD %d'%x)
            coeff, fit = rmsd_nd.polyfit('dt',order = 5)
            fl.next('RMSD dt')
            plot(rmsd_nd)
            interp_fit = fit.interp('dt', 5000)
            plot(interp_fit,':')
            dt = interp_fit.argmin('dt')
            fl.show();quit()
        print dt
        for x in xrange(ndshape(signal)['magnetic_field']):
            field_val = signal.getaxis('magnetic_field')[x]
            this_s = signal['magnetic_field',x]
            fl.next('plot, signal coherence pathway, time domain')
            fl.plot(this_s,alpha=0.3,label='%0.4f G'%field_val)
        signal.ft('t')
        for x in xrange(ndshape(signal)['magnetic_field']):
            field_val = signal.getaxis('magnetic_field')[x]
            this_s = signal['magnetic_field',x]
            fl.next('plot, signal coherence pathway, freq domain')
            fl.plot(this_s,alpha=0.3,label='%0.4f G'%field_val)
        fl.show();quit()
            #}}}
fl.show()
quit()
