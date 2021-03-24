# To be run from the computer connected to the EPR spectrometer
import sys, os, time, socket
from numpy import dtype, empty, concatenate
from numpy.random import rand


IP = "0.0.0.0"
PORT = 6002

log_list = []
# {{{ this is a structured array
log_dtype = dtype([('time','f8'),('Rx','f8'),('power','f8'),('cmd','i4')])
array_len = 10 # just the size of the buffer
log_array = empty(array_len, dtype=log_dtype)
log_cmds = {} # use hash to convert commands to a number, and this to look up the meaning of the hashes
# }}}
currently_logging = False
log_pos = 0

if True:
    if True:
        if True:
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
                            data = data.strip()
                            if currently_logging:
                                log_array[log_pos]['time'] = time.time()
                                log_array[log_pos]['Rx'] = rand()
                                log_array[log_pos]['power'] = rand()
                                thehash = hash(data)
                                log_cmds[thehash] = data
                                log_array[log_pos]['cmd'] = thehash
                                log_pos += 1
                                if log_pos == array_len:
                                    log_pos = 0
                                    log_list.append(log_array)
                                    log_array = empty(array_len, dtype=log_dtype)
                            args = data.split(' ')
                            print("I split it to ",args)
                            if len(args) == 3:
                                if args[0] == 'DIP_LOCK':
                                    freq1 = float(args[1])
                                    freq2 = float(args[2])
                                else:
                                    raise ValueError("I don't understand this 3 component command")
                            if len(args) == 2:
                                if args[0] == 'SET_POWER':
                                    dBm = float(args[1])
                                else:
                                    raise ValueError("I don't understand this 2 component command")
                            elif len(args) == 1:
                                if args[0] == 'CLOSE':
                                    print("closing connection")
                                    conn.close()
                                    leave_open = False
                                elif args[0] == 'START_LOG':
                                    currently_logging = True
                                elif args[0] == 'STOP_LOG':
                                    currently_logging = False
                                    retval = b''
                                    retval += pickle.dumps(log_dict)
                                    retval += b'ENDDICT'
                                    retval += pickle.dumps(concatenate(
                                        log_list+[log_array[:log_pos]]))
                                    retval += b'ENDARRAY'
                                    conn.send(retval)
                                else:
                                    raise ValueError("I don't understand this 1 component command")
                        else:
                            print("no data received")
                    except TimeoutError:
                        if currently_logging:
                            log_array[log_pos]['time'] = time.time()
                            log_array[log_pos]['Rx'] = rand()
                            log_array[log_pos]['power'] = rand()
                            thehash = hash(data)
                            log_cmds[thehash] = data
                            log_array[log_pos]['cmd'] = thehash
                            log_pos += 1
                            if log_pos == array_len:
                                log_pos = 0
                                log_list.append(log_array)
                                log_array = empty(array_len, dtype=log_dtype)
