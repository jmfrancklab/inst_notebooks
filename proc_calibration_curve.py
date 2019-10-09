from pyspecdata import *

id_string = '191008_HP_calib_2'

data = load(getDATADIR(exp_type='test_equip')+id_string+'.npz')

x_axis = data[data.files[0]]
y_axis = data[data.files[1]]

figure()
title('HP Source Calibration Curve')
plot(x_axis,y_axis,'o-')
xlabel('programmed power (dBm)')
ylabel('output power (dBm)')
show()
