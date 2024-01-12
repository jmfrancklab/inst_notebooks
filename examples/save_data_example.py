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
import SpinCore_pp
from Instruments import *
import os,sys,time
import random
import h5py
from datetime import datetime

# {{{create filename and save to config file
config_dict = SpinCore_pp.configuration("active.ini")
config_dict["type"] = "test_B12_log"
config_dict["date"] = datetime.now().strftime("%y%m%d")
filename = f"{config_dict['date']}_{config_dict['chemical']}_{config_dict['type']}.h5"
target_directory = getDATADIR(exp_type="ODNP_NMR_comp/test_equipment")
# }}}
# {{{set phase cycling
ph1_cyc = r_[0, 1, 2, 3]
ph2_cyc = r_[0]
#}}}
#{{{ params for Bridge 12/power
dB_settings = round(linspace(0,35,14)/0.5)*0.5
powers =1e-3*10**(dB_settings/10.)
nPoints = 2048
short_delay = 0.5
long_delay = 5
#}}}
#{{{ function that generates fake data with two indirect dimensions
def run_scans(indirect_idx, indirect_len, indirect_fields = None, ret_data=None):
    # there are many changes to this function that seem to be aimed
    # at making it more dependent on code that is elsewhere
    # this should be a simple example, so I'm rolling those back
    ph1_cyc = r_[0,1,2,3]
    ph2_cyc = r_[0]
    nPhaseSteps = len(ph1_cyc)*len(ph2_cyc)
    data_length = 2*nPoints*nEchoes*nPhaseSteps
    for x in range(nScans):
        raw_data = np.random.random(data_length) + np.random.random(data_length) * 1j
        data_array = complex128(raw_data[0::2]+1j*raw_data[1::2])
        dataPoints = int(shape(data_array)[0])
        if DNP_data is None and power_idx ==0 and field_idx == 0:
            time_axis = linspace(0.0,1*nPhaseSteps*85.3*1e-3,dataPoints)
            DNP_data = ndshape([len(powers),len(r_[3501:3530:0.1]),1,dataPoints],['power','field','nScans','t']).alloc(dtype=complex128)
            DNP_data.setaxis('power',r_[powers]).set_units('W')
            DNP_data.setaxis('field',r_[3501:3530:0.1]).set_units('G')
            DNP_data.setaxis('t',time_axis).set_units('t','s')
            DNP_data.setaxis('nScans',r_[0:1])
            DNP_data.name("node_name")
        DNP_data['power',power_idx]['field',field_idx]['nScans',x] = data_array
        if nScans > 1:
            DNP_data.setaxis('nScans',r_[0:1])
        return DNP_data
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
                config_dict['uw_dip_center_GHz'] - config_dict['uw_dip_width_GHz'] / 2,
                config_dict['uw_dip_center_GHz'] + config_dict['uw_dip_width_GHz'] / 2,
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

