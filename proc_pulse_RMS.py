from pyspecdata import *
fl = figlist_var()

def gen_plotdict(capture_list,plot_str):
    plotdict = {}
    for n in xrange(len(capture_list)):
        cap_no = capture_list[n]
        dict_n = dict([(cap_no,'CAPTURE %d %s'%(cap_no,plot_str))])
        plotdict.update(dict_n)
    return plotdict

def plot_captures(capture_list,plot_str,current_j,data,how_many_ch):
    plotdict = gen_plotdict(capture_list,plot_str)
    for whichp in capture_list:
        fl.next(plotdict[whichp])
        if current_j == whichp:
            for ch_no in range(how_many_ch):
                k = ch_no + 1
                fl.plot(data['ch',ch_no],alpha=0.2,label='CH%d'%k)
    return

def gen_power_data(date,id_string,V_AFG,pulse_threshold,noise_threshold):
    p_len = len(V_AFG)
    for j in range(1,p_len+1):
        print "loading signal",j
        j_str = str(j)
        d = nddata_hdf5(date+'_'+id_string+'.h5/capture'+j_str+'_'+date,
                directory=getDATADIR(exp_type='test_equip'))
        d.set_units('t','s')
        if j == 1:
            raw_signal = (ndshape(d) + ('power',p_len)).alloc()
            raw_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
            raw_signal.setaxis('power',(V_AFG/2.0/sqrt(2))**2/50.).set_units('power','W')
        raw_signal['power',j-1]=d
        capture_list = [1,p_len]
        plot_captures(capture_list,'RAW',j,d,2)
        d.ft('t',shift=True)

        plot_captures(capture_list,'RAW FT',j,abs(d),2)
        d = d['t':(0,None)]
        d['t':(0,5e6)] = 0
        d['t':(25e6,None)] = 0
        plot_captures(capture_list,'ANALYTIC FT',j,abs(d),2)
        d.ift('t')
        d *= 2
        plot_captures(capture_list,'ANALYTIC',j,abs(d),2)
        #I only want to do the following for d['ch',0] (control, ch1)3
        #NOT d['ch',1], since I want to define the power axis values for ch2
        #as values I generate for ch1
        if j == 1:
            analytic_signal = (ndshape(d) + ('power',p_len)).alloc()
            analytic_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
            #Do I need to do this? Isn't it arbitrary?
            analytic_signal.setaxis('power',(V_AFG/2/sqrt(2))**2/50.)
        analytic_signal['power',j-1]=d
    print "Done loading signal for %s \n\n"%id_string 
    pulse0_slice = abs(analytic_signal['ch',0]['power',-1]).contiguous(lambda x: x>pulse_threshold*x.data.max())
    pulse0_slice = pulse0_slice[0,:]
    pulse0_slice += r_[0.6e-6,-0.6e-6]
    pulse0_limits = tuple(pulse0_slice)
    p0_lim1,p0_lim2 = pulse0_limits
    noise0_slice = abs(analytic_signal['ch',0]['power',-1]).contiguous(lambda x: x>noise_threshold*x.data.min())
    noise0_slice = noise0_slice[0,:]
    noise0_limits = tuple(noise0_slice)
    n0_lim1,n0_lim2 = noise0_limits
    Vn1_rms0 = (abs(analytic_signal['ch',0]['t':(0,n0_lim1)]))**2
    Vn1_rms0 = Vn1_rms0.mean('t',return_error=False)
    Vn1_rms0 = sqrt(Vn1_rms0)
    Vn2_rms0 = (abs(analytic_signal['ch',0]['t':(n0_lim2,None)]))**2
    Vn2_rms0 = Vn2_rms0.mean('t',return_error=False)
    Vn2_rms0 = sqrt(Vn2_rms0)
    Vn_rms0 = (Vn1_rms0 + Vn2_rms0)/2.
    V_rms0 = (abs(analytic_signal['ch',0]['t':tuple(pulse0_slice)]))**2
    V_rms0 = V_rms0.mean('t',return_error=False)
    V_rms0 = sqrt(V_rms0)
    V_rms0 -= Vn_rms0
    print 'Control noise limits in microsec: %f, %f'%(n0_lim1/1e-6,n0_lim2/1e-6)
    print 'Control pulse limits in microsec: %f, %f'%(p0_lim1/1e-6,p0_lim2/1e-6)
   #Calculate atten_factor using exact attenuation of VY574681722
    VinPP = 500.e-3
    VoutPP = 4.20e-3
    VinRMS = (VinPP)/(2*sqrt(2))
    VoutRMS = (VoutPP)/(2*sqrt(2))
    Pin_ = ((VinRMS)**2)/50.
    Pout_ = ((VoutRMS)**2)/50.
    atten_factor_P = (Pout_)/(Pin_)
    power0 = ((V_rms0)**2./50.)*atten_factor_P
    print power0.data
    s = analytic_signal['ch',1] 
    s.rename('power','power_in').setaxis('power_in',power0.data).set_units('power_in','W')
    pulse1_slice = abs(s['power_in',-1]).contiguous(lambda x: x>pulse_threshold*x.data.max())
    pulse1_slice = pulse1_slice[0,:]
    pulse1_slice += r_[0.6e-6,-0.6e-6]
    pulse1_limits = tuple(pulse1_slice) 
    p1_lim1,p1_lim2 = pulse1_limits
    noise1_slice = abs(s['power_in',-1]).contiguous(lambda x: x>noise_threshold*x.data.min())
    noise1_slice = noise1_slice[0,:]
    noise1_limits = tuple(noise1_slice) 
    n1_lim1,n1_lim2 = noise1_limits
    Vn1_rms1 = (abs(analytic_signal['ch',1]['t':(0,n1_lim1)]))**2
    Vn1_rms1 = Vn1_rms1.mean('t',return_error=False)
    Vn1_rms1 = sqrt(abs(Vn1_rms1))
    Vn2_rms1 = (abs(analytic_signal['ch',1]['t':(n1_lim2,None)]))**2
    Vn2_rms1 = Vn2_rms1.mean('t',return_error=False)
    Vn2_rms1 = sqrt(abs(Vn2_rms1))
    Vn_rms1 = (Vn1_rms1+Vn2_rms1)/2.
    V_rms1 = (abs(analytic_signal['ch',1]['t':tuple(pulse1_slice)]))**2

    V_rms1 = V_rms1.mean('t',return_error=False)
    V_rms1 = sqrt(abs(V_rms1))
    V_rms1 -= Vn_rms1
    print 'Amplifier noise limits in microsec: %f, %f'%(n1_lim1/1e-6,n1_lim2/1e-6)
    print 'Amplifier pulse limits in microsec: %f, %f'%(p1_lim1/1e-6,p1_lim2/1e-6)
    power1 = (V_rms1)**2./50.
    power_amp = power1
    power_amp.name('$P_{out}$').set_units('W')  #***IMPORTANT!***
    power_amp.rename('power','$P_{in}$').setaxis('$P_{in}$',power0.data).set_units('$P_{in}$','W')
    print power1.data
    return power_amp

