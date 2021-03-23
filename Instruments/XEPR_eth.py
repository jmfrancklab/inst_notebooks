import socket
import sys

#IP = "127.0.0.1"
IP = "jmfrancklab-bruker.syr.edu"
#IP = "128.230.29.95"
if len(sys.argv) > 1:
    IP = sys.argv[1]
PORT = 6001

class xepr(object):
    """wraps the ethernet connection to the XEPR server and allows you to send commands (provides a with block)"""
    def __init__(self, ip=IP, port=PORT):
        print("target IP:", IP)
        print("target port:", PORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((IP, PORT))
        self.exp_has_been_run = False
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        self.sock.close()
        return 
    def get(self):
        data = self.sock.recv(1024).decode('ASCII').strip()
        success = False
        for j in range(30):
            if len(data) == 0:
                data = self.sock.recv(1024).decode('ASCII').strip()
            else:
                success = True
                break
        if not success: raise ValueError("no response after 30 tries!!")
        return data
    def send(self,msg):
        self.sock.send(msg.encode('ASCII'))
        return
    def set_field(self,field):
        "Sets the current field with high accuracy"
        self.send('SET_FIELD %0.2f'%field)
        self.exp_has_been_run = True
        return float(self.get())
    def set_coarse_field(self,field):
        "Sets the field to the nearest 0.1G"
        self.send('SET_COARSE_FIELD %0.2f'%field)
        self.exp_has_been_run = True
        return float(self.get())
    def get_field(self):
        "Gets the current Hall probe reading"
        self.send('GET_FIELD')
        if not self.exp_has_been_run: raise ValueError("You can't run this because you haven't run an experiment yet!")
        retval = self.get()
        try:
            retval = float(retval)
        except:
            raise ValueError("can't convert",repr(retval),"to a float!")
