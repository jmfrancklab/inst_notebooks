"Reads the output from test_power_control_server.py"
import os, time, h5py
import pylab as plt
from numpy import empty
from matplotlib.ticker import FuncFormatter
import matplotlib.transforms as transforms

@FuncFormatter
def thetime(x, position):
    result = time.localtime(x)
    return time.strftime('%I:%M%p',result)
with h5py.File('output.h5', 'r') as f:
    log_grp = f['log']
    dset = log_grp['log']
    print("length of dset",dset.shape)
    # {{{ convert to a proper structured array
    read_array = empty(len(dset), dtype=dset.dtype)
    read_array[:] = dset
    # }}}
    read_dict = {}
    for j in range(dset.attrs['dict_len']):
        val = dset.attrs['val%d'%j]
        if isinstance(val, bytes):
            val = val.decode('ASCII')
        read_dict[dset.attrs['key%d'%j]] = val
for j in range(len(read_array)):
    thistime, thisrx, thispower, thiscmd = read_array[j]
    print('%-04d'%j,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(thistime)),
            thisrx,
            thispower,
            read_dict[thiscmd])
fig, (ax_Rx,ax_power) = plt.subplots(2,1, figsize=(10,8))
ax_Rx.xaxis.set_major_formatter(thetime)
ax_power.xaxis.set_major_formatter(thetime)
ax_Rx.set_ylabel('Rx / mV')
ax_Rx.plot(read_array['time'], read_array['Rx'], '.')
ax_power.set_ylabel('power / dBm')
ax_power.plot(read_array['time'], read_array['power'], '.')
mask = read_array['cmd'] != 0
n_events = len(read_array['time'][mask])
trans_power = transforms.blended_transform_factory(
    ax_power.transData, ax_power.transAxes)
trans_Rx = transforms.blended_transform_factory(
    ax_Rx.transData, ax_Rx.transAxes)
for j,thisevent in enumerate(read_array[mask]):
    ax_Rx.axvline(x=thisevent['time'])
    ax_power.axvline(x=thisevent['time'])
    y_pos = j/n_events
    ax_Rx.text(thisevent['time'], y_pos, read_dict[thisevent['cmd']], transform=trans_Rx)
    ax_power.text(thisevent['time'], y_pos, read_dict[thisevent['cmd']], transform=trans_power)
#ax.legend(**dict(bbox_to_anchor=(1.05,1), loc=2, borderaxespad=0.))
plt.tight_layout()
plt.show()
