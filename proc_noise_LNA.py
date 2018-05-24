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

def pull_first(date,id_string):
    filename = date+'_'+id_string+'.h5'
    j_str = '1'
    d = nddata_hdf5(filename+'/capture'+j_str+'_'+date,
        directory=getDATADIR(exp_type='test_equip'))
    return d['ch',0]
fl.next('pull first sine dataset to check units')
d = pull_first('180523','sine_LNA_noavg')
fl.plot(d)
d.ft('t', shift=True)
d['t':(-13e6,13e6)] = 0
d['t':(16e6,None)] = 0
d['t':(None,-16e6)] = 0
d.ift('t')
fl.plot(d)
fl.show()
exit()
#4096 points
captures = linspace(0,100,100)
for date,id_string in [
    ('180523','sine_LNA_noavg'),
    ]:

    s = load_noise(date,id_string,captures)
    acq_time = diff(s.getaxis('t')[r_[0,-1]])[0]
    print '\nAcquistion time:',acq_time
    w=1e6 
    plot_y_max = 1
    #Declaring now because cannot set frequency units atm
    s.ft('t',shift=True)
    T = 293
    s_modsq = abs(s)**2     #mod square
    s_modsq /= 519.01901761     #divide by gain factor, found from power curve
    s_modsq /= acq_time         #divide by acquisition time
    s_modsq /= 50.              #divide by resistance, gives units: W*s, or W/Hz
    s_modsq /= k_B*T         #divide by thermal noise
    #s_modsq *= 2 # because the power is split over negative and positive frequencies
    s_avg = s_modsq.C.mean('capture', return_error=False)
    if id_string == 'noise_LNA':
        label = 'bandwidth = 250 MHz'
    elif id_string == 'sine_LNA':
        label = '14.5 MHz sine, bandwidth = 250 MHz'
    else:
        label = 'undetermined'
    signal_slice = s_avg['t':(12e6,17e6)]
    fl.next('power_density($\\nu$)')
    fl.plot(s_avg,alpha=0.3, label="%s"%label)
    fl.plot(signal_slice,alpha=0.3, label="signal: %s"%label)
    fl.next('power_density($\\nu$) semilog')
    fl.plot(s_avg,alpha=0.3, label="%s"%label, plottype='semilogy')
    fl.plot(signal_slice,alpha=0.3, label="signal: %s"%label, plottype='semilogy')
    print "for,",label,"signal is: ",'%0.4e'%(signal_slice.C.integrate('t').data)
    #ylim(0,6e-21)
    #interval = (14.4e6,14.6e6)
    #print "integrate from 14.4 to 14.6 MHz (should match P/(k_B T) of injected reference signal):",s_avg['t':interval].integrate('t')
    #print "Johnson noise over same interval (also P/(k_B T)) should be:",(interval[1]-interval[0])
    ###ylim(0,plot_y_max)
    ###w_str = str(w)
    ###fl.next('power_densities($\\nu$),width= %.1e Hz'%w)
    ###fl.plot(s_avg,alpha=0.23,label='PD')
    ###s_avg = s_avg.convolve('t',w)
    ###fl.plot(s_avg,alpha=0.2,color='green',label='Convolved')
    ####ylim(0,6e-21)
    ###fl.next('PD Convolved, width= %.1e Hz'%w)
    ###fl.plot(s_avg,alpha=0.23)
    ####ylim(0,6e-21)
    #fl.next('PD Convolved zoom, width= %.1e Hz'%w)
    #fl.plot(s_avg['t':(-600e6,600e6)],alpha=0.23)
    ###ylim(0,plot_y_max)
    #p_J = (abs(s_avg['t':(-600e6,600e6)])).integrate('t')
    #print p_J
fl.show()


