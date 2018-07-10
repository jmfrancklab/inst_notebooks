from pyspecdata import *
fl = figlist_var()
import os
import sys
matplotlib.rcParams['legend.fontsize'] ='xx-small'

matplotlib.rcParams['legend.labelspacing'] = 0.2 
matplotlib.legend 
#4096 points
# {{{ constants measured elsewhere
gain_factor_amp1 = 525.94786172         #LNA 2
gain_factor_amp2 = 531.84920761         #LNA 1
gain_factor_casc12 = 171428.95568926    #cascade (1 then 2)
gain_factor_damp1 = 318.5103874         #duplexer,LNA 1 
gain_factor_damp2 = 325.65682308        #duplexer,LNA 2 
gain_factor_dcasc12 = 114008.55204672   #duplexer,cascade(1,2)
gain_factor_pdcasc12 = 45514.53212012    #probe,duplexer,cascade

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
    # {{{ command line arguments for integration interval 
default = True
try:
    sys.argv[1]
    default = False
except:
    sys.argv[0]
if default:
    integration = False
if not default:
    integration = True
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
    else:
        print "Unrecognized width choice"
        integration_center = 14.5e6 
        integration_width = 2.e6
    # }}}
#{{{ loads noise into accumulated data file for faster processing
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
# }}}
captures = linspace(0,100,100)
power_dens_CH1_dict = {}
power_dens_CH2_dict = {}

