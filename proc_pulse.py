from pyspecdata import *
fl = figlist_var()

date = '180122'
id_string = 'amp_test'
#for j in r_[1,30,50]:
V_AFG = linspace(0.4,7,50)
V_calib = 0.5*V_AFG
for j in range(1,51):
    j_str = str(j)
    d = nddata_hdf5(date+'_'+id_string+'.h5/capture'+j_str+'_'+date)
    d.set_units('t','s')
    fl.next('Dual-channel d')
    fl.plot(d, alpha=0.5)
    fl.next('Fourier transform',figsize=(12,6))
    d.ft('t',shift=True)
    fl.plot(d,alpha=0.5)
    fl.next('Zoom In', figsize=(12,6))
    d = d['t':(0,40e6)]
    fl.plot(abs(d),alpha=0.5)
    # calculate the analytic signal
    d.ift('t')
    if j == 1:
        analytic_signal = (ndshape(d) + ('power',50)).alloc()
        analytic_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
        analytic_signal.setaxis('power',(V_calib/2/sqrt(2))**2/50.)
    analytic_signal['power',j-1] = d
fl.next('Analytic signal magnitude',figsize=(12,6))
fl.plot(abs(analytic_signal['ch',0]),alpha=0.2)
pulse_slice = abs(
        analytic_signal['ch',0]['power',-1]).contiguous(lambda x:
                x>0.6*x.data.max())
assert pulse_slice.shape[0] == 1, "found more than one region rising about 0.6 max amplitude"
pulse_slice = pulse_slice[0,:]
pulse_slice += r_[0.1e-6,-0.1e-6]
Vrms = abs(analytic_signal['ch',0]['t':tuple(pulse_slice)]).mean('t')*sqrt(2)
fl.next('power plot')
atten = 10**(-40./10)
fl.plot((Vrms)**2/50./atten)
fl.show()

#    d.ft('t',shift=True)
#    d = d['t':(0,25e6)]
#    collated = ndshape(d)
#with figlist_var(filename='amp.pdf') as fl:
#    collated.reorder('ch')
#    collated.ift('t')
#    fl.next('idk')
#    fl.image(collated)
    
    



        

        




