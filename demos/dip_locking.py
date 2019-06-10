from pylab import *
from Instruments import Bridge12
from Instruments.bridge12 import convert_to_power, convert_to_mv
from serial import Serial
import time
from itertools import cycle

run_bridge12 = True
if run_bridge12:
    with Bridge12() as b:
        #b.set_wg(True)
        #b.set_rf(True)
        #b.set_amp(True)
        #b.set_power(10.0)
        #b.freq_sweep(r_[9.80:9.83:20j]*1e9)
        b.lock_on_dip(ini_range=(9.80e9,9.83e9))
        b.zoom(dBm_increment=3)
        b.zoom(dBm_increment=3)
        b.zoom(dBm_increment=3)
        b.zoom(dBm_increment=3)
        b.zoom(dBm_increment=3)
        b.zoom(dBm_increment=2)
        b.zoom(dBm_increment=1)
        b.zoom(dBm_increment=2)
        manual_iris_adjust = False
        if manual_iris_adjust:
            zoom_return = b.zoom(dBm_increment=1)
            dip_f = zoom_return[2]
            b.set_freq(dip_f)
            raw_input("Minimzie RX...")
        else:
            b.zoom(dBm_increment=1)
        result = b.tuning_curve_data
        #fits = b.fit_data
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