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
captures = linspace(0,100,100)
for date,id_string in [
#    ('180523','sine_LNA'),
#    ('180521','noise_LNA'),
    ('180523','sine_LNA_noavg'),
    ('180523','noise_LNA_noavg'),
    ('180524','sine_noavg'),
    ('180524','sine25_noavg'),
    ('180524','sine25_LNA_noavg'),
#    ('180523','noise_LNA_noavg_bw100'),
#    ('180524','noise_LNA_noavg_bw20'),
    ]:
    s = load_noise(date,id_string,captures)
    acq_time = diff(s.getaxis('t')[r_[0,-1]])[0]
    print '\nAcquistion time:',acq_time
    s.ft('t',shift=True)
    T = 293.15
    s_modsq = abs(s)**2         #mod square
    s_modsq /= 519.01901761     #divide by gain factor, found from power curve
    s_modsq /= acq_time         #divide by acquisition time
    s_modsq /= 50.              #divide by resistance, gives units: W*s, or W/Hz
   # s_modsq /= k_B*T           #divide by thermal noise
    s_modsq *= 2                # because the power is split over negative and positive frequencies
    s_avg = s_modsq.C.mean('capture', return_error=False)
    if id_string == 'sine_LNA':
        label = '14 avg/cap, 14.5 MHz sine, BW=250 MHz'
    elif id_string == 'sine_LNA_noavg':
        label = '0 avg/cap, 14.5 MHz sine, BW=250 MHz'
    elif id_string == 'sine_noavg':
        label = 'NO LNA, 0 avg/cap, 14.5MHz sine, BW=250 MHz'
    elif id_string == 'sine25_noavg':
        label = 'NO LNA, 0 avg/cap, 25 MHz sine, BW=100 MHz'
    elif id_string == 'sine25_LNA_noavg':
        label = '0 avg/cap, 25 MHz sine, BW=100 MHz'
    elif id_string == 'noise_LNA':
        label = '14 avg/cap, BW=250 MHz'
    elif id_string == 'noise_LNA_noavg':
        label = '0 avg/cap, BW=250 MHz'
    elif id_string == 'noise_LNA_noavg_bw100':
        label = '0 avg/cap, BW=100 MHz'
    else:
        label = 'undetermined'
    signal_slice = s_avg['t':(12e6,17e6)]
    fl.next('power_density($\\nu$): slices')
    fl.plot(s_avg,alpha=0.3,label="%s"%id_string,plottype='semilogy')
    fl.plot(signal_slice,alpha=0.4,color='black',label="SLICE")
    print "for,",id_string,"signal is: ",'%0.4e'%(signal_slice.C.integrate('t').data)
    print 'check above same as ',s_avg['t':(12e6,17e6)].integrate('t')
    interval = (130e6,131e6)
    print "integrate from 130 to 131 MHz (should match P/(k_B T) of injected reference signal):",s_avg['t':interval].integrate('t')
    print "Johnson noise over same interval (also P/(k_B T)) should be:",(interval[1]-interval[0])
    w=1e6
    w_str = str(w)
    fl.next('power_densities($\\nu$): smoothing=%.1eHz'%w)
    fl.plot(s_avg,alpha=0.23,label='%s'%id_string, plottype='semilogy')
    s_avg = s_avg.convolve('t',w)
    smooth_slice = s_avg['t':(9.89317e6,18.9844e6)]
    fl.plot(s_avg,alpha=0.2,color='black',label='smoothing', plottype='semilogy')
    fl.next('power_density($\\nu$), slices and smoothing=%.1e Hz'%w)
    fl.plot(s_avg,alpha=0.23,label='%s'%id_string,plottype='semilogy')
    fl.plot(smooth_slice,alpha=0.4,color='black',label='SLICE',plottype='semilogy')
    print "for smooth,",id_string,"signal is: ",'%0.4e'%(smooth_slice.C.integrate('t').data)

    ####ylim(0,6e-21)
    #fl.next('PD Convolved zoom, width= %.1e Hz'%w)
    #fl.plot(s_avg['t':(-600e6,600e6)],alpha=0.23)
    ###ylim(0,plot_y_max)
    #p_J = (abs(s_avg['t':(-600e6,600e6)])).integrate('t')
    #print p_J
fl.show()

