from pyspecdata import *
fl = figlist_var()
import os
import sys
#4096 points
# {{{ constants measured elsewhere
gain_factor_amp1 = 521.817303                          #LNA1 gain factor
gain_factor_amp2 = 530.83648352                        #LNA2 gain factor
gain_factor_amp3 = 524.42584615                        #LNA3 gain factor
gain_factor_both = 174549.75561175                     #LNA1,LNA2 gain factor
gain_factor_dpx = 0.7156772659294433                       #Duplexer gain factor
gain_factor_tot = gain_factor_both*gain_factor_dpx
scope_noise = 4.4578468934e-19                         # pulled from the gain=1.0 calculation of the
                                                        # scope noise, below
atten_factor = 7.056e-5
T = 273.15 + 20.
power_signal_AFG = ((50.e-3)/(sqrt(2)*2))**2./50.
test_signal_power = power_signal_AFG * atten_factor
# }}}

    # {{{ integration arguments
width_choice = int(sys.argv[1])
if width_choice == 1:
    integration_center = 1.452e7
    integration_width = 2.42e5
elif width_choice == 2:
    integration_center = 1.45e7
    integration_width = 8.11e5
elif width_choice == 3:
    integration_center = 1.45e7
    integration_width = 2.2e6
elif width_choice == 4:
    integration_center = 1.45e7
    integration_width = 5.28e6
elif width_choice == 5:
    integration_center = 3.0e6 
    integration_width = 1.0e6
    # }}}

def load_noise(date,id_string,captures):
    cap_len = len(captures)
    filename = date+'_'+id_string+'.h5'
    try:
        s = nddata_hdf5(filename+'/accumulated_'+date,
                directory=getDATADIR(exp_type='test_equip'))
        s.set_units('t','s')
    except:
        print "accumulated data was not found, pulling individual captures"
        for j in xrange(1,cap_len+1):
            j_str = str(j)
            d = nddata_hdf5(filename+'/capture'+j_str+'_'+date,
                directory=getDATADIR(exp_type='test_equip'))
            d.set_units('t','s')
            if j == 1:
                channels = ((ndshape(d)) + ('capture',cap_len)).alloc()
                channels.setaxis('t',d.getaxis('t')).set_units('t','s')
                channels.setaxis('ch',d.getaxis('ch'))
            print "loading signal %s into capture %s "%(j_str,j_str)
            channels['capture',j-1]=d        
        s = channels
        s.labels('capture',captures)
        s.name('accumulated_'+date)
        s.hdf5_write(filename,
                directory=getDATADIR(exp_type='test_equip'))
    return s

captures = linspace(0,100,100)
power_dens_CH1_dict = {}
power_dens_CH2_dict = {}

    # {{{ call files
for date,id_string,numchan,gain_factor in [
        ('180605','noise_LNA1_2CH',2,gain_factor_amp1),
        ('180605','noise_LNA2_2CH',2,gain_factor_amp2),
        ('180605','noise_LNA3_2CH',2,gain_factor_amp3),
        ('180605','noise_cascade12_2CH',2,gain_factor_both),
        ('180527','noise_LNA1_noavg',1,gain_factor_amp1),
        ('180527','noise_LNA2_noavg',1,gain_factor_amp2),
        ('180527','noise_LNA3_noavg',1,gain_factor_amp3),
#        ('180523','sine_LNA_noavg',1,gain_factor_amp1),
#        ('180527','noise_cascade12_2',2,gain_factor_both),
#        ('180528','sine_cascade12_2',2,gain_factor_both),
#        ('180601','noise_pomona_dpx_cascade12_2CH',2,gain_factor_tot),
#        ('180604','sine_pomona_dpx_cascade12_2CH',2,gain_factor_tot),
#        ('180526','AFG_terminator_2',2,gain_factor_both),
#        ('180526','AFG_terminator_2',2,gain_factor_amp1),
#        ('180526','AFG_terminator_2',2,gain_factor_amp2),
#        ('180526','AFG_terminator_2',2,gain_factor_amp3),
#    ('180526','AFG_terminator_2',2,1.0),#   leave gain set to 1 so we can get the 
                                         #   absolute number here (not input-referred)
    ]:
    # }}}
    # {{{ plot labels
    if id_string == 'sine_LNA_noavg':
        label = '0 avg/cap, bw=250 MHz, 14.5 MHz sine'
    elif id_string == 'noise_LNA1_noavg':
        label = 'LNA#1, 0 avg/cap, bw=250 MHz, noise'
    elif id_string == 'noise_LNA2_noavg':
        label = 'LNA#2, 0 avg/cap, bw=250 MHz, noise'
    elif id_string == 'noise_LNA3_noavg':
        label = 'LNA#3, 0 avg/cap, bw=250 MHz, noise'
    elif id_string == 'noise_LNA1_2CH':
        label = 'LNA#1, 0 avg/cap, bw=250 MHz, noise, 6518'
    elif id_string == 'noise_LNA2_2CH':
        label = 'LNA#2, 0 avg/cap, bw=250 MHz, noise, 6518'
    elif id_string == 'noise_LNA3_2CH':
        label = 'LNA#3, 0 avg/cap, bw=250 MHz, noise, 6518'
    elif id_string == 'noise_cascade12_2CH':
        label = 'Cascade #1,#2, 0 avg/cap, bw=250 MHz, noise, 6518'
    elif id_string == 'noise_cascade12_2':
        label = 'Cascade #1,#2, 0 avg/cap, bw=250 MHz, noise'
    elif id_string == 'noise_cascade21_2CH':
        label = 'Cascade #2,#1, 0 avg/cap, bw=250 MHz, noise'
    elif id_string == 'sine_cascade12_2':
        label = 'Cascade #1,#2, 0 avg/cap, bw=250 MHz, 14.5 MHz sine'
    elif id_string == 'AFG_terminator':
        label = '0 avg/cap, bw=250 MHz, AFG terminator noise'
    elif id_string == 'AFG_terminator_2':
        label = '0 avg/cap, bw=250 MHz, AFG,coax,adapter terminator noise'
    elif id_string == 'noise_dpx_cascade12':
        label = 'Duplexer-cascade #1,#2, 0 avg/cap, bw=250 MHz, noise'
    elif id_string == 'sine_dpx_cascade12':
        label = 'Duplexer-cascade #1,#2, 0 avg/cap, bw=250 MHz, 14.5 MHz sine'
    elif id_string == 'noise_dpx_cascade12_2CH':
        label = 'Duplexer-cascade #1,#2, 0 avg/cap, bw=250 MHz, noise'
    elif id_string == 'sine_dpx_cascade12_2CH':
        label = 'Duplexer-cascade #1,#2, 0 avg/cap, bw=250 MHz, 14.5 MHz sine'
    elif id_string == 'noise_pomona_dpx_cascade12_2CH':
        label = 'Pomona duplexer-cascade #1,#2, 0 avg/cap, bw=250 MHz, noise'
    elif id_string == 'sine_pomona_dpx_cascade12_2CH':
        label = 'Pomona duplexer-cascade #1,#2, 0 avg/cap, bw=250 MHz, 14.5 MHz sine'
    else:
        label = 'undetermined'
    label += ' (g=%0.1e)'%gain_factor
        # }}}
    print "\nLOADING:",id_string
    print "for",id_string,"label is",label
    # {{{ calculate positive frequency noise power spectral density
    s = load_noise(date,id_string,captures)
    acq_time = diff(s.getaxis('t')[r_[0,-1]])[0]
    print "acquisition time for",id_string,"is",acq_time
    print "dwell time for",id_string,"is",diff(s.getaxis('t')[r_[0,1]])[0]
    s.ft('t',shift=True)
    s = abs(s)**2         #mod square
    s.mean('capture', return_error=False)
    s.convolve('t',1e6) # we do this before chopping things up, since it uses
    #                      fft and assumes that the signal is periodic (at this
    #                      point, the signal at both ends is very close to
    #                      zero, so that's good
    s = abs(s)['t':(0,None)]
    s /= 50.              # divide by resistance, gives units: W*s, or W/Hz
    s /= acq_time         # divide by acquisition time
    s *= 2                # because the power is split over negative and positive frequencies
