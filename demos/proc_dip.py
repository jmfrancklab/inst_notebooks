from pyspecdata import *
from itertools import cycle

#filename = '190711_MiniCircuits_Narda_test'
filename = '190711_just_Narda_test'
data = load(getDATADIR(exp_type='test_equip')+filename+'.npz')

for x in xrange(int(shape(data.keys())[0])):
    print data.keys()[x],"stored in key index",x

def plot_all():
    figure()
    powerlist = []
    thesecolors = cycle(list('bgrcmyk'))
    powerlist = list(set((float(k.split('dBm')[0 ]) for k in data.keys())))
    powerlist.sort()
    print "powerlist is",powerlist
    for power in powerlist:
        show_log_scale = False
        if show_log_scale:
            fmt = convert_to_power
        else:
            fmt = lambda x: x
        thiscolor = thesecolors.next()
        show_fits = False
        plotstyle = 'o-'
        if show_fits: plotstyle = 'o'
        plot(data['%ddBm_freq'%power],
             fmt(data['%ddBm_rx'%power]),
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


plot_all()
title('Narda test')
xlabel('frequency (Hz)')
ylabel('detected power (dBm)')
legend()
show()
