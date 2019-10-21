from pyspecdata import *


fl = figlist_var()
for id_string,label_string in [
        ('191021_b12_calib_3','coupled to meter'),
        ('191021_b12_calib_5','coupled to meter'),
        ]:

    data = load(getDATADIR(exp_type='test_equip')+id_string+'.npz')

    x_axis = data[data.files[0]]
    y_axis = data[data.files[1]]

    figure('Calib curve')
    title('Calibration curve')
    plot(x_axis,y_axis,'o-',label=label_string)
legend()
xlabel('programmed power (dBm)')
ylabel('output power (dBm)')
show()
