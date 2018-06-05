from pyspecdata import *
import pprint
#import winsound
#import logging
#init_logging(level=logging.DEBUG)
fl = figlist_var()

def process_series(date,id_string,V_AFG,pulse_threshold,noise_threshold):
    """Process a series of pulse data.
    
    Lumping this as a function so we can do things like divide series, etc.

    Parameters
    ----------
    date: str
        date used in the filename
    id_string: str
        filename is called date_id_string
    V_AFG: array
        list of voltage settings used on the AFG 
    pulse_threshold: float 
        determines cut-off limit for calculating pulse power;
        this number is multiplied by the maximum V_{RMS} in the pulse width.
    noise_threshold: float
        determines cut-off limit for calculating noise power;
        this number is multiplied by the minimum V_{RMS} in the capture, outside of pulse width.

    Returns
    -------
    V_rms: nddata
        Generated from the analytic signal for each capture,
        has noise outside of pulse width subtracted out.
    """
    p_len = len(V_AFG)
    V_calib = 0.694*V_AFG
    fl.next('Channel 1, 1')
    for j in range(1,p_len+1):
        print "loading signal",j
        j_str = str(j)
        d = nddata_hdf5(date+'_'+id_string+'.h5/capture'+j_str+'_'+date,
                directory=getDATADIR(exp_type='test_equip'))
        d.set_units('t','s')
        if j == 1:
            raw_signal = (ndshape(d) + ('power',p_len)).alloc()
            raw_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
            raw_signal.setaxis('power',((V_calib/2.0/sqrt(2))**2/50.))
        raw_signal['power',j-1] = d
        if j == 1:
            fl.next('Channel 1, 1')
            fl.plot(d['ch',0], alpha=0.5, label="label %s"%id_string)
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
        analytic_signal['power',j-1] = abs(d)
    fl.next('analytic')
    fl.plot(analytic_signal['ch',0]['power',-1])
    print "Done loading signal for %s \n\n"%id_string 
    pulse0_slice = abs(analytic_signal['ch',0]['power',-1]).contiguous(lambda x: x>pulse_threshold*x.data.max())
    pulse0_slice = pulse0_slice[0,:]
    pulse0_slice += r_[0.6e-6,-0.6e-6]
    pulse0_limits = tuple(pulse0_slice)
    p0_lim1,p0_lim2 = pulse0_limits
    print p0_lim1,p0_lim2
    noise0_slice = abs(analytic_signal['ch',0]['power',-1]).contiguous(lambda x: x>noise_threshold*x.data.min())
    noise0_slice = noise0_slice[0,:]
    noise0_limits = tuple(noise0_slice)
    print noise0_slice
    n0_lim1,n0_lim2 = noise0_limits
    print n0_lim1
    print n0_lim2
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
    print 'Noise limits in microsec: %f, %f'%(n0_lim1/1e-6,n0_lim2/1e-6)
    print 'Pulse limits in microsec: %f, %f'%(p0_lim1/1e-6,p0_lim2/1e-6)
    return V_rms0


# must comment out on of the following before starting
    # {{{ user input
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
    # {{{   no user input (must update)
#V_start = 0.01
#V_stop = 1.45 
#V_step = 50
#V_start_log = log10(V_start)
#V_stop_log = log10(V_stop)
#V_step_log = V_step
#V_AFG = logspace(V_start_log,V_stop_log,V_step)
#print "V_AFG(log10(%f),log10(%f),%f)"%(V_start,V_stop,V_step)
#print "V_AFG(%f,%f,%f)"%(log10(V_start),log10(V_stop),V_step)
##Ignore attenuation here, does not correspond to the corrections we apply later
#atten_p = 1
#atten_V = 1
    # }}}

    # {{{ call files
