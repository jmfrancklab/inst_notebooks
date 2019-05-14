from pylab import *
from Instruments import Bridge12
from Instruments.bridge12 import convert_to_power, convert_to_mv
from serial import Serial
import time
from itertools import cycle

run_bridge12 = True
if run_bridge12:
    with Bridge12() as b:
    #    b.set_wg(True)
    #    b.set_rf(True)
    #    b.set_amp(True)
    #    b.set_power(10.0)
    #    b.freq_sweep(r_[9.848:9.855:100j]*1e9)
        b.lock_on_dip()
        for j in range(5):
            b.zoom(dBm_increment=3)
        
        #for j in range(15):
        #    b.increase_power_zoom2(dBm_increment=1,n_freq_steps=15)
    
        result = b.tuning_curve_data
        fits = b.fit_data
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