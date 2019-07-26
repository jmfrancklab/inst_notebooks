import RPi.GPIO as g
from w1thermsensor import W1ThermSensor
#sensor1 = w1thermsensor.W1ThermSensor()
#print(sensor1)

#temp = sensor1.get_temperature()
#print(temp)
for sensor in W1ThermSensor.get_available_sensors():
    print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))