for date,id_string in [
        ('180514','sweep_high_control'),
        ('180514','sweep_high_duplexer_2piTL')
#        ('180514','sweep_control'),
#        ('180514','sweep_duplexer_2piTL'),
#        ('180531','sweep_pomona_dpx_testing'),
#        ('180531','sweep_pomona_dpx_testing2'),
#        ('180531','sweep_pomona_dpx_testing3'),
#        ('180601','sweep_pomona_dpx_testing'),
#        ('180601','sweep_pomona_dpx_testing2'),
#        ('180601','sweep_pomona_dpx_testing3'),
#        ('180601','sweep_pomona_dpx_testing4'),
#        ('180601','sweep_pomona_dpx'),
#        ('180514','sweep_control'),
#        ('180514','sweep_duplexer_2piTL'),
#        ('180514','sweep_duplexer_2piTL_2'),
#        ('180503','sweep_high_control'),
#        ('180513','sweep_high_control'),
#        ('180503','sweep_high_duplexer_2pi'),
#        ('180513','sweep_high_duplexer_2piTL'),
#        ('180502','sweep_control'),
#        ('180503','sweep_duplexer_2pi'),
#        ('180513','sweep_duplexer_2piTLnoD'),
#        ('180513','sweep_duplexer_2piTL'),
#       ('180510','sweep_low_control'),
#       ('180503','sweep_low_duplexer_2pi'),
#       ('180513','sweep_low_duplexer_2piTLnoD'),
#       ('180513','sweep_low_duplexer_2piTL'),
        ]:
    # }}}

    # {{{ plot labels
    if date == '180514' and id_string == 'sweep_control':
        label='control'
    elif date == '180514' and id_string == 'sweep_duplexer_2piTL':
        label = 'previous duplexer'
    elif date == '180514' and id_string == 'sweep_duplexer_2piTL_2':
        label = 'previous duplexer 2'
    elif date == '180531' and id_string == 'sweep_pomona_dpx':
        label = 'pomona duplexer'
    elif date == '180531' and id_string == 'sweep_pomona_dpx_testing':
        label = 'Trial 2'
    elif date == '180531' and id_string == 'sweep_pomona_dpx_testing2':
        label = 'Trial 3'
    elif date == '180531' and id_string == 'sweep_pomona_dpx_testing3':
        label = 'Trial 4'
    elif date == '180601' and id_string == 'sweep_pomona_dpx_testing':
        label = 'Trial 5'
    elif date == '180601' and id_string == 'sweep_pomona_dpx_testing2':
        label = 'Trial 6'
    elif date == '180601' and id_string == 'sweep_pomona_dpx_testing3':
        label = 'Trial 7'
    elif date == '180601' and id_string == 'sweep_pomona_dpx_testing4':
        label = 'Trial 8'
    elif date == '180601' and id_string == 'sweep_pomona_dpx':
        label = 'current pomona duplexer'
    else:
        label = id_string
    # }}}

    V_rms = process_series(date,id_string,V_AFG/atten_V,pulse_threshold=0.1,noise_threshold=2)
    fl.next('Output vs Input: High power, loglog')
   # V_rms.rename('power','$P_{in}$').set_units('$P_{in}$','W')
   # V_rms.name('$P_{out}$').set_units('W')
    fl.plot(V_rms**2/50./atten_p,'-o',alpha=0.65,plottype='loglog',label="%s"%label) 
    # {{{ voltage plots, if needed
#    fl.next('log($P_{out}$) vs. log($V^{RMS}_{in}$)')
#    val = V_rms/atten_V
#    val.rename('$P_{in}$','setting').setaxis('setting',V_AFG).set_units('setting','Vrms')
#    fl.plot(val,'.',plottype='loglog',label="%s $V_{RMS}$"%label)
#    fl.next('log($V^{RMS}_{out}$) vs. log($V^{RMS}_{in}$)')
#    fl.plot(val,'.',plottype='loglog',label="%s $V{RMS}$"%label)
    # }}}
#    dB_value =  10*log10(V_rms.mean())
#    print '\n\n\n\n\n calculating dB for',id_string
#    print dB_value 
#    if date+id_string == '180514sweep_control':
#        k=0
#        dbdict = {}
#    dict_db = dict([(date+'_'+id_string,dB_value.data)])
#    dbdict.update(dict_db)
#    k += 1
#print k
#pprint.pprint(dbdict) 
fl.show()


