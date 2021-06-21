"Reads the output from test_power_control_server.py"
import os, time, h5py
from numpy import empty
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