## NO USER INPUT; LOG SPACING 
V_start = 0.01
V_stop = 0.860
V_step = 40
V_start_log = log10(V_start)
V_stop_log = log10(V_stop)
V_step_log = log10(V_step)
V_AFG = logspace(V_start_log,V_stop_log,V_step)
print "V_AFG(log10(%f),log10(%f),%f)"%(V_start,V_stop,V_step)
print "V_AFG(%f,%f,%f)"%(log10(V_start),log10(V_stop),V_step)
#Ignore attenuation here, does not correspond to the corrections we apply later
atten_p = 1
atten_V = 1
#print "power, Voltage attenuation factors = %f, %f"%(atten_p,atten_V) 
#print "Axis spacing: Log"

for date,id_string in [
#       ('180601','sweep_pomona_dpx_cascade12'),
#        ('180528','sweep_cascade12'),
#        ('180526','sweep_test_LNA1'),
#        ('180526','sweep_test_LNA2'),
        ('180526','sweep_test_LNA3'),
        ]:
    LNA_power = gen_power_data(date,id_string,V_AFG,pulse_threshold=0.1,noise_threshold=10.)
#    truncate_LNAp = LNA_power['$P_{in}$':((1e2*1e-12),None)]
    fl.next('Power Curve: LNA #3, RMS processing')
    fl.plot(LNA_power,'.',plottype='loglog')           
    c,result = LNA_power.polyfit('$P_{in}$',force_y_intercept=0)
    fl.plot(result,plottype='loglog')
    print "\n \n \nprinting results for ",id_string
    print c
fl.show()

## REQUESTS USER INPUT
#V_start = raw_input("Input start of sweep in Vpp: ")
#V_start = float(V_start)
#print V_start
#V_stop = raw_input("Input stop of sweep in Vpp: ")
#V_stop = float(V_stop)
#print V_stop
#V_step = raw_input("Input number of steps: ")
#V_step = float(V_step)
#print V_step
#
#axis_spacing = raw_input("1 for log scale, 0 for linear scale: ")
#if axis_spacing == '1':
#    V_start_log = log10(V_start)
#    V_stop_log = log10(V_stop)
#    V_AFG = logspace(V_start_log,V_stop_log,V_step)
#    print "V_AFG(log10(%f),log10(%f),%f)"%(V_start,V_stop,V_step)
#    print "V_AFG(%f,%f,%f)"%(log10(V_start),log10(V_stop),V_step)
#    print V_AFG
#elif axis_spacing == '0':
#    V_AFG = linspace(V_start,V_stop,V_step)

#    print "V_AFG(%f,%f,%f)"%(V_start,V_stop,V_step)
#    print V_AFG
#
#atten_choice = raw_input("1 for attenuation, 0 for no attenuation: ")
#if atten_choice == '1':
#    atten_p = 10**(-40./10.)
#    atten_V = 10**(-40./20.)
#elif atten_choice == '0':
#    atten_p = 1
#    atten_V = 1
#print "power, Voltage attenuation factors = %f, %f"%(atten_p,atten_V) 