#    if gain_factor != 1: # if we're not talking about the scope noise
#        s -= scope_noise
    s /= gain_factor      # divide by gain factor, found from power curve -->
    #                       now we have input-referred power
    # }}}
    interval = tuple(integration_center+r_[-1,1]*integration_width)
    if 'ch' not in s.dimlabels:
        # {{{ a hack to create a fake ch axis
        t_label = s.getaxis('t')
        t_units = s.get_units('t')
        s.setaxis('t',None)
        s.chunk('t',['t','ch'],[-1,1])
        s.setaxis('t',t_label)
        s.set_units('t',t_units)
        # }}}
    try:
        s_slice = s['t':interval]['ch',0]
    except:
        raise ValueError(strm("problem trying to pull the slice, shape of s is",ndshape(s),"numchan is",numchan))
    if gain_factor == 1.0:
        print "Noise coming from the scope is",s['t':interval]['ch',0].mean('t', return_error=False).data
    else:
        fl.next('Input-referred Power Spectral Density, semilog')
        s.name('$S_{xx}(\\nu)$').set_units('W/Hz')
        s_slice.name('$S_{xx}(\\nu)$').set_units('W/Hz')
        fl.plot(s['t':(0e6,250e6)]['ch',0], alpha=0.5, label="%s"%label, plottype='semilogy')
        fl.plot(s_slice, alpha=0.3, color='black', label="integration slice",
                plottype='semilogy')
        axhline(y=k_B*T/1e-12, alpha=0.9, color='purple') # 1e-12 b/c the axis is given in pW
        # {{{ calculates power at input of component over specified frequency interval
        if numchan == 2:
            print id_string,"CH1 power",str(interval)," Hz = ",s['t':interval]['ch',0].integrate('t')
            print id_string,"CH2 power (only for test signal)",str(interval)," Hz = ",s['t':interval]['ch',1].integrate('t')*atten_factor*gain_factor
            power_dens_CH2_dict[id_string] = (s['t':interval]['ch',1].integrate('t').data)*atten_factor*gain_factor
        # }}}
        power_dens_CH1_dict[id_string] = s['t':interval]['ch',0].integrate('t').data
        expand_x()
        print "CH1 noise power over",str(interval)," Hz : ",s['t':interval]['ch',0].integrate('t').data
        print "thermal noise power over",str(interval)," Hz : ",k_B*T*float(interval[-1]-interval[0])
        print "NOISE FIGURE : ",(s['t':interval]['ch',0].integrate('t').data)/(k_B*T*float(interval[-1]-interval[0]))
        print "END",id_string
#print "error is %0.12f"%(((power_dens_CH1_dict['sine_pomona_dpx_cascade12_2CH'] - power_dens_CH1_dict['noise_pomona_dpx_cascade12_2CH'] - power_dens_CH2_dict['sine_pomona_dpx_cascade12_2CH'])/power_dens_CH2_dict['sine_pomona_dpx_cascade12_2CH'])*100)
fl.show()

