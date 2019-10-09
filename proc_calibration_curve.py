from pyspecdata import *

id_string = '191009_b12_calib_1'

data = load(getDATADIR(exp_type='test_equip')+id_string+'.npz')

x_axis = data[data.files[0]]
y_axis = data[data.files[1]]

figure()
plot(x_axis-35,y_axis,'o-')
xlabel('programmed power')
ylabel('output power')
show()