# {{{ call files
for date,id_string,numchan,gain_factor in [
        #('180709','control_SE',2,1.0),
        #('180709','control_SE_250MSPS',2,1.0),
        #('180709','control_SE_500MSPS',2,1.0),
        #('180709','control_SE_1GSPS',2,1.0),
        #('180709','control_SE_2p5GSPS',2,1.0),
        #('180709','control_SE_nofilter',2,1.0),
        #('180709','control_SE_250MSPS_nofilter',2,1.0),
        #('180709','control_SE_500MSPS_nofilter',2,1.0),
        #('180709','control_SE_1GSPS_nofilter',2,1.0),
        #('180709','control_SE_2p5GSPS_nofilter',2,1.0),
        ('180709','network_SE_full',2,gain_factor_dcasc12),
        ('180709','network_SE_full_250MSPS',2,gain_factor_dcasc12),
        ('180709','network_SE_full_500MSPS',2,gain_factor_dcasc12),
        ('180709','network_SE_full_1GSPS',2,gain_factor_dcasc12),
        ('180709','network_SE_full_2p5GSPS',2,gain_factor_dcasc12),
        ('180709','network_SE',2,gain_factor_dcasc12),
        ('180709','network_SE_250MSPS',2,gain_factor_dcasc12),
        ('180709','network_SE_500MSPS',2,gain_factor_dcasc12),
        ('180709','network_SE_1GSPS',2,gain_factor_dcasc12),
        ('180709','network_SE_2p5GSPS',2,gain_factor_dcasc12),
        #{{{ older files
#        ('180709','control_pulse_22MHz_2p5GSPS',2,1.0),
       # ('180709','control_pulse_22MHz_250MSPS',2,1.0),
#        ('180625','network_22MHz_100M',2,gain_factor_dcasc12),
#        ('180625','network_22MHz_100M_2',2,gain_factor_dcasc12),
#        ('180709','network_1',2,gain_factor_dcasc12),
#        ('180709','network_2',2,gain_factor_dcasc12),
#        ('180709','network_3',2,gain_factor_dcasc12),
#        ('180709','network_4',2,gain_factor_dcasc12),
        #('180709','network_5',2,gain_factor_dcasc12),
#        ('180709','network_6',2,gain_factor_dcasc12),
#        ('180709','network_7',2,gain_factor_dcasc12),
#        ('180709','network_8',2,gain_factor_dcasc12),
#        ('180709','network_9',2,gain_factor_dcasc12),
#        ('180709','network_9_2',2,gain_factor_dcasc12),
        #('180709','network_9_3',2,gain_factor_dcasc12),
#        ('180709','control_pulse',2,1.0),
#        ('180709','control_pulse_3',2,1.0),
#        ('180709','control_pulse_22MHz',2,1.0),
#        ('180709','control_pulse_22MHz_2',2,1.0),
#        ('180709','control_pulse_22MHz_3',2,1.0),
#        ('180709','control_pulse_22MHz_4',2,1.0),
#        ('180709','control_pulse_22MHz_delay',2,1.0),
#        ('180709','control_pulse_22MHz_100MSPS',2,1.0),
        #('180709','control_pulse_22MHz_100MSPS_2',2,1.0),
#    ('180526','AFG_terminator_2',2,1.0),#   leave gain set to 1 so we can get the 
                                         #   absolute number here (not input-referred)
    ]:
    # }}}
    
    # {{{ plot labels
    plot_params = False # toggle this to use plot params or not
    #{{{ plotting AFG waveform, attn, power splitter, with low pass filter
    if id_string == 'control_SE':
        plot_params = dict(label = 'Waveform, 100 MSPS', color = 'blue', alpha=0.15, plottype='semilogy')
    elif id_string == 'control_SE_250MSPS':
        plot_params = dict(label = 'Waveform, 250 MSPS', color = 'orange', alpha=0.15, plottype='semilogy')
    elif id_string == 'control_SE_500MSPS':
        plot_params = dict(label = 'Waveform, 500 MSPS', color = 'green', alpha=0.15, plottype='semilogy')
    elif id_string == 'control_SE_1GSPS':
        plot_params = dict(label = 'Waveform, 1 GSPS', color = 'red', alpha=0.15, plottype='semilogy')
    elif id_string == 'control_SE_2p5GSPS':
        plot_params = dict(label = 'Waveform, 2.5 GSPS', color = 'purple', alpha=0.15, plottype='semilogy')
        #}}}
    #{{{ plotting AFG waveform, attn, power splitter, no input low pass filter
    elif id_string == 'control_SE_nofilter':
        plot_params = dict(label = 'Waveform, no filter, 100 MSPS', color = 'blue', alpha=0.15, linestyle=':', plottype='semilogy')
    elif id_string == 'control_SE_250MSPS_nofilter':
        plot_params = dict(label = 'Waveform, no filter, 250 MSPS', color = 'orange', alpha=0.15, linestyle=':', plottype='semilogy')
    elif id_string == 'control_SE_500MSPS_nofilter':
        plot_params = dict(label = 'Waveform, no filter, 500 MSPS', color = 'green', alpha=0.15, linestyle=':', plottype='semilogy')
    elif id_string == 'control_SE_1GSPS_nofilter':
        plot_params = dict(label = 'Waveform, no filter, 1 GSPS', color = 'red', alpha=0.15, linestyle=':', plottype='semilogy')
    elif id_string == 'control_SE_2p5GSPS_nofilter':
        plot_params = dict(label = 'Waveform, no filter, 2.5 GSPS', color = 'purple', alpha=0.15, linestyle=':', plottype='semilogy')
        #}}}
    #{{{ plotting network, up to ENI amplifier with 50 ohm input
    elif id_string == 'network_SE':
        plot_params = dict(label = '50$\Omega$ input ENI, 100 MSPS', color = '#1f77b4', alpha=0.255, linestyle=':', plottype='semilogy')
    elif id_string == 'network_SE_250MSPS':
        plot_params = dict(label = '50$\Omega$ input ENI, 250 MSPS', color ='#ff7f0e', alpha=0.25, linestyle=':', plottype='semilogy')
    elif id_string == 'network_SE_500MSPS':
        plot_params = dict(label = '50$\Omega$ input ENI, 500 MSPS', color = '#2ca02c', alpha=0.25, linestyle=':', plottype='semilogy')
    elif id_string == 'network_SE_1GSPS':
        plot_params = dict(label = '50$\Omega$ input ENI, 1 GSPS', color ='#d62728', alpha=0.25, linestyle=':', plottype='semilogy')
    elif id_string == 'network_SE_2p5GSPS':
        plot_params = dict(label = '50$\Omega$ input ENI, 2.5 GSPS', color ='#9467bd', alpha=0.25, linestyle=':', plottype='semilogy')
        #}}}
    #{{{ plotting network, everything but magnet and sample
    elif id_string == 'network_SE_full':
        plot_params = dict(label = 'Network, 100 MSPS', color = '#1f77b4', alpha=0.25, plottype='semilogy')
    elif id_string == 'network_SE_full_250MSPS':
        plot_params = dict(label = 'Network, 250 MSPS', color ='#ff7f0e', alpha=0.25, plottype='semilogy')
    elif id_string == 'network_SE_full_500MSPS':
        plot_params = dict(label = 'Network, 500 MSPS', color = '#2ca02c', alpha=0.25, plottype='semilogy')
    elif id_string == 'network_SE_full_1GSPS':
        plot_params = dict(label = 'Network, 1 GSPS', color ='#d62728', alpha=0.25, plottype='semilogy')
    elif id_string == 'network_SE_full_2p5GSPS':
        plot_params = dict(label = 'Network, 2.5 GSPS', color ='#9467bd', alpha=0.25, plottype='semilogy')
    else:
        label = date+'_'+id_string 
        #}}}
    #label += ' (g=%0.2f)'%gain_factor
   # }}}
    print "\n*** LOADING:",id_string,"***"
    s = load_noise(date,id_string,captures)
    #fl.next('plot')
    #fl.plot(s)
    #fl.show()
    #quit()
    if '250MSPS' in id_string:
        u = s.C['t':(40e-6,None)]       #250 MSPS
    elif '500MSPS' in id_string:
        u = s.C['t':(0,35e-6)]          #500 MSPS
    elif id_string == 'control_SE':
        u = s.C['t':(159.0e-6,None)]   #100 MSPS
    elif id_string == 'control_SE_nofilter':
        u = s.C['t':(159.0e-6,None)]   #100 MSPS
    elif '100MSPS' in plot_params['label']:
        u = s.C['t':(159.0e-6,None)]   #100 MSPS
    else:
        u = s.C
    #fl.next('new plot')
    #fl.plot(u)
    #fl.show()
    #quit()
    acq_time = diff(s.getaxis('t')[r_[0,-1]])[0]
    u_acq_time = diff(u.getaxis('t')[r_[0,-1]])[0]
    print acq_time
    print "\t"
    print u_acq_time
    print "\t"
    print "ACQUISITION TIME IS:\t",acq_time
    print "DWELL TIME IS:      \t",diff(s.getaxis('t')[r_[0,1]])[0]
    #{{{ calculate PSD for s
    s.ft('t',shift=True)
    s = abs(s)['t':(0,None)]**2   #mod square and throw out negative frequencies
    s.mean('capture', return_error=False)
    width = 1e6
