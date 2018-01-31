from pyspecdata import *
fl = figlist_var()

date = '180130'
id_string = 'amp6'
#for j in r_[1,30,50]:
V_AFG = linspace(0.5,7,50)
p_len = len(V_AFG)
V_calib = 0.5*V_AFG
p_len = len(V_AFG)
#list_of_captures = [9] # capture 9 should be 1.50-1.51 Vpp
#if len(V50_calib) != len(list_of_captures):
#    print "WARNING -- length of voltage array doesn't match number of captures!!!!!"
#    print "FIX THIS!!"
### from previous version, needed to specify plot dimensions, labels, etc. beforehand
fl.next('Channel 1, 1',
        figsize=(12,6),legend=True)
fl.next('Channel 1, %d'%p_len,
        figsize=(12,6),legend=True)
fl.next('Fourier transform -- low power',
        figsize=(12,6))
fl.next('Fourier transform -- high power',
        figsize=(12,6))
fl.next('Analytic signal mag')# for some strange reason, things get messed up if I don't do this here -- can't figure it out -- return to later
#for j in list_of_captures:
for j in range(1,p_len+1):
    print "loading signal",j
    j_str = str(j)
    d = nddata_hdf5(date+'_'+id_string+'.h5/capture'+j_str+'_'+date,
            directory=getDATADIR(exp_type='test_equip'))
    d.set_units('t','s')
    if j == 1:
        raw_signal = (ndshape(d) + ('power',p_len)).alloc()
        raw_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
        raw_signal.setaxis('power',(V_calib/2/sqrt(2))**2/50.)
    raw_signal['power',j-1] = d
    if j == 1:
        fl.next('Channel 1, 1')
        fl.plot(d['ch',0], alpha=0.5,label='raw data')
    if j == p_len:
        fl.next('Channel 1, %d'%p_len)
        fl.plot(d['ch',0], alpha=0.5,label='raw data')
    d.ft('t',shift=True)
    plotdict = {1:"Fourier transform -- low power",
            p_len:"Fourier transform -- high power"}
    for whichp in [1,p_len]:
        fl.next(plotdict[whichp])
        if j == whichp:
            fl.plot(abs(d)['ch',0],alpha=0.2,label='FT')
    d.ift('t')
    for whichp in [1,p_len]:
        if j == whichp:
            fl.next('Channel 1, %d'%whichp)
            fl.plot(d['ch',0], alpha=0.5, label='FT and IFT')
            fl.plot(d['ch',0], alpha=0.5,label='raw data')
    # calculate the analytic signal
    d.ft('t')
    d = d['t':(0,None)]
    d_harmonic = d.copy()
    d['t':(33e6,None)] = 0
    d_harmonic['t':(0,33e6)] = 0
    d_harmonic['t':(60e6,None)] = 0
    for whichp in [1,p_len]:
        fl.next(plotdict[whichp])
        if j == whichp:
            fl.plot(abs(d)['ch',0],alpha=0.2, label="used for analytic")
            fl.plot(abs(d_harmonic)['ch',0],alpha=0.2, label="used for harmonic")
    d.ift('t')
    d_harmonic.ift('t')
    d *= 2
    d_harmonic *= 2
    for whichp in [1,p_len]:
        if j == whichp:
            fl.next('Channel 1, %d'%whichp)
            fl.plot(abs(d)['ch',0],alpha=0.5, label='analytic abs')
            fl.plot(abs(d_harmonic)['ch',0],alpha=0.5, label='harmonic abs')
            fl.plot(d['ch',0],alpha=0.5, label='analytic real')
    if j == 1:
        analytic_signal = (ndshape(d) + ('power',p_len)).alloc()
        analytic_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
        analytic_signal.setaxis('power',(V_calib/2/sqrt(2))**2/50.)
        harmonic_signal = (ndshape(d_harmonic) + ('power',p_len)).alloc()
        harmonic_signal.setaxis('t',d_harmonic.getaxis('t')).set_units('t','s')
        harmonic_signal.setaxis('power',(V_calib/2/sqrt(2))**2/50.)
    analytic_signal['power',j-1] = d
    harmonic_signal['power',j-1] = d_harmonic
    fl.next('Analytic signal mag')
    fl.plot(abs(analytic_signal['ch',0]),alpha=0.2)
pulse_slice = abs(
        analytic_signal['ch',0]['power',-1]).contiguous(lambda x:
                x>0.4*x.data.max())
print "done loading all signals"
assert pulse_slice.shape[0] == 1, strm("found more than one (or none) region rising about 0.6 max amplitude:",tuple(pulse_slice))
pulse_slice = pulse_slice[0,:]
pulse_slice += r_[0.1e-6,-0.1e-6]
V_anal = abs(analytic_signal['ch',0]['t':tuple(pulse_slice)]).mean('t')
V_harmonic = abs(harmonic_signal['ch',0]['t':tuple(pulse_slice)]).mean('t')
pulse_slice += r_[0.5e-6,-0.5e-6]
V_pp = raw_signal['ch',0]['t':tuple(pulse_slice)].run(max,'t')
V_pp -= raw_signal['ch',0]['t':tuple(pulse_slice)].run(min,'t')
atten = 10**(-40./10)
fl.next('power vs. power')
fl.plot((V_anal/sqrt(2))**2/50./atten, label='$V_{analytic}$') #this is the true power plot, using analytic signal Vrms
fl.plot((V_harmonic/sqrt(2))**2/50./atten, label='$V_{harmonic}$') #this is the true power plot, using analytic signal Vrms
#fl.next('power plot Vpp raw')
fl.plot((V_pp/sqrt(2)/2.0)**2/50./atten,'.', label='$V_{pp}$')
fl.next('power vs. AFG setting')
val = (V_pp/sqrt(2)/2.0)**2/50./atten
val.rename('power','setting').setaxis('setting',V_AFG).set_units('setting','V')
fl.plot(val,'.', label='$V_{pp}$')
fl.show()


