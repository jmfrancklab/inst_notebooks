"test the power control server"
from Instruments.power_control import power_control
import time
import h5py
time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
with power_control() as p:
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
for j in range(len(log_array)):
    thistime, thisrx, thispower, thiscmd = log_array[j]
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(thistime)),
            thisrx,
            thispower,
            log_dict[thiscmd])
