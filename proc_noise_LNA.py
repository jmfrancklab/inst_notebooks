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
#Declaring now because cannot set frequency units atm
s_data = (ndshape(s)).alloc()
s_data.setaxis('t',s.getaxis('t')).set_units('t','s')
s_avg = (ndshape(s)).alloc()
s_avg.setaxis('t',s.getaxis('t')).set_units('t','s')
s.ft('t',shift=True)
s_data.ft('t',shift=True)
s_avg.ft('t',shift=True)
s_modsq = ((abs(s))**2)     #mod square
s_modsq /= 519.01901761     #divide by gain factor, found from power curve
s_modsq /= acq_time         #divide by acquisition time
s_modsq /= 50.              #divide by resistance, gives units: W*s, or W/Hz
for q in xrange(int(0),int(len(captures))):
    s_data['capture',q] = s_modsq['capture',q]
    if q == 0:
        s_avg = s_data['capture',q]
    s_avg += s_data['capture',q]
s_avg /= len(captures) 
print s_avg
fl.next('Power density($\\nu$)')
fl.plot(s_avg,alpha=0.3)
fl.next('Power densities($\\nu$), width=1.5e4 Hz')
fl.plot(s_avg,alpha=0.23,label='PD')
w=1.5e4 #this still contains large peaks at the +/- 1250 MHz
#w=1.5e5 #this removes the large peaks at 1250 MHz and leaves
####w = 1e6
###w = 1.5e6 #this is very smooth, but may be too drastic 
s_avg = s_avg.convolve('t',w)
fl.plot(s_avg,alpha=0.2,color='green',label='Convolved')
fl.next('Convolved, width=1.5e4 Hz')
fl.plot(s_avg,alpha=0.15)
###print "\n\n printing power density, f'n of f:\n"
###print p_den
###p_J = abs(p_den['t':(626e-6,626e6)]).sum('t')
###p_J /= ((1.381e-23)*(293.15)) #kBT units
###print p_J
fl.show()

