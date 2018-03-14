
# coding: utf-8

# # Initialization
# 
# to run on a different computer, run ``jupyter notebook --ip='*'`` copy and paste address and replace ``localhost`` with ``jmfranck-pi2.syr.edu`` (if on the internet) or ``192.168.1.20`` (if on local network)

# (test:make change to see if file commits to github)


get_ipython().magic(u'pylab inline')
from serial.tools.list_ports import comports, grep
import serial
import time
#import winsound
print serial.VERSION

def generate_beep(freq,duration):
    "Generates a beep -- used winsound.Beep under windows -- use pygame under linux"
    return
class Bridge12 (Serial):
    def __init__(self, *args, **kwargs):
        # Grab the port labeled as Arduino (since the Bridge12 microcontroller is an Arduino)
        portlist = [j.device for j in comports() if u'Arduino Due' in j.description]
        assert len(portlist)==1
        thisport = portlist[0]
        super(self.__class__, self).__init__(thisport, timeout=3, baudrate=115200)
        return self
    def bridge12_wait(self):
        #time.sleep(5)
        def look_for(this_str):
            for j in range(1000):
                a = self.read_until(this_str+'\r\n')
                time.sleep(0.1)
                #print "a is",repr(a)
                print "look for",this_str,"try",j+1
                if this_str in a:
                    print "found: ",this_str
                    break
        look_for('MPS Started')
        look_for('System Ready')
        return
    def help(self):
        self.write("help\r") #command for "help"
        print "after help:"
        entire_response = ''
        start = time.time()
        entire_response += self.readline()
        time_to_read_a_line = time.time()-start
        grab_more_lines = True
        while grab_more_lines:
            time.sleep(3*time_to_read_a_line)
            more = self.read_all()
            entire_response += more
            if len(more) == 0:
                grab_more_lines = False
        print repr(entire_response)
    def wgstatus_int_singletry(self):
        self.write('wgstatus?\r')
        return int(self.readline())
    def wgstatus_int(self):
        "need two consecutive responses that match"
        c = self.wgstatus_int_singletry()
        d = self.wgstatus_int_singletry()
        while c != d:
            c = d
            d = self.wgstatus_int_singletry()
        return c
    def set_wg(self,setting):
        """set *and check* waveguide

        Parameters
        ==========
        s: Serial object
            gives the connection
        setting: bool
            Waveguide setting appropriate for:
            True: DNP
            False: ESR
        """
        self.write('wgstatus %d\r'%setting)
        for j in range(10):
            result = self.wgstatus_int()
            if result == setting:
                return
        raise RuntimeError("After checking status 10 times, I can't get the waveguide to change")
        
    def ampstatus_int_singletry(self):
        self.write('ampstatus?\r')
        return int(self.readline())
    def ampstatus_int(self):
        "need two consecutive responses that match"
        a = self.ampstatus_int_singletry()
        b = self.ampstatus_int_singletry()
        while a != b:
            a = b
            b = self.ampstatus_int_singletry()
        return a
    def set_amp(self,setting):
        """set *and check* amplifier

        Parameters
        ==========
        s: Serial object
            gives the connection
        setting: bool
           Amplifier setting appropriate for:
            True: On
            False: Off
        """
        self.write('ampstatus %d\r'%setting)
        for j in range(10):
            result = self.ampstatus_int()
            if result == setting:
                return
        raise RuntimeError("After checking status 10 times, I can't get the amplifier to turn on/off")
        
    def rfstatus_int_singletry(self):
        self.write('rfstatus?\r')
        return int(self.readline())
    def rfstatus_int(self):
        "need two consecutive responses that match"
        f = self.rfstatus_int_singletry()
        g = self.rfstatus_int_singletry()
        while f != g:
            f = g
            g = self.rfstatus_int_singletry()
        return f
    def set_rf(self,setting):
        """set *and check* microwave power

        Parameters
        ==========
        s: Serial object
            gives the connection
        setting: bool
            Microwave Power setting appropriate for:
            True: On
            False: Off
        """
        self.write('rfstatus %d\r'%setting)
        for j in range(10):
            result = self.rfstatus_int()
            if result == setting:
                return
        raise RuntimeError("After checking status 10 times, I can't get the mw power to turn on/off")

    def power_int_singletry(self):
        self.write('power?\r')
        return int(self.readline())
    def power_int(self):
        "need two consecutive responses that match"
        h = self.power_int_singletry()
        i = self.power_int_singletry()
        while h != i:
            h = i
            i = self.power_int_singletry()
        return h
    def set_power(self,dBm):
        """set *and check* power

        Parameters
        ==========
        s: Serial object
            gives the connection
        dBm: float
            power values -- give a dBm (not 10*dBm) as a floating point number
        """
        setting = int(10*dBm+0.5)
        if setting > 150:
            raise ValueError("You are not allowed to use this function to set a power of greater than 15 dBm for safety reasons")
        elif setting < 0:
            raise ValueError("Negative dBm -- not supported")
        self.write('power %d\r'%setting)
        for j in range(10):
            result = self.power_int()
            if result == setting:
                return
        raise RuntimeError("After checking status 10 times, I can't get the power to change")
    def __enter__(self):
        self.bridge12_wait()
    def __exit__(self, exception_type, exception_value, traceback):
        self.set_power(0)
        self.set_rf(False)
        self.set_wg(False)
        return


