from pyspecdata import *
fl = figlist_var()
import os
import sys
atten_factor = 7.056e-5
#{{{ Functions for plotting different captures of one data set
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
#}}}
#{{{ Define parameter input method
params_choice = int(sys.argv[1])
if params_choice == 0:
    print "Choosing script-defined parameters..."
    print "(make sure parameters are what you want)\n"
    V_start = 0.01
    V_stop = 0.860
    V_step = 40
    V_start_log = log10(V_start)
    V_stop_log = log10(V_stop)
    V_step_log = log10(V_step)
    V_AFG = logspace(V_start_log,V_stop_log,V_step)
    print "V_AFG(log10(%f),log10(%f),%f)"%(V_start,V_stop,V_step)
    print "V_AFG(%f,%f,%f)"%(log10(V_start),log10(V_stop),V_step)
    atten_p = 1
    atten_V = 1
    print "power, Voltage attenuation factors = %f, %f"%(atten_p,atten_V) 
elif params_choice == 1:
    print "Requesting user input..."
    V_start = raw_input("Input start of sweep in Vpp: ")
    V_start = float(V_start)
    print V_start
    V_stop = raw_input("Input stop of sweep in Vpp: ")
    V_stop = float(V_stop)
    print V_stop
    V_step = raw_input("Input number of steps: ")
    V_step = float(V_step)
    print V_step

    axis_spacing = raw_input("1 for log scale, 0 for linear scale: ")
    if axis_spacing == '1':
        V_start_log = log10(V_start)
        V_stop_log = log10(V_stop)
        V_AFG = logspace(V_start_log,V_stop_log,V_step)
        print "V_AFG(log10(%f),log10(%f),%f)"%(V_start,V_stop,V_step)
        print "V_AFG(%f,%f,%f)"%(log10(V_start),log10(V_stop),V_step)
        print V_AFG
    elif axis_spacing == '0':
        V_AFG = linspace(V_start,V_stop,V_step)

        print "V_AFG(%f,%f,%f)"%(V_start,V_stop,V_step)
        print V_AFG

    atten_choice = raw_input("1 for attenuation, 0 for no attenuation: ")
    if atten_choice == '1':
        atten_p = 10**(-40./10.)
        atten_V = 10**(-40./20.)
    elif atten_choice == '0':
        atten_p = 1
        atten_V = 1
    print "power, Voltage attenuation factors = %f, %f"%(atten_p,atten_V) 
# }}}

def gen_power_data(date, id_string, V_AFG, rms_method=True,
        pulse_threshold=0.5):

    def return_signal_power(data,ch):
        "find the pulse, calculate the noise and signal powers and subtract them"
        pulse0_slice = abs(data['power',-1]).contiguous(lambda x: x>pulse_threshold*x.data.max())
        assert pulse0_slice.shape[0] == 1
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
    p_len = len(V_AFG)

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
            if j == 1:
                analytic_signal = (ndshape(d) + ('power',p_len)).alloc()
                analytic_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
                analytic_signal.setaxis('power',(V_AFG/2/sqrt(2))**2/50.)
            analytic_signal['power',j-1]=d
        analytic_signal.name('accumulated_'+date)
        analytic_signal.labels('ch',r_[1,2])
        analytic_signal.hdf5_write(filename,
                directory=getDATADIR(exp_type='test_equip'))
#    fl.next('first and last')
#    fl.plot(abs(analytic_signal['power',r_[0,-1]]),label=date+id_string)
    fl.next('last')
    fl.plot(abs(analytic_signal['power',-1]),label=date+id_string)
    highest_power = abs(analytic_signal['power',-1])
    for ch in xrange(0,2):
        this_data = highest_power['ch',ch]
        pulse0_slice = this_data.contiguous(lambda x: x>pulse_threshold*x.data.max())
        assert len(pulse0_slice) == 1
        pulse0_slice = tuple(pulse0_slice[0,:])
        fl.plot(this_data['t':pulse0_slice]['t',r_[0,-1]],'o',label='CH%s'%str(ch))
    print "Done loading signal for %s \n\n"%id_string 
    power0 = return_signal_power(analytic_signal['ch',0],ch=1)
    power0 *= atten_factor #attenuated control power
    power1 = return_signal_power(analytic_signal['ch',1],ch=2) #DUT power
    return_power = power1
    return_power.name('$P_{out}$')#.set_units('W')  #***IMPORTANT!***
    return_power.rename('power','$P_{in}$').setaxis('$P_{in}$',power0.data)#.set_units('$P_{in}$','W')
    return return_power

for date,id_string in [
        ('180607','sweep_cascade12'),
        ('180526','sweep_test_LNA1'),
        ('180526','sweep_test_LNA2'),
        ('180526','sweep_test_LNA3'),
        ]:
    LNA_power = gen_power_data(date,id_string,V_AFG)
#    truncate_LNAp = LNA_power['$P_{in}$':((1e2*1e-12),None)]
    fl.next('Power Curves')
    fl.plot(LNA_power,'.',label=date+id_string,plottype='loglog',)
    c,result = LNA_power.polyfit('$P_{in}$',force_y_intercept=0)
    fl.plot(result,plottype='loglog')
    print "\n \n \nprinting results for ",id_string
    print c
fl.show()

