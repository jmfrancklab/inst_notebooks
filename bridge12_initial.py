from serial.tools.list_ports import comports, grep
import serial
import time

portlist = [j.device for j in comports() if j.description==u'Arduino Due Programming Port (COM3)']
assert len(portlist)==1
thisport = portlist[0]
with serial.Serial(thisport, timeout=1) as s:
    time.sleep(20)
    print "done"
    s.write("freq 9505.0\r")
    s.write("help\r")
    print s.read_all()
    
   

