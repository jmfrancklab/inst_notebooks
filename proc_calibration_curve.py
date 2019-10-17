from pyspecdata import *

id_string = '191017_HP_calib_coupler_1'

data = load(getDATADIR(exp_type='test_equip')+id_string+'.npz')

x_axis = data[data.files[0]]
y_axis = data[data.files[1]]

figure()
title('Calibration Curve')
plot(x_axis-35,y_axis,'o-')
xlabel('programmed power (dBm)')
ylabel('output power (dBm)')
show()
