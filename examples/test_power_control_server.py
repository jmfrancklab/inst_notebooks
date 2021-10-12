"""test the power control server

run this while running power_control_server.py on the same computer

generates hdf output to be read by test_power_control_server_read.py"""
from Instruments import power_control
import os, time, h5py
from numpy import empty
from matplotlib.ticker import FuncFormatter

time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
assert not os.path.exists('output.h5'), "later we can just check that the node doesn't exist, but in this example, we're writing a fresh h5 file"
with power_control() as p:
    retval = p.dip_lock(9.81,9.83)
    print(retval)
    for j in range(100):
        print(j)
        if j == 0:
            p.start_log()
        time.sleep(0.1)
        if j == 10:
            p.set_power(10.5)
        elif j == 20:
            p.set_power(12)
        elif j == 99:
            log_array, log_dict = p.stop_log()
    p.arrange_quit()
print("log array shape",log_array.shape)
with h5py.File('output.h5', 'a') as f:
    log_grp = f.create_group('log') # normally, I would actually put this under the node with the data
    dset = log_grp.create_dataset("log",data=log_array)
    dset.attrs['dict_len'] = len(log_dict)
    for j,(k,v) in enumerate(log_dict.items()):
       dset.attrs['key%d'%j] = k 
       dset.attrs['val%d'%j] = v 
