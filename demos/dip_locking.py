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
        this_return = b.lock_on_dip(ini_range=(9.815e9,9.83e9))
        print "Finished lock on dip, about to zoom"
        dip_f = this_return[2] 
        print dip_f
        for j in range(3):
            _,_,dip_f = b.zoom()
        b.set_freq(dip_f)
        b.set_power(19.0)
        raw_input("Minimzie RX...")
        b.set_power(22.0)
        raw_input("Minimzie RX...")
        b.set_power(25.0)
        raw_input("Minimzie RX...")
        b.set_power(26.0)
        raw_input("Minimzie RX...")
        b.set_power(27.0)
        raw_input("Minimzie RX...")
        b.set_power(28.0)
        raw_input("Minimzie RX...")
        b.set_power(29.0)
        raw_input("Minimzie RX...")
        b.set_power(30.0)
        raw_input("Minimzie RX...")
        b.set_power(31.0)
        raw_input("Minimzie RX...")
        b.set_power(32.0)
        raw_input("Minimzie RX...")
        # Initial test stops here AB 08132019
        #b.set_freq(dip_f)

        #b.set_power(28.0)
        #raw_input("Minimzie RX...")
        #b.set_power(31.0)
        #raw_input("Minimzie RX...")
        #b.set_power(32.0)
        #raw_input("Minimzie RX...")
        #b.set_power(26.0)
        #raw_input("Minimzie RX...")
        #b.set_power(28.0)
        #raw_input("Minimzie RX...")
        #b.set_power(30.0)
        #raw_input("Minimzie RX...")
        #b.set_power(32.0)
        #raw_input("Minimzie RX...")
        #b.set_power(33.0)
        #raw_input("Minimzie RX...")
        #b.set_power(34.0)
        #raw_input("Minimzie RX...")
        
        result = b.tuning_curve_data
        
        #fits = b.fit_data
save_data = True
if save_data:
    filename = '191007_dip_2'
    np.savez(filename+'.npz', **result)
def plot_all(show_log_scale=True):
    figure()
    powerlist = []
    thesecolors = cycle(list('bgrcmyk'))
    powerlist = list(set((float(k.split('dBm')[0 ]) for k in result.keys())))
    powerlist.sort()
    print "powerlist is",powerlist
    for power in powerlist:
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
