from pyspecdata import *
#import winsound
#import logging
#init_logging(level=logging.DEBUG)
fl = figlist_var()

def process_series(date,id_string,ch_no,V_AFG,atten,pulse_threshold):
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

    Returns
    -------
    V_anal: nddata
        The analytic signal, filtered to select the fundamental frequency (this is manually set).
    V_harmonic: nddata
        The analytic signal, filtered to set the second harmonic (this is manually set)
    V_pp: nddata
        After using the analytic signal to determine the extent of the pulse, find the min and max.
    """
    p_len = len(V_AFG)
    V_calib = 0.694*V_AFG
    filename = date+'_'+id_string+'.h5'
    for j in xrange(1,p_len+1):
        print "loading signal",j
        j_str = str(j)
        d = nddata_hdf5(filename+'/capture'+j_str+'_'+date,
                directory=getDATADIR(exp_type='test_equip'))
        d.set_units('t','s')
        if j == 1:
            raw_signal = (ndshape(d) + ('power',p_len)).alloc()
            raw_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
            raw_signal.setaxis('power',(V_calib/2.0/sqrt(2))**2/50.)
        raw_signal['power',j-1] = d
        d.ft('t',shift=True)
        d = d['t':(0,None)]
        d['t':(0,5e6)] = 0
        d['t':(25e6,None)] = 0
        d.ift('t')
        d *= 2
        analytic_signal = (ndshape(d) + ('power',p_len)).alloc()
        analytic_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
        analytic_signal.setaxis('power',(V_calib/2.0/sqrt(2))**2/50.)
        analytic_signal['power',j-1]=d
    pulse_slice = abs(
            analytic_signal['ch',ch_no]['power',-1]).contiguous(lambda x:
                    x>pulse_threshold*x.data.max())

    print "done loading all signals for %s"%id_string
    pulse_slice = pulse_slice[0,:]

    pulse_slice += r_[0.5e-6,-0.5e-6]
    V_pp = raw_signal['ch',ch_no]['t':tuple(pulse_slice)].run(max,'t')
    V_pp -= raw_signal['ch',ch_no]['t':tuple(pulse_slice)].run(min,'t')
    power = (V_pp/2/sqrt(2))**2/50
    power /= atten
    return power 

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

for date,id_string,ch_no,atten in [
        ('180613','sweep_power_splitter_ENI',1,1e-4),
        ('180613','sweep_power_splitter_ENI',1,7.056e-5),
#        ('180513','sweep_high_control',0,1e-4),
#        ('180513','sweep_high_control',0,7.056e-5),
        ]:
    if id_string == 'sweep_high_control':
        label = 'Test 20180513, atten=%s'%(str(atten))
    if id_string == 'sweep_power_splitter_ENI':
        label = 'Test 20180613, atten=%s'%(str(atten))
    return_power = process_series(date,id_string,ch_no,V_AFG,atten,pulse_threshold=0.1)
    fl.next('$P_{out}$ vs $P_{in}$: Old processing code')
    return_power.rename('power','$P_{in}$ $(W)$')
    return_power.name('$P_{out}$ $(W)$')
    fl.plot(return_power,'.', label="%s"%label)#,plottype='loglog')

fl.show()

