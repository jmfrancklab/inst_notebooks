from pyspecdata import *

id_string = '191009_b12_calib_2'

data = load(getDATADIR(exp_type='test_equip')+id_string+'.npz')

x_axis = data[data.files[0]]
y_axis = data[data.files[1]]

figure()
title('Bridge12 Source Calibration Curve')
plot(x_axis-35,y_axis,'o-')
xlabel('programmed power - 35 (dBm)')
ylabel('output power (dBm)')
show()