
# coding: utf-8

# 


get_ipython().magic(u'pylab inline')
from Instruments.bridge12 import Bridge12
#a dBm_increment of 0.1 does not work but 0.5 does


# 


freq = linspace(9.849e9,9.853e9, 200)
with Bridge12() as b:
    b.set_wg(True)
    b.set_amp(True)
    b.set_rf(True)
    b.set_power(10)
    b.freq_sweep(freq)
    for j in range(5):
        tuning_curve_data = b.tuning_curve_data
        b.increase_power_zoom(dBm_increment=2,n_freq_steps=20)
    for j in range(5):
        tuning_curve_data = b.tuning_curve_data
        b.increase_power_zoom(dBm_increment=1,n_freq_steps=10)
    for j in range(5):
        tuning_curve_data = b.tuning_curve_data
        b.increase_power_zoom(dBm_increment=0.5,n_freq_steps=10)
    for j in range(5):
        tuning_curve_data = b.tuning_curve_data
        b.increase_power_zoom(dBm_increment=0.5,n_freq_steps=5)


# 


x = '190222_Tuning_Curves_success'
from scipy.io import savemat, loadmat

series_names = [j.split('_')[0] for j in tuning_curve_data.keys() if '_freq' in j]
for this_series in series_names:
    figure(1)
    plot(tuning_curve_data[this_series+'_freq'],
         tuning_curve_data[this_series+'_rx'],
         'o-',
         markersize=3,
         alpha=0.5,
         label=this_series)
    figure(2)
    plot(tuning_curve_data[this_series+'_freq'],
         tuning_curve_data[this_series+'_tx'], 
         'o-',
         markersize=3,
         label=this_series)
figure(1)
legend(**dict(bbox_to_anchor=(1.05,1),loc=2,borderaxespad=0.))
title('Rx power (mV)')
# xlim(9.8495e9,9.851e9)
# ylim(-0.2,1.0)
figure(2)
legend(**dict(bbox_to_anchor=(1.05,1),loc=2,borderaxespad=0.))
title('Tx power (mV)')
savemat(x+'.mat',tuning_curve_data)


# 


series_names = [j.split('_')[0] for j in tuning_curve_data.keys() if '_freq' in j]
for this_series in series_names:
    figure(1)
    plot(tuning_curve_data[this_series+'_freq'],
         tuning_curve_data[this_series+'_rx'],
         'o-',
         markersize=3,
         alpha=0.5,
         label=this_series)
    figure(2)
    plot(tuning_curve_data[this_series+'_freq'],
         tuning_curve_data[this_series+'_tx'], 
         'o-',
         markersize=3,
         label=this_series)
figure(1)
legend(**dict(bbox_to_anchor=(1.05,1),loc=2,borderaxespad=0.))
title('Rx power (mV)')
xlim(9.8511e9,9.8515e9)
ylim(-0.3,2.2)
# savefig("TC_10dBm_20dBm_190222_2.png")
figure(2)
legend(**dict(bbox_to_anchor=(1.05,1),loc=2,borderaxespad=0.))
title('Tx power (mV)')
xlim(9.8511e9,9.8515e9)


# 


v

