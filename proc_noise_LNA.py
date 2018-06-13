from pyspecdata import *
fl = figlist_var()
import os
import sys
#4096 points
# {{{ constants measured elsewhere
gain_factor_amp1 = 525.94786172         #LNA 2
gain_factor_amp2 = 531.84920761         #LNA 1
gain_factor_casc12 = 171428.95568926    #cascade (1 then 2)
gain_factor_damp1 = 318.5103874         #duplexer,LNA 1 
gain_factor_damp2 = 325.65682308        #duplexer,LNA 2 
gain_factor_dcasc12 = 114008.55204672   #duplexer,cascade(1,2)
gain_factor_pdcasc12 =45514.53212012    #probe,duplexer,cascade

#gain_factor_amp1 = 521.27172202                         #LNA1 gain factor
#gain_factor_amp2 = 529.98023528                        #LNA2 gain factor
#gain_factor_amp3 = 523.73589899                        #LNA3 gain factor
##gain_factor_casc12_ = 203383.76725939914
##gain_factor_casc12 = 174549.75561175 
#gain_factor_casc12 = 193879.86939256                  #LNA1,LNA2 gain factor
#gain_factor_dpx_ = 0.6141065062411988
#gain_factor_dpx = 0.7156772659294433                  #Duplexer gain factor
##gain_factor_tot = 113984.00001949
#gain_factor_tot = 120618.95681133 
scope_noise = 4.4578468934e-19                         # pulled from the gain=1.0 calculation of the
                                                        # scope noise, below
atten_factor = 7.056e-5
T = 273.15 + 20.
power_signal_AFG = ((50.e-3)/(sqrt(2)*2))**2./50.
test_signal_power = power_signal_AFG * atten_factor
# }}}
    # {{{ Command line arguments for integration interval 
width_choice = int(sys.argv[1])
if width_choice == 1:
    integration_center = 1.45e7
    integration_width = 2.2e6
elif width_choice == 2:
    integration_center = 1.452e7
    integration_width = 2.42e5
elif width_choice == 3:
    integration_center = 14.5e6 
    integration_width = 5.7e6
elif width_choice == 4:
    integration_center = 1.45e7
    integration_width = 6.28e6
elif width_choice == 5:
    integration_center = 1.45e7
    integration_width = 8.11e5
elif width_choice == 20:
    integration_center = 20.e6 
    integration_width = 6.4e6
elif width_choice == 25:
    integration_center = 25.e6 
    integration_width = 6.3e6
elif width_choice == 43:
    integration_center = 43.47655e6 
    integration_width = 15.14685e6
elif width_choice == 55:
    integration_center = 55.e6 
    integration_width = 10.e6
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
#        ('180612','sine_14p5_tpmprobe_pmdpx_casc12',2,gain_factor_pdcasc12),
        ('180612','noise_tpmprobe_pmdpx_casc12_11',2,gain_factor_dcasc12),
#        ('180610','noise_LNA1',2,gain_factor_amp1),
#        ('180610','noise_pmdpx_LNA1',2,gain_factor_damp1),
#        ('180610','noise_LNA2',2,gain_factor_amp2),
#        ('180610','noise_pmdpx_LNA2',2,gain_factor_damp2),
#        ('180610','noise_casc12',2,gain_factor_casc12),
        ('180610','noise_pmdpx_casc12',2,gain_factor_dcasc12),
