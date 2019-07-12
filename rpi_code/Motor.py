import datetime
import RPi.GPIO as g
import time
from gpiozero import CPUTemperature

import w1thermsensor
sensor1 = W1ThermSensor()

threshold_temp = 30
min_temp = 20.00
sensor1 = W1ThermSensor()
heater_pin = 22
g.setmode(g.BCM) 
g.setwarnings(False)
g.setup(heater_pin, g.OUT)
heater = g.PWM(heater_pin, True)
heater_on = False

time = datetime.datetime.now()

temp_array = []
time_array = []
NaN = float('nan')


try:
    while True: 
        messages = []
        maxr = 3
        retries = 0
        while retries<maxr: 
            try: 
                temp= sensor1.get_temperature()
                print "Temp is %0.2F"%temp
                temp_array.append(temp)
                time_array.append(time)
                # in here insert code for motor to run as well
               
                if temp == 85.00:
                    print "Ignoring temperature"
                    temp_array.append(NaN)
                else: 
                    temp= sensor1.get_temperature()
                    print "Temp is %0.2F"%temp
                    temp_array.append(temp)
                if (temp < threshold_temp): 
                    print "Turning Heater On" 
                    g.output(heater_pin, True)
                    heater_on = True
                    time.sleep(1)
                    if heater_on = True: 
                        print "Heater On"
                    else: 
                        print "Restarting Heater"
                        g.output(heater_pin, True)
                        heater_on = True        
                else: 
                    print "Temp Exceeded"
                    if heater_on is True: 
                        print "Turning Heater Off"
                        g.output(heater_pin, False) 
                        heater_on = False
                    else:
                        print "Heater Off"
                        heater_on = False 
                 np.savez("190712Heater", temp = temp_array, time = time_array)
            except Exception as e: 
                messages.append(e)
                print "Encountered error..."
                time.sleep(1)
            retries += 1
            







                    
