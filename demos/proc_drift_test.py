from pyspecdata import *
data = load('190610_Katie_drift_test_air_34dBm_iris.npz')
f_axis = data[data.files[0]]
rx_axis = data[data.files[1]]
t_axis = data[data.files[2]]
print f_axis
stop_index = where(rx_axis==180)
print shape(t_axis)
print len(t_axis[1])
for x in r_[0:len(f_axis)]:
    plot(t_axis[x,:len(t_axis[1])-1],rx_axis[x,:len(t_axis[1])-1]/10.,'o-',label='%0.7f GHz'%(f_axis[x]*1e-9))
title('Air at 34 dBm')
xlabel('time (sec)')
ylabel('receiver (mV)')
grid();legend();show()

