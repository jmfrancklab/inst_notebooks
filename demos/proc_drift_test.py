from pyspecdata import *
data = load('190607_Katie_drift_test_air_33dBm_iris.npz')
f_axis = data[data.files[0]]
rx_axis = data[data.files[1]]
t_axis = data[data.files[2]]
print f_axis
for x in r_[0:len(f_axis)]:
    plot(t_axis[x,:50],rx_axis[x,:50]/10.,'o-',label='%0.7f GHz'%(f_axis[x]*1e-9))
title('Air at 33 dBm')
xlabel('time (sec)')
ylabel('receiver (mV)')
grid();legend();show()

