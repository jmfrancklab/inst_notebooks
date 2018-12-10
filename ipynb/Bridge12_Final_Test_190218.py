
# coding: utf-8

# 


get_ipython().magic(u'pylab inline')
sys.path.append('..')
from Instruments.bridge12 import Bridge12
import time
#a dBm_increment of 0.1 does not work but 0.5 does


# # our basic test to see that Bridge12 behaves reasonably
# 
# (frequency range is appropriate when NMR probe is in cavity)

# 


freq = linspace(9.816e9,9.825e9, 100)
with Bridge12() as b:
    b.set_wg(True)
    b.set_amp(True)
    b.set_rf(True)
    b.set_power(10)
    b.freq_sweep(freq)
    tuning_curve_data = b.tuning_curve_data
    for j in range(6):
        print "power currently at %f and increasing by 1 dB"%(b.cur_pwr_int/10.0)
        tuning_curve_data = b.tuning_curve_data
        b.increase_power_zoom(dBm_increment=1,n_freq_steps=15)


# 


# check the zero point of the mV reading -- was giving some -0.2 mV before update

with Bridge12() as b:
    time.sleep(5)
    print "power Rx",b.rxpowermv_float()
    print "power Tx",b.txpowermv_float()
    b.write('rxdiodesn?\r')
    print "serial number for rx serial:"
    print b.readline()
    b.write('txdiodesn?\r')
    print "serial number for tx serial:"
    print b.readline()
    time.sleep(5)


# 


x = '190227_Tuning_Curves_after_update_run8'
def convert_to_power(x):
    y = 0
    c = r_[2.78135,25.7302,5.48909]
    for j in range(len(c)):
        y += c[j] * (x*1e-3)**(3-j)
    return log10(y)*10.0+2.2
from scipy.io import savemat, loadmat
series_names = [j.split('_')[0] for j in tuning_curve_data.keys() if '_freq' in j]
for this_series in series_names:
    figure(1)
    plot(tuning_curve_data[this_series+'_freq']/1e9,
         convert_to_power(tuning_curve_data[this_series+'_rx']),
         'o-',
         markersize=3,
         alpha=0.5,
         label=this_series)
    figure(2)
    plot(tuning_curve_data[this_series+'_freq']/1e9,
         tuning_curve_data[this_series+'_tx'], 
         'o-',
         markersize=3,
         label=this_series)
figure(1)
legend(**dict(bbox_to_anchor=(1.05,1),loc=2,borderaxespad=0.))
title('Rx power (dBm)')
# xlim(9.8495e9,9.851e9)
# ylim(-0.2,3)
plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
xticks(rotation=45)
xlim((9.82,9.821))
xlabel('freq / GHz')
figure(2)
legend(**dict(bbox_to_anchor=(1.05,1),loc=2,borderaxespad=0.))
title('Tx power (mV)')
plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
xticks(rotation=45)
xlabel('freq / GHz')
savemat(x+'.mat',tuning_curve_data)


# ## crank up the power, and then hold frequency

# 


#freq = (linspace(-0.005,0.005,100)+9.82046)*1e9
freq = linspace(9.816e9,9.825e9, 70)
with Bridge12() as b:
    b.set_wg(True)
    b.set_amp(True)
    b.set_rf(True)
    b.set_power(10)
    b.freq_sweep(freq)
    tuning_curve_data = b.tuning_curve_data
    for j in range(9):
        tuning_curve_data = b.tuning_curve_data
        print "power currently at %f and increasing by 1 dB"%(b.cur_pwr_int/10.0)
        b.increase_power_zoom(dBm_increment=1,n_freq_steps=15)
    center_freq = tuning_curve_data[b.last_sweep_name+'_freq'].mean()
    print "setting frequency to %f GHz"%(center_freq/1e9)
    b.set_freq(center_freq)
    for j in range(19*2):
        new_power = float(b.cur_pwr_int) / 10.0 + 0.5
        print "%d increasing power to %f dBm"%(j,new_power)
        b.set_power(new_power)
        print "read power of %f mV"%b.rxpowermv_float()
        if b.cur_pwr_int > 270:
            print "let's see if it drifts"
            for k in range(10):
                time.sleep(1)
                print "read power of %f mV"%b.rxpowermv_float()
    time.sleep(2.0)


# # other stuff --?

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

