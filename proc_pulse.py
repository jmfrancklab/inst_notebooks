from pyspecdata import *
fl = figlist_var()

date = '180124'
id_string = 'amp'
#for j in r_[1,30,50]:
V_AFG = linspace(0.4,7,50)
V_calib = 0.5*V_AFG
list_of_captures = [9] # capture 9 should be 1.50-1.51 Vpp
if len(V_calib) != len(list_of_captures):
    print "WARNING -- length of voltage array doesn't match number of captures!!!!!"
    print "FIX THIS!!"
fl.next('Channel 1',
        figsize=(12,6),legend=True)
fl.next('Fourier transform',figsize=(12,6))
fl.next('Analytic signal')# for some strange reason, things get messed up if I don't do this here -- can't figure it out -- return to later
for j in list_of_captures:
    j_str = str(j)
    d = nddata_hdf5(date+'_'+id_string+'.h5/capture'+j_str+'_'+date)
    print d
    d.set_units('t','s')
    if j == list_of_captures[0]:
        raw_signal = (ndshape(d) + ('power',len(list_of_captures))).alloc()
        raw_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
        raw_signal.setaxis('power',(V_calib/2/sqrt(2))**2/50.)
    raw_signal['power',list_of_captures.index(j)] = d
    fl.next('Channel 1')
    fl.plot(d['ch',0], alpha=0.5,label='raw data')
    d.ft('t',shift=True)
    print "channel 1",id(gcf())
    fl.next('Fourier transform')
    print "ft",id(gcf())
    fl.plot(abs(d)['ch',0])
    fl.next('Channel 1')
    print "channel 1",id(gcf())
    d.ift('t')
    fl.plot(d['ch',0], alpha=0.5, label='FT and IFT')
    # calculate the analytic signal
    d.ft('t')
    d = d['t':(0,None)]
    d['t':(33e6,None)] = 0
    fl.next("Fourier transform")
    fl.plot(abs(d)['ch',0], label="used for analytic")
    d.ift('t')
    d *= 2
    fl.next('Channel 1')
    fl.plot(abs(d)['ch',0],alpha=0.5, label='analytic abs')
    fl.plot(d['ch',0],alpha=0.5, label='analytic real')
    if j == list_of_captures[0]:
        analytic_signal = (ndshape(d) + ('power',len(list_of_captures))).alloc()
        analytic_signal.setaxis('t',d.getaxis('t')).set_units('t','s')
        analytic_signal.setaxis('power',(V_calib/2/sqrt(2))**2/50.)
    analytic_signal['power',list_of_captures.index(j)] = d
print "channel 1",id(gcf())
fl.next('Analytic signal')
print "analytic",id(gcf())
fl.plot(abs(analytic_signal['ch',0]),alpha=0.2)
pulse_slice = abs(
        analytic_signal['ch',0]['power',-1]).contiguous(lambda x:
                x>0.4*x.data.max())
assert pulse_slice.shape[0] == 1, strm("found more than one (or none) region rising about 0.6 max amplitude:",tuple(pulse_slice))
pulse_slice = pulse_slice[0,:]
pulse_slice += r_[0.1e-6,-0.1e-6]
V_anal = abs(analytic_signal['ch',0]['t':tuple(pulse_slice)]).mean('t')
pulse_slice += r_[0.5e-6,-0.5e-6]
V_pp = raw_signal['ch',0]['t':tuple(pulse_slice)].run(max,'t')
V_pp -= raw_signal['ch',0]['t':tuple(pulse_slice)].run(min,'t')
print "V_pp",V_pp
print "V_anal",V_anal
if len(list_of_captures) > 1:
    fl.next('power plot')
    atten = 10**(-40./10)
    fl.plot((V_anal/sqrt(2))**2/50./atten, label='analytic')
    fl.plot((V_pp/sqrt(2)/2.0)**2/50./atten, label='pp')
fl.show()

#    d.ft('t',shift=True)
#    d = d['t':(0,25e6)]
#    collated = ndshape(d)
#with figlist_var(filename='amp.pdf') as fl:
#    collated.reorder('ch')
#    collated.ift('t')
#    fl.next('idk')
#    fl.image(collated)
    
    



        

        




