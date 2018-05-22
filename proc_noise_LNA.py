from pyspecdata import *
fl = figlist_var()

def load_noise(date,id_string,captures):
    cap_len = len(captures)
    for j in xrange(1,cap_len+1):
        j_str = str(j)
        d = nddata_hdf5(date+'_'+id_string+'.h5/capture'+j_str+'_'+date,
            directory=getDATADIR(exp_type='test_equip'))
        d.set_units('t','s')
        if j == 1:
            ch1 = ((ndshape(d)) + ('capture',cap_len)).alloc()
            ch1.setaxis('t',d.getaxis('t')).set_units('t','s')
        print "loading signal %s into capture %s "%(j_str,j_str)
        ch1['capture',j-1]=d        
    s = ch1['ch',0]
    return s

#4096 points
captures = linspace(1,100,100)
sample_rate = 5e9 #samples/sec
acq_time = 1./sample_rate
print '\nAcquistion time:',acq_time

for date,id_string in [
    ('180521','noise_LNA'),
    ]:
    s = load_noise(date,id_string,captures)
s.ft('t',shift=True)
s_modsq = ((abs(s))**2)
s_data = (ndshape(s_modsq)).alloc()
s_avg = (ndshape(s_modsq)).alloc()
s_data.setaxis('t',s_modsq.getaxis('t')).set_units('t','s')
s_avg.setaxis('t',s_modsq.getaxis('t')).set_units('t','s')
for q in xrange(int(0),int(len(captures))):
    s_data['capture',q] = s_modsq['capture',q]
    if q == 0:
        s_avg = s_data['capture',q]
    s_avg += s_data['capture',q]
s_avg /= len(captures) 
fl.next('Avg of FT(modsq(s))')
fl.plot(s_avg,alpha=0.3)
ylim(0,2e-22)
p_den = s_avg/acq_time
fl.next('power density')
fl.plot(p_den,alpha=0.3)
ylim(0,8e-13)
fl.next('power densities')
fl.plot(p_den,alpha=0.23,label='nix')
#w=1.4e3 #near minimum before losing plot, looks too noisy
#w=1.5e3 #can still see some noise
#w=1.5e4 #this still contains large peaks at the +/- 1250 MHz
#w = 9e5 #this removes the large peaks at 1250 MHz and leaves
        #approximately the expected bandwidth of the LNA
#w = 1e6
w = 1.5e6 #this is very smooth, but may be too drastic 
p_den = p_den.convolve('t',w)
fl.plot(p_den,alpha=0.2,color='green',label='conv')
ylim(0,1.5e-12)
fl.next('power density conv')
fl.plot(p_den,alpha=0.15)
ylim(0,1.5e-12)
print "\n\n printing power density, f'n of f:\n"
print p_den
p_J = abs(p_den['t':(626e-6,626e6)]).sum('t')
p_J /= ((1.381e-23)*(293.15)) #kBT units
print p_J
fl.show()

