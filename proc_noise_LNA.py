from pyspecdata import *
fl = figlist_var()
import os

def load_noise(date,id_string,captures):
    cap_len = len(captures)
    filename = date+'_'+id_string+'.h5'
    try:
        s = nddata_hdf5(filename+'/accumulated_'+date,
                directory=getDATADIR(exp_type='test_equip'))
        s.set_units('t','s')
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
for date,id_string in [
    ('180521','noise_LNA'),
    ]:
    s = load_noise(date,id_string,captures)

acq_time = diff(s.getaxis('t')[r_[0,-1]])[0]
print '\nAcquistion time:',acq_time

w=1e6 
plot_y_max = 1
#Declaring now because cannot set frequency units atm
s.ft('t',shift=True)
s_modsq = abs(s)**2     #mod square
s_modsq /= 519.01901761     #divide by gain factor, found from power curve
s_modsq /= acq_time         #divide by acquisition time
s_modsq /= 50.              #divide by resistance, gives units: W*s, or W/Hz
s_modsq /= k_B*300.         #divide by thermal noise
s_modsq *= 2 # because the power is split over negative and positive frequencies
fl.next('without averaging')
fl.plot(s_modsq.C.convolve('t',w))
ylim(0,plot_y_max)
s_avg = s_modsq.C.mean('capture', return_error=False)
fl.next('Power density($\\nu$)')
fl.plot(s_avg,alpha=0.3)
interval = (14.4e6,14.6e6)
print "integrate from 14.4 to 14.6 MHz (should match P/(k_B T) of injected reference signal):",s_avg['t':interval].integrate('t')
print "Johnson noise over same interval (also P/(k_B T)) should be:",(interval[1]-interval[0])
ylim(0,plot_y_max)
w_str = str(w)
fl.next('Power densities($\\nu$), width= %.1e Hz'%w)
fl.plot(s_avg,alpha=0.23,label='PD')
s_avg = s_avg.convolve('t',w)
fl.plot(s_avg,alpha=0.2,color='green',label='Convolved')
ylim(0,plot_y_max)
fl.next('PD Convolved, width= %.1e Hz'%w)
fl.plot(s_avg,alpha=0.23)
ylim(0,plot_y_max)
fl.next('PD Convolved zoom, width= %.1e Hz'%w)
fl.plot(s_avg['t':(-600e6,600e6)],alpha=0.23)
ylim(0,plot_y_max)
p_J = (abs(s_avg['t':(-600e6,600e6)])).integrate('t')
print p_J
fl.show()

