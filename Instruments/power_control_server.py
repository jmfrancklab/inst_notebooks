# To be run from the computer connected to the EPR spectrometer
import sys, os, time, socket, pickle
from Instruments import Bridge12,prologix_connection,gigatronics,logobj


IP = "0.0.0.0"
PORT = 6002

def main():
    with prologix_connection() as p:
        with gigatronics(prologix_instance=p, address=7) as g:
            with Bridge12(prologix_object=p) as b:
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sock.bind((IP,PORT))
                this_logobj = logobj()
                def process_cmd(cmd,this_logobj):
                    leave_open = True
                    cmd = cmd.strip()
                    print("I am processing",cmd)
                    if this_logobj.currently_logging:
                        this_logobj.add(Rx = b.rxpowermv_float(),
                                power = g.read_power(),
                                cmd=cmd)
                    args = cmd.split(b' ')
                    print("I split it to ",args)
                    if len(args) == 3:
                        if args[0] == b'DIP_LOCK':
                            freq1 = float(args[1])
                            freq2 = float(args[2])
                            _,_,min_f = b.lock_on_dip(ini_range=(freq1*1e9,freq2*1e9))
                            b.set_freq(min_f)
                            min_f = float(b.freq_int())*1e3
                            conn.send(('%0.6f'%min_f).encode('ASCII'))
                        else:
                            raise ValueError("I don't understand this 3 component command")
                    if len(args) == 2:
                        if args[0] == b'SET_POWER':
                            dBm_setting = float(args[1])
                            last_power = b.power_float()
                            if dBm_setting > last_power + 3:
                                last_power += 3
                                nsecs = -1*time.time()
                                print("SETTING TO...",last_power)
                                b.set_power(last_power)
                                for j in range(30):
                                    if b.power_float() < last_power:
                                        time.sleep(0.1)
                                    else:
                                        break
                                nsecs += time.time()
                                print("took",j,"tries and",nsecs,"seconds")
                                while dBm_setting > last_power+3:
                                    last_power += 3
                                    nsecs = -1*time.time()
                                    print("SETTING TO...",last_power)
                                    b.set_power(last_power)
                                    for j in range(30):
                                        if b.power_float() < last_power:
                                            time.sleep(0.1)
                                        else:
                                            break
                                    nsecs += time.time()
                                    print("took",j,"tries and",nsecs,"seconds")
                            nsecs = -1*time.time()
                            b.set_power(dBm_setting)
                            for j in range(30):
                                if b.power_float() < last_power:
                                    time.sleep(0.1)
                                else:
                                    break
                            nsecs += time.time()
                            print("took",j,"tries and",nsecs,"seconds")
                        else:
                            raise ValueError("I don't understand this 2 component command:"+str(args))
                    elif len(args) == 1:
                        if args[0] == b'CLOSE':
                            print("closing connection")
                            leave_open = False
                            b.soft_shutdown()
                            conn.close()
                        elif args[0] == b'GET_POWER':
                            result = b.power_float()
                            conn.send(('%0.1f'%result).encode('ASCII'))
                        elif args[0] == b'MW_OFF':
                            b.soft_shutdown()
                            
                        elif args[0] == b'QUIT':
                            print("closing connection")
                            conn.close()
                            leave_open = False
                            quit()
                        elif args[0] == b'START_LOG':
                            this_logobj.currently_logging = True
                        elif args[0] == b'STOP_LOG':
                            this_logobj.currently_logging = False
                            retval = pickle.dumps(this_logobj) +b'ENDTCPIPBLOCK'
                            conn.send(retval)
                            this_logobj.reset()
                        elif args[0] == b'MW_OFF':
                            b.soft_shutdown()
                        else:
                            raise ValueError("I don't understand this 1 component command"+str(args))
                    return leave_open
                while True:
                    sock.listen(1)
                    print("I am listening")
                    conn, addr = sock.accept()
                    print("I have accepted from",addr)
                    leave_open = True
                    oldtimeout = conn.gettimeout()
                    while leave_open:
                        conn.settimeout(0.001)
                        try:
                            data = conn.recv(1024)
                            timelist = []
                            timelabels = []
                            conn.settimeout(oldtimeout)
                            timelist.append(time.time())
                            if oldtimeout is None:
                                timelabels.append("set timeout to None on receiving command, '%s'"%(data))
                            else:
                                timelabels.append("set timeout to %g on receiving command, '%s'"%(oldtimeout,data))
                            if len(data) > 0:
                                for cmd in data.strip().split(b'\n'):
                                    timelist.append(time.time())
                                    timelabels.append("about to process")
                                    leave_open = process_cmd(cmd,this_logobj)
                                    timelist.append(time.time())
                                    timelabels.append("processed %s"%cmd)
                            else:
                                print("no data received")
                                timelist.append(time.time())
                                timelabels.append("no data received")
                            print("time to process:")
                            print(" --> ".join([
                                timelabels[j] + ' --> ' + str(timelist[j+1]-timelist[j])
                                for j in range(len(timelist)-1)] + [timelabels[-1]]))
                        except socket.timeout as e:
                            if this_logobj.currently_logging:
                                this_logobj.add(Rx=b.rxpowermv_float(),
                                        power=g.read_power())
