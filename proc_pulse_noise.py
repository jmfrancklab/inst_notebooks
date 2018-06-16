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
#{{{ Loads noise into accumulated data file for faster processing
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
#}}}
# {{{ Signal processing function
def gen_power_data(date, id_string, V_AFG, rms_method, atten=1,
        pulse_threshold=0.5):
    # {{{ documentation
    """Process a series of pulse data to produce output vs input power set
    ready for plotting.
    
    Lumping this as a function so we can do things like divide series, etc.

    Parameters
    ----------
    date: str
        date used in the filename
    id_string: str
        filename is called date_id_string
    V_AFG: array
        list of voltage settings used on the AFG 
    rms_method: boolean
        if True, calls rms_signal_to_power() which returns power of input data set 
        by subtracting V_RMS noise from V_RMS pulse and converting the difference to
        power.
        if False, calls pp_signal_to_power() which returns power of input data set
        by subtracting minimum V from maximum V within the pulse length, and converting
        the difference (V_PP) to power. Original method used for processing such data 
        sets until 06/2018.
    pulse_threshold: float 
        determines cut-off limit for calculating pulse power;
        this number is multiplied by the maximum V_{RMS} in the pulse width.

    Returns
    -------
    return_power : nddata
        output power (y-axis) vs input power (x-axis) for each capture
    """
    #}}}
    #{{{ RMS function: calculates power by subtracting RMS noise from RMS signal, both analytic
    def rms_signal_to_power(data,ch):
        "find the pulse, calculate the noise and signal powers and subtract them"
        pulse0_slice = abs(data['power',-1]).contiguous(lambda x: x>pulse_threshold*x.data.max())
        pulse0_slice = pulse0_slice[0,:]
        pulse_limits = pulse0_slice + r_[0.6e-6,-0.6e-6]
        noise_limits = pulse0_slice - r_[0.6e-6,-0.6e-6]
        p0_lim1,p0_lim2 = pulse_limits
        n0_lim1,n0_lim2 = noise_limits
        Vn1_rms0 = sqrt((abs(data['t':(0,n0_lim1)]
            )**2).mean('t',return_error=False))
        Vn2_rms0 = sqrt((abs(data['t':(0,n0_lim2)]
            )**2).mean('t',return_error=False))
        Vn_rms0 = (Vn1_rms0 + Vn2_rms0)/2.
        V_rms0 = sqrt((abs(data['t':tuple(pulse0_slice)]
            )**2).mean('t',return_error=False))
        V_rms0 -= Vn_rms0
        print 'CH',ch,'Noise limits in microsec: %f, %f'%(n0_lim1/1e-6,n0_lim2/1e-6)
        print 'CH',ch,'Pulse limits in microsec: %f, %f'%(p0_lim1/1e-6,p0_lim2/1e-6)
        return (V_rms0)**2./50.
    #}}}
    #{{{ PP method: calculates power by subtract min from max analytic signal within pulse slice
    def pp_signal_to_power(data,ch):
        pulse_max = abs(data['power',-1].data.max())
        pulse_slice = abs(data['power',-1]).contiguous(lambda x: x>pulse_threshold*x.data.max())
        pulse_slice = pulse_slice[0,:]  
        pulse_slice += r_[0.6e-6,-0.6e-6]
        pulse_limits = tuple(pulse_slice)
        p_lim1,p_lim2 = pulse_limits
        print 'CH',ch,'Pulse limits in microsec: %f, %f'%(p_lim1/1e-6,p_lim2/1e-6)
        #Important point: Should this be modified to make it so that we are calculate V_pp from the
        #   raw data and not the analytic signal, as we had this method originally? 
        V_pp = data['t':tuple(pulse_slice)].run(max,'t')
        V_pp -= data['t':tuple(pulse_slice)].run(min,'t')
        return (V_pp)**2./50. 
    #}}}    
    p_len = len(V_AFG)
    V_calib = 0.694*V_AFG
    filename = date+'_'+id_string+'.h5'
    try:
        analytic_signal = nddata_hdf5(filename+'/accumulated_'+date,
                directory=getDATADIR(exp_type='test_equip'))
        analytic_signal.set_units('t','s')
    except:
        print "accumulated data was not found, pulling individual captures"
        for j in xrange(1,p_len+1):
            print "loading signal",j
            j_str = str(j)
            d = nddata_hdf5(filename+'/capture'+j_str+'_'+date,
                    directory=getDATADIR(exp_type='test_equip'))
            d.set_units('t','s')
            if j == 1:
                raw_signal = (ndshape(d) + ('power',p_len)).alloc()
                raw_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
                raw_signal.setaxis('power',((V_calib/2.0/sqrt(2))**2/50.)).set_units('power','W')
            raw_signal['power',j-1] = d
            d.ft('t',shift=True)
            d = d['t':(0,None)]
            d['t':(0,5e6)] = 0
            d['t':(25e6,None)] = 0
            d.ift('t')
            d *= 2
            if j == 1:
                analytic_signal = (ndshape(d) + ('power',p_len)).alloc()
                analytic_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
                analytic_signal.setaxis('power',(V_calib/2/sqrt(2))**2/50.)
            analytic_signal['power',j-1] = d
        analytic_signal.name('accumulated_'+date)
        analytic_signal.labels('ch',r_[1,2])
        analytic_signal.hdf5_write(filename,
                directory=getDATADIR(exp_type='test_equip'))
        #{{{Optional - plots analytic pulse cut off 
    fl.next('Lowest power, analytic')
    fl.plot(abs(analytic_signal['ch',0]['power',0]),label=id_string)
    fl.plot(abs(analytic_signal['ch',1]['power',0]),label=id_string)
    lowest_power = abs(analytic_signal['power',0])
    for ch in xrange(0,2):
        this_data = lowest_power['ch',ch]
        pulse0_slice = this_data.contiguous(lambda x: x>pulse_threshold*x.data.max())
        pulse0_slice = tuple(pulse0_slice[0,:])
        fl.plot(this_data['t':pulse0_slice]['t',r_[0,-1]],'o',label='CH%s'%str(ch))
    fl.next('Highest power, analytic')
    fl.plot(abs(analytic_signal['ch',0]['power',-1]),label=id_string)
    fl.plot(abs(analytic_signal['ch',1]['power',-1]),label=id_string)
    highest_power = abs(analytic_signal['power',-1])
    for ch in xrange(0,2):
        this_data = highest_power['ch',ch]
        pulse0_slice = this_data.contiguous(lambda x: x>pulse_threshold*x.data.max())
        pulse0_slice = tuple(pulse0_slice[0,:])
        fl.plot(this_data['t':pulse0_slice]['t',r_[0,-1]],'o',label='CH%s'%str(ch))
        #}}}
    print "DATA: %s"%id_string 
    #{{{ NOTE: ASSUMES CH1=REFERENCE AND CH2=DUT
    if rms_method:
        power0 = rms_signal_to_power(analytic_signal['ch',0],ch=1)
