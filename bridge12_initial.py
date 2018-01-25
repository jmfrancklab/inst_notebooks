from serial.tools.list_ports import comports, grep
import serial
portlist = [j.device for j in comports() if j.description==u'Arduino Due Programming Port (COM3)']
assert len(portlist)==1
thisport = portlist[0]
with serial.Serial(thisport, timeout=1) as s:
    s.write("help\n")
    print s.read_all()
