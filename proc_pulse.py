from pyspecdata import *
#import winsound
#import logging
#init_logging(level=logging.DEBUG)
fl = figlist_var()

def process_series(date,id_string,V_AFG, pulse_threshold):
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
    V_calib = 0.9*V_AFG
    fl.next('Channel 1, 1')
    #fl.next('Channel 1, %d'%p_len)
    #fl.next('Fourier transform -- low power')
    #fl.next('Fourier transform -- high power')
    for j in range(1,p_len+1):
        print "loading signal",j
        j_str = str(j)
        d = nddata_hdf5(date+'_'+id_string+'.h5/capture'+j_str+'_'+date,
                directory=getDATADIR(exp_type='test_equip'))
        d.set_units('t','s')
        if j == 1:
            raw_signal = (ndshape(d) + ('power',p_len)).alloc()
            raw_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
            #gain = 10**5
            gain = 1
            raw_signal.setaxis('power',(gain)*((V_calib/2.0/sqrt(2))**2/50.))
        raw_signal['power',j-1] = d
        if j == 1:
            #NOTE: process file will not run without the following graph -- need to figure out why
            fl.next('Channel 1, 1')
            fl.plot(d['ch',0], alpha=0.5, label="label %s"%id_string)
        #if j == p_len:
        #    fl.next('Channel 1, %d'%p_len)
        #    fl.plot(d['ch',0], alpha=0.5, label="label")
        d.ft('t',shift=True)
        plotdict = {1:"Fourier transform -- low power",
                p_len:"Fourier transform -- high power"}
        for whichp in [1,p_len]:
            fl.next(plotdict[whichp])
            if j == whichp:
                fl.plot(abs(d)['ch',0],alpha=0.2,label="FT %s"%id_string)
        d.ift('t')
        #for whichp in [1,p_len]:
        #    if j == whichp:
        #        fl.next('Channel 1, %d'%whichp)
        #        fl.plot(d['ch',0], alpha=0.5, label='FT and IFT')
        #        fl.plot(d['ch',0], alpha=0.5,label='raw data')
        # calculate the analytic signal
        d.ft('t')
        d = d['t':(0,None)]
        d_harmonic = d.copy()
        d['t':(33e6,None)] = 0
        d_harmonic['t':(0,33e6)] = 0
        d_harmonic['t':(60e6,None)] = 0
        #for whichp in [1,p_len]:
        #    fl.next(plotdict[whichp])
        #    if j == whichp:
        #        fl.plot(abs(d)['ch',0],alpha=0.15, label="used for analytic")
        #        fl.plot(abs(d_harmonic)['ch',0],alpha=0.15, label="used for harmonic")
        d.ift('t')
        d_harmonic.ift('t')
        d *= 2
        d_harmonic *= 2
        #for whichp in [1,p_len]:
        #    if j == whichp:
        #        fl.next('Channel 1, %d'%whichp)
        #        fl.plot(abs(d)['ch',0],alpha=0.5, label="analytic abs")
        #        fl.plot(abs(d_harmonic)['ch',0],alpha=0.5, label="harmonic abs")
        #        fl.plot(d['ch',0],alpha=0.5, label="analytic real")
        if j == 1:
            analytic_signal = (ndshape(d) + ('power',p_len)).alloc()
            analytic_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
            analytic_signal.setaxis('power',(V_calib/2/sqrt(2))**2/50.)
            harmonic_signal = (ndshape(d_harmonic) + ('power',p_len)).alloc()
            harmonic_signal.setaxis('t',d_harmonic.getaxis('t')).set_units('t','s')
            harmonic_signal.setaxis('power',(V_calib/2/sqrt(2))**2/50.)
        analytic_signal['power',j-1] = d
        harmonic_signal['power',j-1] = d_harmonic
        #fl.next('analytic signal magnitude')
        #fl.plot(abs(analytic_signal['ch',0]),alpha=0.2,label="label")
    pulse_slice = abs(
            analytic_signal['ch',0]['power',-1]).contiguous(lambda x:
                    x>pulse_threshold*x.data.max())

   # winsound.Beep(1010,890)        
    print "done loading all signals for %s"%id_string
    pulse_slice = pulse_slice[0,:]
    pulse_slice += r_[0.1e-6,-0.1e-6]
    V_anal = abs(analytic_signal['ch',0]['t':tuple(pulse_slice)]).mean('t')
    V_harmonic = abs(harmonic_signal['ch',0]['t':tuple(pulse_slice)]).mean('t')
    pulse_slice += r_[0.5e-6,-0.5e-6]
    V_pp = raw_signal['ch',0]['t':tuple(pulse_slice)].run(max,'t')
    V_pp -= raw_signal['ch',0]['t':tuple(pulse_slice)].run(min,'t')
    return V_anal, V_harmonic, V_pp

V_AFG = linspace(0.07,10,100)
atten = 1 
#atten = 10**(-40./10) 

for date,id_string in [
       ('180501','noamp_control'),
       ('180425','sweep_bandpass_3L'),
       ('180430','duplexer_bp'),
       ('180501','duplexer_2pi'),
       ('180502','duplexer_bp2')
        ]:
    V_anal, V_harmonic, V_pp = process_series(date,id_string,V_AFG, pulse_threshold=0.2)
    fl.next('V_analytic: P vs P')
    fl.plot((V_anal/sqrt(2))**2/50./atten, label="%s $V_{analytic}$"%id_string) 
    fl.next('V_harmonic: P vs P')
    fl.plot((V_harmonic/sqrt(2))**2/50./atten, label="%s $V_{harmonic}$"%id_string) 
    fl.next('$P_{OUT}$ vs $P_{IN}$: No RF Amp')
    fl.plot((V_pp/sqrt(2)/2.0)**2/50./atten,'.', label="%s"%id_string)
    fl.next('Power(W) vs. AFG signal(Vpp)')
    val = (V_pp/sqrt(2)/2.0)**2/50./atten
    val.rename('power','setting').setaxis('setting',V_AFG).set_units('setting','Vpp')
    fl.plot(val,'.', label="%s $V_{pp}$"%id_string)
    fl.next('GDS signal(Vpp) vs AFG signal(Vpp)')
    val = V_pp
    val.rename('power','setting').setaxis('setting',V_AFG).set_units('setting','Vpp')
    fl.plot(val,'.', label="%s $V{pp}$"%id_string)

fl.show()

