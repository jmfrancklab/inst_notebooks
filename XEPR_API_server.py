# To be run from the computer connected to the EPR spectrometer
import sys, os, time
sys.path.append('/opt/Bruker/xepr/sharedProDeL/Standard/XeprAPI/')
import XeprAPI
x = XeprAPI.Xepr()
cmd = x.XeprCmds
cmd.aqSetServer('localhost')

# {{{ commands that can be run
def wait_for_run(exp):
    start_time = time.time()
    while time.time() - start_time < 60:
        time.sleep(0.1)
        if exp.aqGetExpState() == 5:
            print("experiment is running!!!")
            return
        elif exp.aqGetExpState() == 4:
            print("experiment is not running")
        else:
            print("I don't know what Exp State code",exp.aqGetExpState(),"means!")
    raise ValueError("timed out")
def wait_for_stop(exp):
    start_time = time.time()
    while time.time() - start_time < 60:
        time.sleep(0.1)
        if exp.aqGetExpState() == 4:
            print("experiment has stopped!!!")
            return
        elif exp.aqGetExpState() == 5:
            print("experiment is still running")
        else:
            print("I don't know what Exp State code",exp.aqGetExpState(),"means!")
    raise ValueError("timed out")
def wait_for_field(exp, field):
    r"""assuming we are running a sweep, wait for the field to hit the right value, and then abort"""
    start_time = time.time()
    while time.time() - start_time < 60:
        time.sleep(0.1)
        print("the field is",exp['FieldPosition'].value)
        if exp['FieldPosition'].value >= field:
            exp.aqExpAbort()
            wait_for_stop(exp)
            print("after stopping, the field is",exp['FieldPosition'].value)
            return exp['FieldPosition'].value
    raise ValueError("timed out")
def set_field(field):
    """run a sweep to set the field with high resolution

    requires the existence of experiment `set_field` in
    the Acquisition folder"""
    cmd.aqExpLoad(os.path.expanduser('~xuser/xeprFiles/Acquisition/set_field'))
    exp = x.XeprExperiment()
    desired_field = 3489.11
    exp["CenterField"].value = int(desired_field*10)/10.0 # nearest 0.1 beneath where I want to be
    exp["SweepWidth"].value = 0.2
    exp["SweepTime"].value = 60
    exp.aqExpRun()
    wait_for_run(exp)
    field_result = wait_for_field(exp,desired_field)
# }}}

IP = "0.0.0.0"
PORT = 6001

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
    sock.bind((IP,PORT))
    while True:
        sock.listen(1)
        conn, addr = sock.accept()
        with conn:
            data = conn.recv(1024)
            if len(data) > 0:
                if data.startswith('SET_FIELD'):
                    args = data.split(' ')
                    assert len(args)==2
                    field = double(args[1])
                    field_result = set_field(field)
                    conn.send('%f'%field_result)
            else:
                print("no data received")
