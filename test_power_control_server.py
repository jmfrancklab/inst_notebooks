"test the power control server"
from Instruments.power_control import power_control
import time
time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
with power_control() as p:
    for j in range(100):
        if j == 0:
            p.start_log()
        time.sleep(0.1)
        if j == 10:
            p.set_power(10.5)
        elif j == 20:
            p.set_power(12)
        elif j == 99:
            p.stop_log()
