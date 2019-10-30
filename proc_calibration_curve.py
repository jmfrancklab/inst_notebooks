from pyspecdata import *
from scipy.optimize import leastsq,minimize
fl = figlist_var()
for id_string,label_string,col in [
        ('191008_HP_calib_2','HP source','orange'),
        ('191009_b12_calib_2','B12 source','blue'),
        ('191017_HP_calib_coupler_2','HP source -10 dB (directional coupler)','red'),
        ('191017_HP_calib_coupler_3_2','HP source - directional coupler insertion loss','violet'),
        ('191017_HP_calib_coupler_4','amplified -10 dB, HP source','green'),
        ('191021_b12_calib_2','amplified -10 dB, B12 source','cyan'),
        #('191030_b12_calib_1','amplified -10 dB, B12 source (replaced double right angle SMA)','black'),
        #('191030_HP_calib_coupler_2','amplified -10 dB, HP source with B12 source running','black'),
        #('191030_b12_calib_2','B12 source, with HP and amplifier running','magenta'),
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
    print ndshape(power_data)
    fl.next('calib curve')
    fl.plot(power_data,'.-',label=label_string,c=col)
    #c,result = power_data.polyfit('set_power')
    #fl.plot(result,':',label='%f'%c[0],c=col)
    #plot(x_axis[1:],y_axis[1:],'o-',)
    
legend()
xlabel('programmed power (dBm)')
ylabel('output power (dBm)')
gridandtick(gca())
fl.show()
show()
