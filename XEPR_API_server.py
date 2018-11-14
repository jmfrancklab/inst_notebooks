# To be run from the computer connected to the EPR spectrometer
import socket
import time, os, sys
sys.path.append('/opt/Bruker/xepr/sharedProDeL/Standard/XeprAPI/')
import XeprAPI
Xepr = XeprAPI.Xepr()
exp = Xepr.XeprExperiment() # requires you have loaded a prior dataset and used it to create new experiment

IP = "0.0.0.0"
PORT = 6001

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind((IP,PORT))
while True:
    sock.listen(1)
    conn, addr = sock.accept()
    data = conn.recv(1024)
    conn.close()
    if len(data) > 0:
        print data.strip()
        field = float(data.strip())
        print "Setting field to %f..."%field
        exp["CenterField"].value = field
        print "Field set to %f"%field
        print "Waiting for next instruction"
    else:
        print "None"
