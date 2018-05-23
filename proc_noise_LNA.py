from pyspecdata import *
fl = figlist_var()
import os

def load_noise(date,id_string,captures):
    cap_len = len(captures)
    filename = date+'_'+id_string+'.h5'
    try:
        s = nddata_hdf5(filename+'/accumulated_'+date,
                directory=getDATADIR(exp_type='test_equip'))
        print "pulled accumulated data"
    except:
        print "accumulated data was not found, pulling individual captures"
        for j in xrange(1,cap_len+1):
            j_str = str(j)
            d = nddata_hdf5(filename+'/capture'+j_str+'_'+date,
                directory=getDATADIR(exp_type='test_equip'))
            d.set_units('t','s')
            if j == 1:
                ch1 = ((ndshape(d)) + ('capture',cap_len)).alloc()
                ch1.setaxis('t',d.getaxis('t')).set_units('t','s')
            print "loading signal %s into capture %s "%(j_str,j_str)
            ch1['capture',j-1]=d        
        s = ch1['ch',0]
        s.labels('capture',captures)
        s.name('accumulated_'+date)
        s.hdf5_write(filename,
                directory=getDATADIR(exp_type='test_equip'))
    return s

#4096 points
captures = linspace(1,100,100)
sample_rate = 5e9 #samples/sec
acq_time = 1./sample_rate
for date,id_string in [
    ('180521','noise_LNA'),
    ]:
    s = load_noise(date,id_string,captures)
#Declaring/allocating now because cannot set frequency units atm
s_data = (ndshape(s)).alloc()
s_data.setaxis('t',s.getaxis('t')).set_units('t','s')
s.ft('t',shift=True)
s_data.ft('t',shift=True)
s_modsq = ((abs(s))**2)     #mod square
s_modsq /= 519.01901761     #divide by gain factor, found from power curve
s_modsq /= acq_time         #divide by acquisition time
s_modsq /= 50.              #divide by resistance, gives units: W*s, or W/Hz
#for q in xrange(int(0),int(len(captures))):
#    s_data['capture',q] = s_modsq['capture',q]
#    if q == 0:
#        s_avg = s_data['capture',q]
#    s_avg += s_data['capture',q]
#s_avg /= len(captures) 
s_avg = s_modsq.C.mean('capture', return_error=False)
fl.next('Power density($\\nu$)')
fl.plot(s_avg,alpha=0.3)
ylim(0,4e-17)
#w=1.5e4 
#w=1.5e5 
w=1e6 
#w=1.5e6 
#w=1.5e7 
w_str = str(w)
fl.next('Power densities($\\nu$), width= %.1e Hz'%w)
fl.plot(s_avg,alpha=0.23,label='PD')
s_avg = s_avg.convolve('t',w)
fl.plot(s_avg,alpha=0.2,color='green',label='Convolved')
ylim(0,4e-17)
fl.next('PD Convolved, width= %.1e Hz'%w)
fl.plot(s_avg,alpha=0.23)
ylim(0,4e-17)
fl.next('PD Convolved zoom, width= %.1e Hz'%w)
fl.plot(s_avg['t':(-600e6,600e6)],alpha=0.23)
ylim(0,4e-17)
p_J = (abs(s_avg['t':(-600e6,600e6)])).integrate('t')
print p_J
fl.show()

