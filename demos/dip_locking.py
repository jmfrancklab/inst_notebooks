from pylab import *
from Instruments import Bridge12
from Instruments.bridge12 import convert_to_power, convert_to_mv
from serial import Serial
import time
from itertools import cycle

run_bridge12 = True
if run_bridge12:
    with Bridge12() as b:
        b.set_wg(True)
        b.set_rf(True)
        b.set_amp(True)
        b.set_freq(9.851321*1e9)
        b.set_power(0.0)    
        raw_input("Set scope for 0 dBm")
        b.set_power(10.0)
        
        b.freq_sweep(r_[9.835:9.865:15j]*1e9)
        print "Finished frequency sweep..."
        b.set_power(10.0)
        b.set_freq(9.851321*1e9)
        raw_input("Record RX at 10 dBm")
        b.set_power(13.0)
        raw_input("Record RX at 13 dBm")
        b.set_power(16.0)
        raw_input("Record RX at 16 dBm")
        b.set_power(19.0)
        raw_input("Record RX at 19 dBm")
        b.set_power(20.0)
        raw_input("Record RX at 20 dBm")
        #b.set_freq(9.851366*1e9)
        #raw_input("enter")
        #print "19"
        #b.set_power(19.0)
        #b.set_freq(9.851366*1e9)
        #raw_input("enter")
        #print "20"
        #b.set_power(20.0)
        #b.set_freq(9.851366*1e9)
        #raw_input("Enter to stop")
        #b.freq_sweep(r_[9.83:9.86:50j]*1e9)
        #print "13 dBm"
        #b.set_power(13.0)
        #b.freq_sweep(r_[9.83:9.86:25j]*1e9)
        #print "16 dBm"
        #b.set_power(16.0)
        #b.freq_sweep(r_[9.83:9.86:25j]*1e9)
        #print "19 dBm"
        #b.set_power(19.0)
        #b.freq_sweep(r_[9.83:9.86:25j]*1e9)
        #print "20 dBm"
        #b.set_power(20.0)
        #b.freq_sweep(r_[9.83:9.86:25j]*1e9)
        #b.set_power(13.0)
        #b.freq_sweep(r_[9.84:9.87:25j]*1e9)
        #b.set_power(14.0)
        #b.freq_sweep(r_[9.84:9.87:25j]*1e9)
        b.lock_on_dip(ini_range=(9.84e9,9.855e9))
        b.zoom(dBm_increment=3)
        b.zoom(dBm_increment=3)
        #b.zoom(dBm_increment=3)
        #b.zoom(dBm_increment=3)
        #b.zoom(dBm_increment=3)
        #b.zoom(dBm_increment=3)
        #b.zoom(dBm_increment=2)
        #b.zoom(dBm_increment=2)
        manual_iris_adjust = False
        if not manual_iris_adjust:
            b.zoom(dBm_increment=1) # Ends at 36 dBm
        if manual_iris_adjust:
            zoom_return = b.zoom(dBm_increment=1)
            dip_f = zoom_return[2]
            b.set_freq(dip_f)
            raw_input("Minimzie RX...")
        else:
            b.zoom(dBm_increment=1)
        result = b.tuning_curve_data
        
        #fits = b.fit_data
save_data = False
if save_data:
    filename = '190730_empty_cavity_lock_on_dip_1'
    np.savez(filename+'.npz', **result)
def plot_all():
    figure()
    powerlist = []
    thesecolors = cycle(list('bgrcmyk'))
    powerlist = list(set((float(k.split('dBm')[0 ]) for k in result.keys())))
    powerlist.sort()
    print "powerlist is",powerlist
    for power in powerlist:
        show_log_scale = True
        if show_log_scale:
            fmt = convert_to_power
        else:
            fmt = lambda x: x
        thiscolor = thesecolors.next()
        show_fits = False
        plotstyle = 'o-'
        if show_fits: plotstyle = 'o'
        plot(result['%ddBm_freq'%power],
             fmt(result['%ddBm_rx'%power]),
             plotstyle,
             color=thiscolor,
             label='%s'%power)
        if show_fits:
            if '%ddBm_range'%power in fits.keys():
                print "plotting fit for",power
                f_range = fits['%ddBm_range'%power]
                f_axis = r_[f_range[0]:f_range[1]:100j]
                plot(f_axis,
                        fmt(fits['%ddBm_func'%power](f_axis)),
                        '-',
                        color=thiscolor)
plot_all();legend()
