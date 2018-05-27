from pyspecdata import *
fl = figlist_var()
import os
import sys

# {{{ constants measured elsewhere
#gain_factor =   523.09526795    #LNA#1 gain factor
#gain_factor =  533.02207468    #LNA#2 gain factor
gain_factor =  526.65867808    #LNA#3 gain factor
atten_factor = 7.056e-5
T = 273.15 + 20.
power_signal_AFG = ((50.e-3)/(sqrt(2)*2))**2./50.
test_signal_power = power_signal_AFG * atten_factor
# }}}
width_choice = int(sys.argv[1])
if width_choice == 1:
    integration_center = 1.452e7
    integration_width = 2.42e5
elif width_choice == 2:
    integration_center = 1.45e7
    integration_width = 8.11e5
elif width_choice == 3:
    integration_center = 1.45e7
    integration_width = 3.28e6
elif width_choice == 4:
    integration_center = 1.45e7
    integration_width = 5.28e6


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
power_dens_dict = {}
for date,id_string in [
#    ('180525','AFG_terminator'),
#    ('180526','AFG_terminator_2'),
#    ('180527','noise_LNA1_noavg'),
#    ('180527','noise_LNA2_noavg'),
    ('180527','noise_LNA3_noavg'),
#    ('180523','sine_LNA_noavg'),
#    ('180523','noise_LNA_noavg_bw100'),
#    ('180524','noise_LNA_noavg_bw20'),
    ]:
    if id_string == 'sine_LNA':
        label = '14 avg/cap, BW=250 MHz, 14.5 MHz sine'
    elif id_string == 'sine_LNA_noavg':
        label = '0 avg/cap, BW=250 MHz, 14.5 MHz sine'
    elif id_string == 'sine25_LNA_noavg':
        label = '0 avg/cap, BW=100 MHz, 14.5 MHz sine'
    elif id_string == 'noise_LNA':
        label = '14 avg/cap, BW=250 MHz, noise'
    elif id_string == 'noise_LNA_noavg':
        label = '0 avg/cap, BW=250 MHz, noise'
    elif id_string == 'noise_LNA2_noavg':
        label = '0 avg/cap, BW=250 MHz, noise'
    elif id_string == 'noise_LNA3_noavg':
        label = '0 avg/cap, BW=250 MHz, noise'
    elif id_string == 'noise_LNA_noavg_bw100':
        label = '0 avg/cap, BW=100 MHz, noise'
    elif id_string == 'noise_LNA_noavg_bw20':
        label = '0 avg/cap, BW=20 MHz, noise'
    elif id_string == 'AFG_terminator':
        label = '0 avg/cap, BW=250 MHz, AFG terminator noise'
    elif id_string == 'AFG_terminator_2':
        label = '0 avg/cap, BW=250 MHz, AFG,coax,adapter terminator noise'
    else:
        label = 'undetermined'
    #fl.next('Amplitude spectral density')
    #s.name('$\hat{x}(\\nu)$').set_units('V/Hz')
    #fl.plot(s['capture',1],alpha=0.5,label='%s'%label)
    # {{{ this part calculates the positive frequency noise power spectral density
    s = load_noise(date,id_string,captures)
    acq_time = diff(s.getaxis('t')[r_[0,-1]])[0]
    s.ft('t',shift=True)
    s = abs(s)**2         #mod square
    s.mean('capture', return_error=False)
    s.convolve('t',2e5) # we do this before chopping things up, since it uses
    #                      FFT and assumes that the signal is periodic (at this
    #                      point, the signal at both ends is very close to
    #                      zero, so that's good
    s = abs(s)['t':(0,None)]
    s /= 50.              # divide by resistance, gives units: W*s, or W/Hz
    s /= acq_time         # divide by acquisition time
    s /= gain_factor      # divide by gain factor, found from power curve -->
    #                       now we have input-referred power
#    s /= k_B*T           # divide by thermal noise
    s *= 2                # because the power is split over negative and positive frequencies
    # }}}
    interval = tuple(integration_center+r_[-1,1]*integration_width)
    s_slice = s['t':interval]
    fl.next('Input-Referred Power Spectral Density, semilog')
    s.name('$S_{xx}(\\nu)$').set_units('W/Hz')
    s_slice.name('$S_{xx}(\\nu)$').set_units('W/Hz')
    fl.plot(s['t':(0e6,80e6)], alpha=0.8, label="%s"%label, plottype='semilogy')
    fl.plot(s_slice, alpha=0.8, color='black', label="integration slice",
            plottype='semilogy')
    axhline(y=k_B*T/1e-12, alpha=0.9, color='g', lw=2) # 1e-12 b/c the axis is given in pW
    print id_string," integration ",str(interval)," Hz = ",s['t':interval].integrate('t')
#    power_dens_dict[id_string] = s['t':interval].integrate('t').data
    expand_x()
    ####ylim(0,6e-21)
    #fl.next('PD Convolved zoom, width= %.1e Hz'%w)
    #fl.plot(s['t':(-600e6,600e6)],alpha=0.23)
    ###ylim(0,plot_y_max)
    #p_J = (abs(s['t':(-600e6,600e6)])).integrate('t')
    #print p_J
#print "error is %0.2f"%((power_dens_dict['sine_LNA_noavg'] - power_dens_dict['noise_LNA_noavg'] - test_signal_power)/test_signal_power*100)
fl.show()