#        power0 *= atten    #for LNA testing
                    #needed to multiply reference ch by attenuation
                    #in order to generate proper O/I plot 
        power1 = rms_signal_to_power(analytic_signal['ch',1],ch=2)
        power1 /= atten #for ENI testing
    if not rms_method:
        power0 = abs(pp_signal_to_power(analytic_signal['ch',0],ch=1))
        power0 *= atten #old code
        power1 = abs(pp_signal_to_power(analytic_signal['ch',1],ch=2))
        #}}}
    control = power0
    control.name('$P_{out}  (W)$')#.set_units('W')
    control.rename('power','$P_{in}  (W)$').setaxis('$P_{in}  (W)$',power0.data)#.set_units('$P_{in}$','W')
    return_power = power1
    return_power.name('$P_{out}  (W)$')#.set_units('W')
    return_power.rename('power','$P_{in}  (W)$').setaxis('$P_{in}  (W)$',power0.data)#.set_units('$P_{in}$','W')
    return return_power,control
#}}}

captures = linspace(0,100,100)
power_dens_CH1_dict = {}
power_dens_CH2_dict = {}

for date,id_string,numchan,gain_factor in [
        ('180615','pulse_noise_amp_dibox_tpmprobe_pmdpx_casc12_2',2,gain_factor_dcasc12),
    ]:
    print "\n*** LOADING:",id_string,"***"
    s = load_noise(date,id_string,captures)
    print ndshape(s)
    fl.next("test")
    fl.plot(s['ch',0]['capture',0])
    fl.plot(s['ch',0]['capture',-1])
    s.ft('t',shift=True)
    fl.next("test ft")
    fl.plot(s['ch',0]['capture',0])
    fl.plot(s['ch',0]['capture',-1])
    fl.show()
    quit()
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
        fl.next('Power Spectral Density (convolution = %0.1e Hz)'%width)
        s.name('$S_{xx}(\\nu)$').set_units('W/Hz')
        s_slice.name('$S_{xx}(\\nu)$').set_units('W/Hz')
        fl.plot(s['t':(0,250e6)]['ch',0], alpha=0.5, label="%s"%id_string, plottype='semilogy')
#        fl.plot(s_slice, alpha=0.8, color='black', label="integration slice",
#                plottype='semilogy')
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

fl.show()

