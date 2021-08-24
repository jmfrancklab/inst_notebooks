# To be run from the computer connected to the EPR spectrometer
import sys, os, time, socket, pickle
from numpy import dtype, empty, concatenate
from numpy.random import rand


IP = "0.0.0.0"
PORT = 6002

log_list = []
# {{{ this is a structured array
log_dtype = dtype([('time','f8'),('Rx','f8'),('power','f8'),('cmd','i8')])
array_len = 1000 # just the size of the buffer
log_array = empty(array_len, dtype=log_dtype)
log_dict = {0:""} # use hash to convert commands to a number, and this to look up the meaning of the hashes
# }}}
currently_logging = False
def main():
    print("once script works, move code into here")

if True:
    if True:
        if True:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.bind((IP,PORT))
            log_pos = 0
            def process_cmd(cmd,currently_logging,log_list,log_array,log_pos):
                leave_open = True
                cmd = cmd.strip()
                print("I am processing",cmd)
                if currently_logging:
                    log_array[log_pos]['time'] = time.time()
                    log_array[log_pos]['Rx'] = rand()
                    log_array[log_pos]['power'] = rand()
                    thehash = hash(cmd)
                    log_dict[thehash] = cmd
                    log_array[log_pos]['cmd'] = thehash
                    log_pos += 1
                    if log_pos == array_len:
                        log_pos = 0
                        log_list.append(log_array)
                        log_array = empty(array_len, dtype=log_dtype)
                args = cmd.split(b' ')
                print("I split it to ",args)
                if len(args) == 3:
                    if args[0] == b'DIP_LOCK':
                        freq1 = float(args[1])
                        freq2 = float(args[2])
                        time.sleep(1)
                        conn.send(('%0.6f'%min_f).encode('ASCII'))
                    else:
                        raise ValueError("I don't understand this 3 component command")
                if len(args) == 2:
                    if args[0] == b'SET_POWER':
                        dBm_setting = float(args[1])
                        last_power = dBm_setting
                        if dBm_setting > last_power + 3:
                            last_power += 3
                            print("SETTING TO...",last_power)
                            while dBm_setting > last_power+3:
                                last_power += 3
                                print("SETTING TO...",last_power)
                            print("FINALLY - SETTING TO DESIRED POWER")
                    else:
                        raise ValueError("I don't understand this 2 component command:"+str(args))
                elif len(args) == 1:
                    if args[0] == b'CLOSE':
                        print("closing connection")
                        leave_open = False
                        conn.close()
                    elif args[0] == b'GET_POWER':
                        result = rand()
                        conn.send(('%0.1f'%result).encode('ASCII'))
                    elif args[0] == b'QUIT':
                        print("closing connection")
                        conn.close()
                        leave_open = False
                        quit()
                    elif args[0] == b'START_LOG':
                        currently_logging = True
                    elif args[0] == b'STOP_LOG':
                        currently_logging = False
                        retval = b''
                        retval += pickle.dumps(log_dict)
                        retval += b'ENDDICT'
                        total_log = concatenate(log_list+[log_array[:log_pos]])
                        print("shape of total log",total_log.shape)
                        retval += pickle.dumps(total_log)
                        retval += b'ENDARRAY'
                        conn.send(retval)
                        log_list = []
                        log_array = empty(array_len, dtype=log_dtype)
                        log_pos = 0
                    else:
                        raise ValueError("I don't understand this 1 component command"+str(args))
                return log_pos,leave_open,currently_logging
            while True:
                sock.listen(1)
                print("I am listening")
                conn, addr = sock.accept()
                print("I have accepted from",addr)
                leave_open = True
                oldtimeout = conn.gettimeout()
                while leave_open:
                    conn.settimeout(0.1)
                    try:
                        data = conn.recv(1024)
                        conn.settimeout(oldtimeout)
                        if len(data) > 0:
                            print("I received a command '",data,"'")
                            for cmd in data.strip().split(b'\n'):
                                log_pos,leave_open,currently_logging = process_cmd(cmd,currently_logging,log_list,log_array,log_pos)
                        else:
                            print("no data received")
                    except socket.timeout as e:
                        if currently_logging:
                            log_array[log_pos]['time'] = time.time()
                            log_array[log_pos]['Rx'] = rand()
                            log_array[log_pos]['power'] = rand()
                            log_array[log_pos]['cmd'] = 0
                            log_pos += 1
                            if log_pos == array_len:
                                log_pos = 0
                                log_list.append(log_array)
                                log_array = empty(array_len, dtype=log_dtype)
