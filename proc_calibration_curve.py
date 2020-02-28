from pyspecdata import *
from scipy.optimize import leastsq,minimize
fl = figlist_var()
for id_string,label_string,col in [
        ('191017_HP_calib_coupler_1','10dB coupler','orange'),
        #('191105_HP_calib_20coupler_1','20dB coupler','purple'),
        ('191107_HP_calib_20coupler_1','20dB coupler','green'),
        ('191017_HP_calib_coupler_4','10dB coupler amp','purple'),
        ('191107_HP_calib_20coupler_3','20dB coupler amp','black'),
        ('191107_HP_calib_20coupler_3_2','20dB coupler amp','magenta'),
        ('191107_HP_calib_20coupler_4','20dB coupler amp','blue'),
        ('191107_HP_calib_20coupler_4_2','20dB coupler amp','cyan'),
        ]:

    data = load(getDATADIR(exp_type='test_equip')+id_string+'.npz')

    x_axis = data[data.files[0]]
    y_axis = data[data.files[1]]

    figure('Calib curve')
    title('Calibration curve')
    power_data = nddata(y_axis,['set_power'])
    if 'b12' in id_string:
        x_axis -= 35.0
    power_data.setaxis('set_power',x_axis)
    power_data['set_power',:] = y_axis[:]
    print(ndshape(power_data))
    fl.next('calib curve')
    fl.plot(power_data,'.-',label=label_string,c=col)
    #c,result = power_data.polyfit('set_power')
    #fl.plot(result,':',label='%f'%c[0],c=col)
    #plot(x_axis[1:],y_axis[1:],'o-',)
    
legend()
xlabel('programmed power (dBm)')
ylabel('output power (dBm)')
gridandtick(gca())
save_fig = False
if save_fig:
    savefig('calib_curve_191021.png',
            transparent=True,
            bbox_inches='tight',
            pad_inches=0)
fl.show();quit()
