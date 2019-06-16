from pyspecdata import *
import matplotlib as mpl
from matplotlib.pylab import text
font = {'family' : 'sans-serif',
        'sans-serif' : 'Times New Roman',
        'weight' : 'normal',
        'size'   : 30}
mpl.rc('font', **font)
rcParams['mathtext.fontset'] = 'cm'

filename = '190610_Katie_drift_test_air_34dBm_iris'
data = load(getDATADIR(exp_type='test_equip')+filename+'.npz')
f_axis = data[data.files[0]]
rx_axis = data[data.files[1]]
t_axis = data[data.files[2]]
print f_axis
stop_index = where(rx_axis==180)
print shape(t_axis)
print len(t_axis[1])
figure(figsize=(15,5),
        facecolor=(1,1,1,0))
ax = axes(#frameon=False,
        facecolor=(1,1,1,0.5))
#ax.set_alpha(0.5)

for x in r_[0:len(f_axis)]:
    plot(t_axis[x,:len(t_axis[1])-1],rx_axis[x,:len(t_axis[1])-1]/10.,'o-',label='%0.7f GHz'%(f_axis[x]*1e-9))
fs = filename.split('_')
substance = [j.capitalize()
        for j in fs
        if j.lower() in ['air','oil']
        ]
assert len(substance) == 1
substance = substance[0]
power = [j[:-3]
        for j in fs
        if j[-3:].lower() == 'dbm'
        ]
assert len(power) == 1
power = power[0]
title(substance+' at '+power+' dBm')
xlabel('time (sec)')
ylabel('receiver (mV)')
grid();legend();
lg = legend(**dict(bbox_to_anchor=(1.05,1), loc=2, borderaxespad=0.))
lg.set_alpha(0.5)
savefig(filename+'.png',
        dpi=300,bbox_inches='tight',
        facecolor=(1,1,1,0),
        )
show()