#        ('180608','sine_20_casc12_auto',2,gain_factor_casc12),
#        ('180608','sine_20_LNA2_auto_2',2,gain_factor_amp2),
#        ('180608','sine_20_LNA2_auto',2,gain_factor_amp2),
#        ('180608','sine_20_LNA1_auto_2',2,gain_factor_amp1),
#        ('180608','sine_20_LNA1_auto',2,gain_factor_amp1),
#        ('180608','sine_14p5_LNA1_auto',2,gain_factor_amp1),
#        ('180608','sine_14p5_LNA2_auto',2,gain_factor_amp2),
##        ('180608','sine_14p5_casc12_auto',2,gain_factor_casc12),
#        ('180608','sine_14p5_pmdpx_auto',2,gain_factor_amp3),
#        ('180608','sine_14p5_pmdpx_casc12_auto',2,gain_factor_dcasc12),
#        ('180608','noise_pmdpx_casc12_auto',2,gain_factor_casc12),
#        ('180608','noise_pmdpx_casc12_auto',2,gain_factor_tot),
#        ('180608','noise_pmdpx_auto',2,gain_factor_),
#        ('180608','sine_25_casc12_auto',2,gain_factor_casc12),
#        ('180608','sine_14p5_casc12_auto_2',2,gain_factor_amp2),
#        ('180608','noise_casc12_auto',2,gain_factor_casc12),
#        ('180608','noise_LNA3_auto',2,gain_factor_amp3),
#        ('180608','sine_25_LNA2_auto',2,gain_factor_amp1),
#        ('180608','sine_14p5_LNA2_auto_3',2,gain_factor_amp2),
##        ('180608','noise_LNA2_auto',2,gain_factor_amp2),
#        ('180608','sine_25_LNA1_auto',2,gain_factor_amp1),
#        ('180608','sine_14p5_LNA1_auto_3',2,gain_factor_amp1),
##        ('180608','noise_LNA1_auto',2,gain_factor_amp1),
#        ('180605','noise_LNA1_2CH',2,gain_factor_amp1),
#        ('180608','noise_LNA1',2,gain_factor_amp1),
#        ('180608','noise_LNA1_200',2,gain_factor_amp1),
#        ('180608','noise_LNA1_2',2,gain_factor_amp1),
#        ('180608','noise_LNA1_CH3trig',2,gain_factor_amp1),
#        ('180608','noise_LNA1_CH1trig',2,gain_factor_amp1),
#        ('180608','noise_LNA2',2,gain_factor_amp2),
#        ('180523','sine_LNA_noavg',1,gain_factor_amp1),
#        ('180606','sine_LNA1_2CH',2,gain_factor_amp1),
#        ('180605','noise_LNA2_2CH',2,gain_factor_amp2),
#        ('180605','noise_LNA3_2CH',2,gain_factor_amp3),
#        ('180527','noise_cascade12_2',2,gain_factor_casc12_), #this did not use splitter
#        ('180528','sine_cascade12_2',2,gain_factor_casc12_),
#        ('180601','noise_pomona_dpx_cascade12_2CH',2,gain_factor_casc12_*gain_factor_dpx_),
#        ('180604','sine_pomona_dpx_cascade12_2CH',2,gain_factor_casc12_*gain_factor_dpx_),
#        ('180526','AFG_terminator_2',2,gain_factor_casc12),
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
    elif id_string == 'noise_LNA1_auto':
        label = 'LNA#1, noise'
    elif id_string == 'noise_LNA2_auto':
        label = 'LNA#2, noise'
    elif id_string == 'noise_LNA3_auto':
        label = 'LNA#3, noise'
    elif id_string == 'noise_casc12_auto':
        label = 'Cascade(LNA#1,LNA#2), noise'
    elif id_string == 'noise_pmdpx_auto':
        label = 'Pomona duplexer, noise'
    elif id_string == 'noise_pmdpx_casc12_auto':
        label = 'Pomona duplexer-cascade(#1,#2), noise'
    elif id_string == 'sine_14p5_pmdpx_casc12_auto':
        label = 'Pomona duplexer-cascade(#1,#2), 14.5 MHz sine'
    elif id_string == 'sine_14p5_casc12_auto':
        label = 'Cascade(LNA#1,LNA#2), 14.5 MHz sine'
    elif id_string == 'sine_14p5_pmdpx_auto':
        label = 'Pomona duplexer, 14.5 MHz sine'
    elif id_string == 'sine_14p5_LNA1_auto':
        label = 'LNA#1, sine 14.5 MHz'
    elif id_string == 'sine_14p5_LNA2_auto':
        label = 'LNA#2, sine 14.5 MHz'
    elif id_string == 'noise_LNA1':
        label = 'LNA #1'
    elif id_string == 'noise_pmdpx_LNA1':
        label = 'LNA #1 + Duplexer'
    elif id_string == 'noise_LNA2':
        label = 'LNA #2'
    elif id_string == 'noise_pmdpx_LNA2':
        label = 'LNA #2 + Duplexer'
    elif id_string == 'noise_casc12':
        label = 'Cascade (#1,#2)'
    elif id_string == 'noise_pmdpx_casc12':
        label = 'Cascade (#1,#2) + Duplexer'
    else:
        label = date+id_string 
    label += ' (g=%0.2f)'%gain_factor
        # }}}
    print "\n*** LOADING:",id_string,"***"
    print "FILE LABEL IS:\t\t",label
    # {{{ calculate positive frequency noise power spectral density
    s = load_noise(date,id_string,captures)
    acq_time = diff(s.getaxis('t')[r_[0,-1]])[0]
    print "ACQUISITION TIME IS:\t",acq_time
    print "DWELL TIME IS:      \t",diff(s.getaxis('t')[r_[0,1]])[0]
    s.ft('t',shift=True)
    s = abs(s)**2         #mod square
    s.mean('capture', return_error=False)
    width = 1e6
    s.convolve('t',width) # we do this before chopping things up, since it uses
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
    startf,stopf = tuple(interval)
    print "INTEGRATION INTERVAL:",startf/1e6,"to",stopf/1e6,"MHz"
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
        s_slice = s['t':interval]['ch',0] #CH1=DUT
    #{{{ for scope noise test
    except:
        raise ValueError(strm("problem trying to pull the slice, shape of s is",ndshape(s),"numchan is",numchan))
    if gain_factor == 1.0:
        print "Noise coming from the scope is",s['t':interval]['ch',0].mean('t', return_error=False).data

        #}}}
    else:
        fl.next('Power Spectral Density, probe (convolution = %0.1e Hz)'%width)
        s.name('$S_{xx}(\\nu)$').set_units('W/Hz')
        s_slice.name('$S_{xx}(\\nu)$').set_units('W/Hz')
        fl.plot(s['t':(0,250e6)]['ch',0], alpha=0.5, label="%s"%label, plottype='semilogy')
        fl.plot(s_slice, alpha=0.3, color='black', label="integration slice",
                plottype='semilogy')
        axhline(y=k_B*T/1e-12, alpha=0.9, color='purple') # 1e-12 b/c the axis is given in pW
        # {{{ calculates power at input of component over specified frequency interval
        if numchan == 2:
            #CH1=DUT, CH2=REF(signal) or NULL(noise)
            print "CH1 POWER IS:",s['t':interval]['ch',0].integrate('t')
            print "CH2 POWER IS:",s['t':interval]['ch',1].integrate('t')*atten_factor*gain_factor
            power_dens_CH2_dict[id_string] = (s['t':interval]['ch',1].integrate('t').data)
        # }}}
        power_dens_CH1_dict[id_string] = s['t':interval]['ch',0].integrate('t').data
        expand_x()
        print "THERMAL NOISE POWER IS:",k_B*T*float(interval[-1]-interval[0])
        NF = (s['t':interval]['ch',0].integrate('t').data)/(k_B*T*float(interval[-1]-interval[0]))
        print "NOISE FIGURE IS:",NF
        print "EFFECTIVE TEMPERATURE IS:",(293.0*(NF-1))
        print "*** EXITING:",id_string,"***"
#print "error is %0.12f"%(((power_dens_CH1_dict['sine_pomona_dpx_cascade12_2CH'] - power_dens_CH1_dict['noise_pomona_dpx_cascade12_2CH'] - power_dens_CH2_dict['sine_pomona_dpx_cascade12_2CH'])/power_dens_CH2_dict['sine_pomona_dpx_cascade12_2CH'])*100)

fl.show()

