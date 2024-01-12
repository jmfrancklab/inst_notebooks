"""
test of dip locking and logging
===============================

This is roughly derived from the combined_ODNP.py example in SpinCore.
Similar in fashion, the script generates a power list, and loops through
each power generating fake data using the run_scans function defined
below. At each power the "data" records the start and stop times that
will correspond to the times and powers inside the log allowing one to
average over each power step in a later post processing step. 
"""
from numpy import *
from numpy.random import rand
from pyspecdata import *
from pyspecdata.file_saving.hdf_save_dict_to_group import hdf_save_dict_to_group
from Instruments import *
import os,sys,time
import random
import h5py
from datetime import datetime

date = datetime.now().strftime("%y%m%d")
filename = date+'_'+"test_B12_log.h5"
target_directory = getDATADIR(exp_type="ODNP_NMR_comp/test_equipment")
# {{{set phase cycling
ph1_cyc = r_[0, 1, 2, 3]
ph2_cyc = r_[0]
#}}}
#{{{ params for Bridge 12/power
dB_settings = round(linspace(0,35,14)/0.5)*0.5
powers =1e-3*10**(dB_settings/10.)
nPoints = 2048
nEchoes = 1
nScans = 1
uw_dip_center_GHz = 9.82
uw_dip_width_GHz = 0.008
short_delay = 0.5
long_delay = 5
#}}}
#{{{ function that generates fake data with two indirect dimensions
def run_scans(indirect_idx, indirect_len, indirect_fields = None, ret_data=None):
    nPhaseSteps = len(ph1_cyc)*len(ph2_cyc)
    data_length = 2*nPoints*nEchoes*nPhaseSteps
    for nScans_idx in range(nScans):
        raw_data = np.random.random(data_length) + np.random.random(data_length) * 1j
        data_array = []
        data_array[::] = complex128(raw_data[0::2]+1j*raw_data[1::2])
        dataPoints = float(shape(data_array)[0])
        if ret_data is None:
            times_dtype = dtype(
                    [(indirect_fields[0],double),(indirect_fields[1],double)]
            )
            mytimes = zeros(indirect_len,dtype = times_dtype)
            time_axis =  r_[0:dataPoints] / (3.9 * 1e3)
            ret_data = ndshape(
                    [indirect_len,nScans,len(time_axis)],["indirect","nScans","t"]).alloc(dtype=complex128)
            ret_data.setaxis('indirect',mytimes)
            ret_data.setaxis('t',time_axis).set_units('t','s')
            ret_data.setaxis('nScans',r_[0:nScans])
        ret_data['indirect',indirect_idx]['nScans',nScans_idx] = data_array
    return ret_data
#}}}
power_settings_dBm = zeros_like(dB_settings)
with power_control() as p:
    for j,this_dB in enumerate(dB_settings):
        print("I'm going to pretend to run",this_dB,"dBm")
        if j == 0:
            time.sleep(short_delay)
            p.start_log()
        p.set_power(this_dB)
        for k in range(10):
            time.sleep(short_delay)
            if p.get_power_setting() >= this_dB: 
                break
        time.sleep(long_delay)
        power_settings_dBm[j] = p.get_power_setting()
        DNP_ini_time = time.time()
        if j == 0: 
            retval = p.dip_lock(
                uw_dip_center_GHz - uw_dip_width_GHz / 2,
                uw_dip_center_GHz + uw_dip_width_GHz / 2,
            ) #needed to set powers above 10 dBm - in future we plan on debugging so this is not needed
            DNP_data = run_scans(
                    indirect_idx=j,
                    indirect_len=len(powers),
                    indirect_fields=("start_times", "stop_times"),
                    ret_data=None,
                    )
        else:
            run_scans(
                    indirect_idx=j,
                    indirect_len=len(powers),
                    indirect_fields=("start_times", "stop_times"),
                    ret_data=DNP_data,
                    )
        DNP_done = time.time()
        if j == 0:
            time_axis_coords = DNP_data.getaxis("indirect")
        time_axis_coords[j]['start_times'] = DNP_ini_time
        time_axis_coords[j]['stop_times'] = DNP_done
    DNP_data.name("nodename_test")
    nodename = DNP_data.name()
    try:
        DNP_data.hdf5_write(filename,directory=target_directory)
    except:
        if os.path.exists("temp.h5"):
            os.remove("temp.h5")
            DNP_data.hdf5_write("temp.h5")
    this_log = p.stop_log()        
with h5py.File(os.path.normpath(os.path.join(target_directory, filename)),"a") as f:
    log_grp = f.create_group("log")
    hdf_save_dict_to_group(log_grp,this_log.__getstate__())

