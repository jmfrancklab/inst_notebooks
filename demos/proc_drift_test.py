from pyspecdata import *
data = load('190521_drift_test_air_15dBm.npz')
f_axis = data[data.files[0]]
rx_axis = data[data.files[1]]
t_axis = data[data.files[2]]

figure()
contourf(t_axis,f_axis[:,newaxis]*ones_like(t_axis),rx_axis)
show()
