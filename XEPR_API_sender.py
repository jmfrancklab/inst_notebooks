import socket
import sys

#IP = "127.0.0.1"
IP = "jmfrancklab-bruker.syr.edu"
#IP = "128.230.29.95"
if len(sys.argv) > 1:
    IP = sys.argv[1]
PORT = 6001

MESSAGE = '3506.4'
print("target IP:", IP)
print("target port:", PORT)
print("message:", MESSAGE)
print("SETTING FIELD TO...", MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
        socket.SOCK_STREAM) # TCP
sock.connect((IP, PORT))
sock.send(MESSAGE)
sock.close()
print("FIELD SET TO...", MESSAGE)