# Print out the com ports, so we know what we're looking for

[(j.device, j.hwid, j.vid, j.description, j.manufacturer) for j in comports()] #list comprehension



    
# ###### Code for MW Power Test
# check that all the ``set_`` functions work correctly:

with Bridge12() as b:
    print "initial wg status:", self.wgstatus_int()
    self.set_wg(True)
    print "initial amp status:", self.ampstatus_int()
    self.set_amp(True)
    print "initial rf status:", self.rfstatus_int()
    self.set_rf(True)
    print "initial power:",self.power_int()
    self.set_power(10)
    print "up power:",self.power_int()
    time.sleep(10)

# # Stop here -- need to read, understand, and use the previous before proceeding

# ### Tuning Curve


freq = linspace(9.4e9,9.9e9, 50)
def freq_sweep(s,freq):
    """sweep over an array of frequencies

    Parameters
    ==========
    s: Serial object
        gives the connection
    freq: array of floats
        frequencies in Hz
        
    Returns
    =======
    rxvalues: array
        An array of floats, same length as freq, containing the receiver (reflected) power in dBm at each frequency.
    """    
    rxvalues = zeros(len(freq))
    #FREQUENCY AND RXPOWER SWEEP
    for j,f in enumerate(freq):
            time.sleep(0.5)
            generate_beep(500, 300)
            s.write('freq %.1f\r'%(f/1e3))
            time.sleep(0.1)
            s.write('rxpowerdbm?\r') 
            rx =s.readline()
            rxvalues[j] = float(rx)/10 
    return rxvalues
with serial.Serial(thisport, timeout=3, baudrate=115200) as s:
    bridge12_wait(s)
    #Turn Components On and Power to 10dBm
    set_wg(s,True)
    set_amp(s, True)
    set_rf(s, True)
    set_power(s,5.0)
    for j in range(1):
        rxvalues = freq_sweep(s,freq)
        plot(freq, rxvalues, alpha=0.5) #tuning curve
    #Turn Components Off and Power to 0dBm
    set_power(s,0)
    set_rf(s,False)
    set_wg(s,False)


# Testing Components of Tuning Curve Individually (Ctrl + / to comment out)


# with serial.Serial(thisport, timeout=3, baudrate=115200) as s:
#     bridge12_wait(s)
#     print "initial wg status:",wgstatus_int(s)
#     set_wg(s,True)
#     time.sleep(10)
#     set_wg(s,False)
#     print "final wg status:", wgstatus_int(s)
# with serial.Serial(thisport, timeout=3, baudrate=115200) as s:
#     bridge12_wait(s)
#     print "initial amp status:",ampstatus_int(s)
#     set_amp(s,True)
#     time.sleep(10)
#     set_amp(s,False)
#     print "final amp status:", ampstatus_int(s)
with serial.Serial(thisport, timeout=3, baudrate=115200) as s:
    bridge12_wait(s)
    print "initial wg status:",wgstatus_int(s)
    set_wg(s,True)
    print "initial rf status:",ampstatus_int(s)
    set_rf(s,True)
    time.sleep(10)
    set_rf(s,False)
    print "final rf status:", rfstatus_int(s)
    set_wg(s,False)
    print "final wg status:", wgstatus_int(s)


# There is an issue with ampstatus: the initial status is 1, which seems to be problematic. When I set it to True then False, the final amp status is 0.

# The same issue appears with the rfstatus, but in this case, the Bridge12 screen says the mw power is off but the "initial rf status" reads it as on.




