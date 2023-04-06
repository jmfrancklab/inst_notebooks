import os, time, h5py
from numpy import empty
from matplotlib.ticker import FuncFormatter
from pyspecdata.file_saving.hdf_save_dict_to_group import hdf_save_dict_to_group
init_logging(level='debug')

with power_control() as p:
    retval = p.dip_lock(9.81,9.83)
    p.start_log()
    this_log = p.stop_log()
log_dict = this_log.log_dict
with h5py.File('output.h5', 'a') as f:
    log_grp = f.create_group('log') # normally, I would actually put this under the node with the data
    hdf_save_dict_to_group(log_grp, this_log.__getstate__())
