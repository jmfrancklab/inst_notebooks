from pyspecdata import *
fl = figlist_var()
import os
import sys

# {{{ constants measured elsewhere
#gain_factor_amp2 = 533.02207468    #LNA#2 gain factor
#gain_factor_amp3 = 526.65867808    #LNA#3 gain factor
gain_factor_amp1 =  523.09526795    #LNA#1 gain factor
gain_factor_both = 203341.124734     #LNA#1,LNA#2 gain factor
                                #Calculated by using splitter
                                #during test signal collection
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
elif width_choice == 5:
    integration_center = 50.e6 
    integration_width = 5.28e6

def load_noise(date,id_string,captures):
    cap_len = len(captures)
    filename = date+'_'+id_string+'.h5'
    try:
        s = nddata_hdf5(filename+'/accumulated_'+date,
                directory=getDATADIR(exp_type='test_equip'))
        s.set_units('t','s')
    except:
        print "accumulated data was not found, pulling individual captures"
        for j in xrange(1,cap_len+1):
            j_str = str(j)
            d = nddata_hdf5(filename+'/capture'+j_str+'_'+date,
                directory=getDATADIR(exp_type='test_equip'))
            d.set_units('t','s')
            if j == 1:
                channels = ((ndshape(d)) + ('capture',cap_len)).alloc()
                channels.setaxis('t',d.getaxis('t')).set_units('t','s')
                channels.setaxis('ch',d.getaxis('ch'))
            print "loading signal %s into capture %s "%(j_str,j_str)
            channels['capture',j-1]=d        
        s = channels
        s.labels('capture',captures)
        s.name('accumulated_'+date)
        s.hdf5_write(filename,
                directory=getDATADIR(exp_type='test_equip'))
    return s
#4096 points
captures = linspace(0,100,100)
power_dens_CH1_dict = {}
power_dens_CH2_dict = {}
for date,id_string,numchan,gain_factor in [
    ('180523','noise_LNA_noavg',1,gain_factor_amp1),
    ('180523','sine_LNA_noavg',1,gain_factor_amp1),
    ('180528','noise_cascade12',2,gain_factor_both),
    ('180528','sine_cascade12_2',2,gain_factor_both),
    ('180526','AFG_terminator_2',2,gain_factor_both),
    ('180526','AFG_terminator_2',2,gain_factor_amp1),
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
    elif id_string == 'noise_cascade12':
        label = '0 avg/cap, BW=250 MHz, noise, cascade #1,#2'
    elif id_string == 'sine_cascade12':
        label = '0 avg/cap, BW=250 MHz, 14.5 MHz sine, cascade #1,#2'
    elif id_string == 'sine_cascade12_2':
        label = '0 avg/cap, BW=250 MHz, 14.5 MHz sine, cascade #1,#2'
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
    label += ' (G=%0.1e)'%gain_factor
    print "for",id_string,"label is",label
    # {{{ this part calculates the positive frequency noise power spectral density
    s = load_noise(date,id_string,captures)
    acq_time = diff(s.getaxis('t')[r_[0,-1]])[0]
    s.ft('t',shift=True)
    s = abs(s)**2         #mod square
    s.mean('capture', return_error=False)
    s.convolve('t',5e5) # we do this before chopping things up, since it uses
    #                      FFT and assumes that the signal is periodic (at this
    #                      point, the signal at both ends is very close to
    #                      zero, so that's good
    s = abs(s)['t':(0,None)]
    s /= 50.              # divide by resistance, gives units: W*s, or W/Hz
    s /= acq_time         # divide by acquisition time
    s /= gain_factor      # divide by gain factor, found from power curve -->
    #                       now we have input-referred power
    s *= 2                # because the power is split over negative and positive frequencies
    # }}}
    interval = tuple(integration_center+r_[-1,1]*integration_width)
    if 'ch' not in s.dimlabels:
        # {{{ a hack to create a fake ch axis
        t_label = s.getaxis('t')
        t_units = s.get_units('t')
        s.setaxis('t',None)
        s.chunk('t',['t','ch'],[-1,1])
        s.setaxis('t',t_label)
        s.set_units('t',t_units)
        # }}}
    try:
        s_slice = s['t':interval]['ch',0]
    except:
        raise ValueError(strm("problem trying to pull the slice, shape of s is",ndshape(s),"numchan is",numchan))
    fl.next('Input-Referred Power Spectral Density, semilog')
    s.name('$S_{xx}(\\nu)$').set_units('W/Hz')
    s_slice.name('$S_{xx}(\\nu)$').set_units('W/Hz')
    fl.plot(s['t':(0e6,80e6)]['ch',0], alpha=0.8, label="%s"%label, plottype='semilogy')
    fl.plot(s_slice, alpha=0.8, color='black', label="integration slice",
            plottype='semilogy')
    axhline(y=k_B*T/1e-12, alpha=0.9, color='purple') # 1e-12 b/c the axis is given in pW
    if numchan == 2:
        print id_string,"CH1 power",str(interval)," Hz = ",s['t':interval]['ch',0].integrate('t')
        print id_string,"CH2 power (only for test signal)",str(interval)," Hz = ",s['t':interval]['ch',1].integrate('t')*atten_factor
        power_dens_CH2_dict[id_string] = (s['t':interval]['ch',1].integrate('t').data)*atten_factor*gain_factor
    power_dens_CH1_dict[id_string] = s['t':interval]['ch',0].integrate('t').data
    expand_x()
print "error is %0.12f"%(((power_dens_CH1_dict['sine_cascade12_2'] - power_dens_CH1_dict['noise_cascade12'] - power_dens_CH2_dict['sine_cascade12_2'])/power_dens_CH2_dict['sine_cascade12_2'])*100)
print "thermal noise is:",k_B*T*float(interval[-1]-interval[0])
fl.show()

