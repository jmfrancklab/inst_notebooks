from pyspecdata import *
data = load('190522_drift_test_air_27dBm_3min.npz')
f_axis = data[data.files[0]]
rx_axis = data[data.files[1]]
t_axis = data[data.files[2]]
print f_axis
for x in r_[0:len(f_axis)]:
    plot(t_axis[x,:50],rx_axis[x,:50]/10.,'o-',label='%0.7f GHz'%(f_axis[x]*1e-9))
xlabel('time (sec)')
ylabel('receiver (mV)')
grid();legend();show()

