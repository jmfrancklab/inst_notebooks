from pyspecdata import *
fl = figlist_var()

date = '180125'
id_string = 'amptest'
#for j in r_[1,30,50]:
V_AFG = linspace(0.5,2.2,50)
V_calib = 0.5*V_AFG
#list_of_captures = [9] # capture 9 should be 1.50-1.51 Vpp
#if len(V_calib) != len(list_of_captures):
#    print "WARNING -- length of voltage array doesn't match number of captures!!!!!"
#    print "FIX THIS!!"
### from previous version, needed to specify plot dimensions, labels, etc. beforehand
fl.next('Channel 1, 1',
        figsize=(12,6),legend=True)
fl.next('Channel 1, 50',
        figsize=(12,6),legend=True)
fl.next('Fourier transform',
        figsize=(12,6))
fl.next('Analytic signal mag')# for some strange reason, things get messed up if I don't do this here -- can't figure it out -- return to later
#for j in list_of_captures:
for j in range(1,51):
    print "loading signal",j
    j_str = str(j)
    d = nddata_hdf5(date+'_'+id_string+'.h5/capture'+j_str+'_'+date,
            directory=getDATADIR(exp_type='test_equip'))
    d.set_units('t','s')
    if j == 1:
        raw_signal = (ndshape(d) + ('power',50)).alloc()
        raw_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
        raw_signal.setaxis('power',(V_calib/2/sqrt(2))**2/50.)
    raw_signal['power',j-1] = d
    if j == 1:
        fl.next('Channel 1, 1')
        fl.plot(d['ch',0], alpha=0.5,label='raw data')
    if j == 50:
        fl.next('Channel 1, 50')
        fl.plot(d['ch',0], alpha=0.5,label='raw data')
    d.ft('t',shift=True)
    if j == 1:
        fl.next('Fourier transform')
        fl.plot(abs(d)['ch',0],alpha=0.2,label='1')
    if j == 50:
        fl.next('Fourier transform')
        fl.plot(abs(d)['ch',0],alpha=0.2,label='50')
    d.ift('t')
    if j == 1:
        fl.next('Channel 1, 1')
        fl.plot(d['ch',0], alpha=0.5, label='FT and IFT')
        fl.next('Channel 1, 1')
        fl.plot(d['ch',0], alpha=0.5,label='raw data')
    if j == 50:
        fl.next('Channel 1, 50')
        fl.plot(d['ch',0], alpha=0.5, label='FT and IFT')
        fl.next('Channel 1, 50')
        fl.plot(d['ch',0], alpha=0.5,label='raw data')
    # calculate the analytic signal
    d.ft('t')
    d = d['t':(0,None)]
    d['t':(33e6,None)] = 0
    if j == 1:
        fl.next("Fourier transform")
        fl.plot(abs(d)['ch',0],alpha=0.2, label="used for analytic 1")
    if j == 50:
        fl.next("Fourier transform")
        fl.plot(abs(d)['ch',0],alpha=0.2, label="used for analytic 50")
    d.ift('t')
    d *= 2
    if j == 1:
        fl.next('Channel 1, 1')
        fl.plot(abs(d)['ch',0],alpha=0.5, label='analytic abs')
        fl.plot(d['ch',0],alpha=0.5, label='analytic real')
    if j == 50:
        fl.next('Channel 1, 50')
        fl.plot(abs(d)['ch',0],alpha=0.5, label='analytic abs')
        fl.plot(d['ch',0],alpha=0.5, label='analytic real')
    if j == 1:
        analytic_signal = (ndshape(d) + ('power',50)).alloc()
        analytic_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
        analytic_signal.setaxis('power',(V_calib/2/sqrt(2))**2/50.)
    analytic_signal['power',j-1] = d
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
pulse_slice += r_[0.5e-6,-0.5e-6]
V_pp = raw_signal['ch',0]['t':tuple(pulse_slice)].run(max,'t')
V_pp -= raw_signal['ch',0]['t':tuple(pulse_slice)].run(min,'t')
atten = 10**(-40./10)
fl.next('power plot Vrms analytic')
fl.plot((V_anal/sqrt(2))**2/50./atten) #this is the true power plot, using analytic signal Vrms
#fl.next('power plot Vpp raw')
fl.plot((V_pp/sqrt(2)/2.0)**2/50./atten, label='$V_{pp}$')
fl.show()

#    d.ft('t',shift=True)
#    d = d['t':(0,25e6)]
#    collated = ndshape(d)
#with figlist_var(filename='amp.pdf') as fl:
#    collated.reorder('ch')
#    collated.ift('t')
#    fl.next('idk')
#    fl.image(collated)
    
    



        

        