#    s.convolve('t',width) # we do this before chopping things up, since it uses
    #                      fft and assumes that the signal is periodic (at this
    #                      point, the signal at both ends is very close to
    #                      zero, so that's good
    s /= 50.              # divide by resistance, gives units: W*s, or W/Hz
    s /= acq_time         # divide by acquisition time
    s *= 2               # because the power is split over negative and positive frequencies
#    if gain_factor != 1: # if we're not talking about the scope noise
#        s -= scope_noise
    s /= gain_factor      # divide by gain factor, found from power curve -->
    #                       now we have input-referred power
    # }}}
    #{{{ calculate PSD for u 
    u.ft('t',shift=True)
    u = abs(u)['t':(0,None)]**2
    u.mean('capture', return_error = False)
    u /= 50.
    u /= u_acq_time
    u *= 2
    u /= gain_factor
    #}}}
    if not integration:
            if not plot_params:
                fl.next('Network Noise Power Spectral Density (Input-referred) (convolution = %0.1e Hz)'%width)
                s.name('$S_{xx}(\\nu)$').set_units('W/Hz')
                fl.plot(s['ch',0],alpha=0.35,label='%s'%label,plottype='semilogy')
                axhline(y=k_B*T/1e-12, alpha=0.9, color='purple') # 1e-12 b/c the axis is given in pW
                fl.next('Power Spectral Density with 22 MHz input filter (Noise)')
                u.name('$S_{xx}(\\nu)$').set_units('W/Hz')
                fl.plot(u['ch',0],alpha=0.35,label='%s'%label,plottype='semilogy')
                axhline(y=k_B*T/1e-12, alpha=0.9, color='purple') # 1e-12 b/c the axis is given in pW
            if plot_params:
                fl.next('Network Noise Power Spectral Density (Input-referred) (convolution = %0.1e Hz)'%width)
                s.name('$S_{xx}(\\nu)$').set_units('W/Hz')
                fl.plot(s['ch',0],**plot_params)
                axhline(y=k_B*T/1e-12, alpha=0.9, color='purple') # 1e-12 b/c the axis is given in pW
                fl.next('Network Noise Power Spectral Density, Input-referred')
                u.name('$S_{xx}(\\nu)$').set_units('W/Hz')
                fl.plot(u['ch',0],**plot_params)
                axhline(y=k_B*T/1e-12, alpha=0.9, color='purple') # 1e-12 b/c the axis is given in pW
            #}}}
    #{{{ processing with integration over frequency bands
    if integration:
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
#        try:
#            s_slice = s['t':interval]['ch',0] #CH1=DUT
#        #{{{ for scope noise test
#        except:
#            raise ValueError(strm("problem trying to pull the slice, shape of s is",ndshape(s),"numchan is",numchan))
#        if gain_factor == 1.0:
#            print "Noise coming from the scope is",s['t':interval]['ch',0].mean('t', return_error=False).data
#
#            #}}}
#        else:
        fl.next('FULL Power Spectral Density (Input-referred) (convolution = %0.1e Hz)'%width)
        s.name('$S_{xx}(\\nu)$').set_units('W/Hz')
