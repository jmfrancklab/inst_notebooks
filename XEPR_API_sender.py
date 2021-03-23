import socket
import sys

#IP = "127.0.0.1"
IP = "jmfrancklab-bruker.syr.edu"
#IP = "128.230.29.95"
if len(sys.argv) > 1:
    IP = sys.argv[1]
PORT = 6001

MESSAGE = b'SET_FIELD 3506.4'
print("target IP:", IP)
print("target port:", PORT)
print("message:", MESSAGE)
print("SETTING FIELD TO...", MESSAGE)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((IP, PORT))
    sock.send(MESSAGE.encode('ASCII'))
    data = sock.recv(1024).decode('ASCII')
    print("FIELD SET TO...", data)
