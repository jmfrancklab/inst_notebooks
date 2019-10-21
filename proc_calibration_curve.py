from pyspecdata import *
from scipy.optimize import leastsq,minimize
fl = figlist_var()
for id_string,label_string,col in [
        ('191017_HP_calib_coupler_2','coupled to meter','red'),
        ('191017_HP_calib_coupler_3_2','coupled to terminator','blue'),
        ('191017_HP_calib_coupler_4','amplified','green')
        ]:

    data = load(getDATADIR(exp_type='test_equip')+id_string+'.npz')

    x_axis = data[data.files[0]]
    y_axis = data[data.files[1]]

    figure('Calib curve')
    title('Calibration curve')
    power_data = nddata(y_axis[2:],['set_power'])
    power_data.setaxis('set_power',x_axis[2:])
    power_data['set_power',:] = y_axis[2:]
    print ndshape(power_data)
    fl.next('calib curve')
    fl.plot(power_data,'.-',label=label_string,c=col)
    c,result = power_data.polyfit('set_power')
    fl.plot(result,':',label='%f'%c[0],c=col)
    #plot(x_axis[1:],y_axis[1:],'o-',)
    
legend()
xlabel('programmed power (dBm)')
ylabel('output power (dBm)')
fl.show()
show()
