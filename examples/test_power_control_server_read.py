"Reads the output from test_power_control_server.py"
import os, time, h5py
import matplotlib as plt
from numpy import empty
@FuncFormatter
def thetime(x, position):
    result = time.localtime(x)
    return result.strftime('%I:%M%p')
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
        read_dict[dset.attrs['key%d'%j]] = dset.attrs['val%d'%j]
for j in range(len(read_array)):
    thistime, thisrx, thispower, thiscmd = read_array[j]
    print('%-04d'%j,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(thistime)),
            thisrx,
            thispower,
            read_dict[thiscmd])
ax = plt.gca()
ax.xaxis.set_major_formatter(thedate)
for whichfield in ['Rx', 'power']:
    ax.plot(read_array['time'], read_array[whichfield],
            label=whichfield)
mask = read_array['cmd'] != 0
for thistime in read_array['time'][mask]:
    plt.axvline(x=thistime)
ax.legend(**dict(bbox_to_anchor=(1.05,1), loc=2, borderaxespad=0.))
plt.tight_layout()
