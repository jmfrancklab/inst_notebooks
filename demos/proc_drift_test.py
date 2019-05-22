from pyspecdata import *
data = load('190522_drift_test_air_21dBm_3min.npz')
f_axis = data[data.files[0]]
rx_axis = data[data.files[1]]
t_axis = data[data.files[2]]

print f_axis,rx_axis
figure()
contourf(t_axis,f_axis[:,newaxis]*ones_like(t_axis),rx_axis)
xlim(10,150)
show()
