# To be run from the computer connected to the EPR spectrometer
import sys, os, time, socket
from Instruments import Bridge12,prologix_connection,gigatronics


IP = "0.0.0.0"
PORT = 6002

power_log = []

with prologix_connection() as p:
    with gigatronics(prologix_instance=p, address=7) as g:
        with Bridge12() as b:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.bind((IP,PORT))
            while True:
                sock.listen(1)
                print("I am listening")
                conn, addr = sock.accept()
                print("I have accepted from",addr)
                leave_open = True
                oldtimeout = sock.gettimeout()
                while leave_open:
                    sock.settimeout(0.1)
                    try:
                        data = conn.recv(1024)
                        sock.settimeout(oldtimeout)
                        if len(data) > 0:
                            print("I received a command '",data,"'")
                            args = data.split(' ')
                            print("I split it to ",args)
                            if len(args) == 3:
                                if args[0] == 'DIP_LOCK':
                                    freq1 = float(args[1])
                                    freq2 = float(args[2])
                                    b.lock_on_dip(ini_range=(freq1,freq2))
                                else:
                                    raise ValueError("I don't understand this 3 component command")
                            if len(args) == 2:
                                if args[0] == 'SET_POWER':
                                    dBm = float(args[1])
                                    b.set_power(dBm)
                                else:
                                    raise ValueError("I don't understand this 2 component command")
                            elif len(args) == 1:
                                if args[0] == 'CLOSE':
                                    print("closing connection")
                                    conn.close()
                                    leave_open = False
                                else:
                                    raise ValueError("I don't understand this 1 component command")
                        else:
                            print("no data received")
                    except TimeoutError:
                        power_log.append(g.get_power())
