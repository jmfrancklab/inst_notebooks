from pylab import *
from Instruments import Bridge12
from Instruments.bridge12 import convert_to_power, convert_to_mv
from serial import Serial
import time

with Bridge12() as b:
    b.lock_on_dip(ini_range=(9.80e9,9.83e9))
    b.zoom(dBm_increment=2)
    b.zoom(dBm_increment=2)
    b.zoom(dBm_increment=2)
    b.zoom(dBm_increment=2)
    b.zoom(dBm_increment=2)





    result = b.tuning_curve_data
    f_axis = result['23dBm_freq']
    dip_index = faxis.argmin()
    
    f_axis = r_[faxis[0],faxis[dip_index-3],faxis[dip_index],faxis[dip_index+3],faxis[-1]]
    b.set_rf(False)

    sleep_time = 2.0
    collect_time = 3*60.0
    time_pts = int(collect_time/sleep_time)
    rx_array = zeros((len(f_axis),time_pts),dtype=int32)
    t_array = zeros((len(f_axis),time_pts),dtype=double)
    for j,thisfreq in enumerate(f_axis):
        print "FREQUENCY POINT...",j,"which is",thisfreq
        k = 0
        start = time.time()
        b.set_rf(True)
        b.set_freq(thisfreq)
        b.set_power(23)
        while time.time() - start < collect_time:
            time.sleep(sleep_time)
            rx_array[j,k] = b.rxpowermv_float()
            t_array[j,k] = time.time() - start
            k += 1
        b.set_rf(False)
        time.sleep(10)
    id_string = '190522_drift_test_air_23dBm_3min'
    savez(id_string,freq=f_axis,rx=rx_array,t=t_array)
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