#        s_slice.name('$S_{xx}(\\nu)$').set_units('W/Hz')
        fl.plot(s['ch',0], alpha=0.35, label="%s"%label, plottype='semilogy')
        axhline(y=k_B*T/1e-12, alpha=0.9, color='purple') # 1e-12 b/c the axis is given in pW
#        fl.next('Power Spectral Density (Input-referred) (convolution = %0.1e Hz)'%width)
#        fl.plot(s['t':(0,250e6)]['ch',0], alpha=0.35, label="%s"%label, plottype='semilogy')
        #   fl.plot(s_slice, alpha=0.8, color='black', label="integration slice",
        #      plottype='semilogy')
        axhline(y=k_B*T/1e-12, alpha=0.9, color='purple') # 1e-12 b/c the axis is given in pW
        #    # {{{ calculates power at input of component over specified frequency interval
        #    if numchan == 2:
        #        #CH1=DUT, CH2=REF(signal) or NULL(noise)
        #        print "CH1 POWER IS:",s['t':interval]['ch',0].integrate('t')
        #        print "CH2 POWER IS:",s['t':interval]['ch',1].integrate('t')*atten_factor*gain_factor
        #        power_dens_CH2_dict[id_string] = (s['t':interval]['ch',1].integrate('t').data)
        #        # }}}
        #    power_dens_CH1_dict[id_string] = s['t':interval]['ch',0].integrate('t').data
        #    expand_x()
        #    print "THERMAL NOISE POWER IS:",k_B*T*float(interval[-1]-interval[0])
        #    NF = (s['t':interval]['ch',0].integrate('t').data)/(k_B*T*float(interval[-1]-interval[0]))
        #    print "NOISE FIGURE IS:",NF
        #    print "EFFECTIVE TEMPERATURE IS:",(293.0*(NF-1))
        #    print "*** EXITING:",id_string,"***"
        #print "error is %0.12f"%(((power_dens_CH1_dict['sine_pomona_dpx_cascade12_2CH'] - power_dens_CH1_dict['noise_pomona_dpx_cascade12_2CH'] - power_dens_CH2_dict['sine_pomona_dpx_cascade12_2CH'])/power_dens_CH2_dict['sine_pomona_dpx_cascade12_2CH'])*100)
        #}}}
fl.show()

