# coding: utf-8
# ## Initialization
#  
# To run on a different computer, run ``jupyter notebook --ip='*'`` copy and paste address and replace ``localhost`` with
# ``jmfranck-pi2.syr.edu`` (if on the internet) or ``192.168.1.20`` (if on local network)
from serial.tools.list_ports import comports
from serial import Serial
from numpy import *
import time

def generate_beep(f,dur):
    # do nothing -- can be used to generate a beep, but platform-dependent
    return
def convert_to_power(x):
    "Convert Rx mV values to powers (dBm)"
    y = 0
    c = r_[2.78135,25.7302,5.48909]
    for j in range(len(c)):
        y += c[j] * (x*1e-3)**(len(c)-j)
    return log10(y)*10.0+2.2

class Bridge12 (Serial):
    def __init__(self, *args, **kwargs):
        # Grab the port labeled as Arduino (since the Bridge12 microcontroller is an Arduino)
        cport = comports()
        if type(cport) is list and hasattr(cport[0],'device'):
            portlist = [j.device for j in comports() if u'Arduino Due' in j.description]
        elif type(cport.next()) is tuple:
            print "using fallback comport method"
            portlist = [j[0] for j in comports() if u'Arduino Due' in j[1]]
        else:
            raise RuntimeError("Not sure how how to grab the USB ports!!!")
        assert len(portlist)==1, "I need to see exactly one Arduino Due hooked up to the Raspberry Pi"
        thisport = portlist[0]
        super(self.__class__, self).__init__(thisport, timeout=3, baudrate=115200)
        # this number represents the highest possible reasonable value for the
        # Rx power -- it is lowered as we observe the Tx values
        self.safe_rx_level_int = 5000
        self.frq_sweep_10dBm_has_been_run = False
        self.tuning_curve_data = {}
        self._inside_with_block = False
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
        look_for('Synthesizer detected')
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
        retval = self.readline()
        if retval.strip() == 'ERROR':
            print "got an error from rfstatus, trying again"
            self.write('rfstatus?\r')
            retval = self.readline()
            if retval.strip() == 'ERROR':
                raise RuntimeError("Tried to read rfstatus twice, and got 'ERROR' both times!!")
        return int(retval)
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
        """set *and check* power.  On successful completion, set `self.cur_pwr_int` to 10*(power in dBm).

        Need to have 2 safeties for set_power:

        1. When power is increased above 10dBm, the power is not allowed to increase by more than 3dBm above the current power.
        2. When increasing the power, call the power reading function.

        Parameters
        ==========
        s: Serial object
            gives the connection
        dBm: float
            power values -- give a dBm (not 10*dBm) as a floating point number
        """
        if not self._inside_with_block: raise ValueError("you MUST use a with block so the error handling works well")
        setting = int(10*dBm+0.5)
        if setting > 400:
            raise ValueError("You are not allowed to use this function to set a power of greater than 40 dBm for safety reasons")
        elif setting < 0:
            raise ValueError("Negative dBm -- not supported")
        elif setting > 100:
            if not self.frq_sweep_10dBm_has_been_run:
                raise RuntimeError("Before you try to set the power above 10 dBm, you must first run a tuning curve at 10 dBm!!!")
            if not hasattr(self,'cur_pwr_int'):
                raise RuntimeError("Before you try to set the power above 10 dBm, you must first set a lower power!!!")
            if setting > 30+self.cur_pwr_int: 
                raise RuntimeError("Once you are above 10 dBm, you must raise the power in MAX 3 dB increments.  The power is currently %g, and you tried to set it to %g -- this is not allowed!"%(self.cur_pwr_int/10.,setting/10.))
        self.write('power %d\r'%setting)
        if setting > 0: self.rxpowermv_int_singletry() # doing this just for safety interlock
        for j in range(10):
            result = self.power_int()
            if setting > 0: self.rxpowermv_int_singletry() # doing this just for safety interlock
            if result == setting:
                self.cur_pwr_int = result
                return
        raise RuntimeError("After checking status 10 times, I can't get the power to change")
    def rxpowermv_int_singletry(self):
        """read the integer value for the Rx power (which is 10* the value in mV).  Also has a software interlock so that if the Rx power ever exceeds self.safe_rx_level_int, then the amp shuts down."""
        self.write('rxpowermv?\r')
        retval = self.readline()
        retval = int(retval)
        if retval > self.safe_rx_level_int:
            raise RuntimeError("Read an unsafe Rx level of %0.1fmV"%(retval/10.))
        return retval
    def rxpowermv_float(self):
        "need two consecutive responses that match"
        for j in range(3):
            # burn a few measurements
            self.rxpowermv_int_singletry()
        h = self.rxpowermv_int_singletry()
        i = self.rxpowermv_int_singletry()
        while h != i:
            h = self.rxpowermv_int_singletry()
            i = self.rxpowermv_int_singletry()
        return float(h)/10.
    def txpowermv_int_singletry(self):
        self.write('txpowermv?\r')
        return int(self.readline())
    def txpowermv_float(self):
        "need two consecutive responses that match"
        for j in range(3):
            # burn a few measurements
            self.txpowermv_int_singletry()
        h = self.txpowermv_int_singletry()
        i = self.txpowermv_int_singletry()
        while h != i:
            h = self.txpowermv_int_singletry()
            i = self.txpowermv_int_singletry()
        return float(h)/10.
    def set_freq(self,Hz):
        """set frequency

        Parameters
        ==========
        s: Serial object
            gives the connection
        Hz: float
            frequency values -- give a Hz as a floating point number
        """
        setting = int(Hz/1e3+0.5)
        self.write('freq %d\r'%(setting))
        if self.freq_int() != setting:
            for j in range(10):
                result = self.freq_int()
                if result == setting:
                    return
            raise RuntimeError("After checking status 10 times, I can't get the "
                           "frequency to change -- result is %d setting is %d"%(result,setting))
    def freq_int(self):
        "return the frequency, in kHz (since it's set as an integer kHz)"
        self.write('freq?\r')
        return int(self.readline())
    def freq_sweep(self,freq,dummy_readings=1,fast_run=True):
        """Sweep over an array of frequencies.
        **Must** be run at 10 dBm the first time around; will fail otherwise.

        Add arrays to the `self.tuning_curve_data` dictionary,
        stored with keys XXXdBm_rx XXXdBm_tx and XXXdBm_freq
        which store the tuning curve data.

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
        txvalues: array
            An array of floats, same length as freq, containing the transmitted power in dBm at each frequency.
        """    
        rxvalues = zeros(len(freq))
        txvalues = zeros(len(freq))
        if not self.frq_sweep_10dBm_has_been_run:
            if self.cur_pwr_int != 100:
                raise ValueError("You must run the frequency sweep for the first time at 10 dBm")
        #FREQUENCY AND RXPOWER SWEEP
        for j in range(dummy_readings):
            self.set_freq(freq[0])  #is this what I would put here (the 'f')?
            time.sleep(10e-3) # allow synthesizer to settle
            _ = self.txpowermv_float()
            _ = self.rxpowermv_float()
        for j,f in enumerate(freq):
            generate_beep(500, 300)
            self.set_freq(f)  #is this what I would put here (the 'f')?
            txvalues[j] = self.txpowermv_float()
            if fast_run:
                rxvalues[j] = self.rxpowermv_float()
            else:
                # the rxpowermv itself demands two consecutive responses to match
                # this then makes sure that three of those measurements match (so essentially, six in a row must match)
                def grab_consist_power():
                    rx_try1 = self.rxpowermv_float()
                    rx_try2 = self.rxpowermv_float()
                    for j in range(20):
                        rx_try3 = self.rxpowermv_float()
                        if rx_try1 == rx_try2 and rx_try2 == rx_try3:
                            rxvalues[j] = rx_try1
                            return rx_try1
                        else:
                            rx_try1,rx_try2 = rx_try2,rx_try3
                    raise ValueError("I tried 20 times to grab a consistent power, and could not (most recent %f, %f, %f)"%(rx_try1,rx_try2,rx_try3))
                rxvalues[j] = grab_consist_power()
        if self.cur_pwr_int == 100:
            self.frq_sweep_10dBm_has_been_run = True
            # reset the safe rx level to the top of the tuning curve at 10 dBm
            # (this is the condition where we are reflecting 10 dBm onto the Rx diode)
            #self.safe_rx_level_int = int(10*rxvalues.max())
        sweep_name = '%gdBm'%(self.cur_pwr_int/10.)
        self.tuning_curve_data[sweep_name+'_tx'] = txvalues
        self.tuning_curve_data[sweep_name+'_rx'] = rxvalues
        self.tuning_curve_data[sweep_name+'_freq'] = freq
        self.last_sweep_name = sweep_name
        return rxvalues, txvalues
    def lock_on_dip(self, dBm_increment = 3, n_freq_steps = 100):
        """Zoom in on freqs at half maximum of previous RX power, increase power by 3dBm, and run freq_sweep again.

        Parameters
        ==========
        dBm_increment: float
            Increase the power by this many dB.
        n_freq_steps: int
            In the increased power frequency sweep, use this many linearly interpolated frequency steps.

        Returns
        =======
        rxvalues: array
            An array of floats, same length as freq, containing the receiver (reflected) power in dBm at each frequency.
        txvalues: array
            An array of floats, same length as freq, containing the transmitted power in dBm at each frequency.
        """    
        if not self.frq_sweep_10dBm_has_been_run:
            self.set_power(10.0)
            self.set_mw(True)
            self.freq_sweep(
        assert self.frq_sweep_10dBm_has_been_run, "I should have run the 10 dBm curve -- not sure what happened"
        rx = self.tuning_curve_data[self.last_sweep_name+'_rx']
        freq = self.tuning_curve_data[self.last_sweep_name+'_freq']
        rx_dBm = convert_to_power(rx)
        #rx_midpoint = 0.25*max(rx_dBm)+0.75*min(rx_dBm)
        #if hasattr(self,'last_rx_midpoint') and self.last_rx_midpoint > rx_midpoint:
        #    rx_midpoint = self.last_rx_midpoint
        #else:
        #    self.last_rx_midpoint = rx_midpoint
        rx_midpoint = max(rx_dBm) - (abs(max(rx_dBm)) + abs(min(rx_dBm))/2)
        if hasattr(self,'last_rx_midpoint') and self.last_rx_midpoint > rx_midpoint:
            rx_midpoint = self.last_rx_midpoint
        else:
            self.last_rx_midpoint = rx_midpoint
        under_midpoint = []
        over_bool = rx_dBm > rx_midpoint
        currently_over = True
        for j,val in enumerate(over_bool):
            if currently_over:
                if not val:
                    start_under = j
                    currently_over = False
            else:
                if val:
                    under_midpoint.append([start_under,j])
                    currently_over = True
        under_midpoint_lengths = diff(array(under_midpoint),axis=0)
        if len(under_midpoint_lengths) > 1:
            longest_under_range = under_midpoint_lengths.argmax()
        else:
            longest_under_range = 0
        start_idx,stop_idx = array(under_midpoint[longest_under_range])
        start_idx = start_idx - 1
        freq_fit = linspace(freq[start_idx],freq[stop_idx],(stop_idx-start_idx+1))
        rx_fit = []
        for x in xrange(stop_idx-start_idx+1):
            rx_fit.append(rx_dBm[x+start_idx])
        p = polyfit(freq_fit,rx_fit,2)
        c,b,a = p 
        center = -b/2/c
        print "Predicted center frequency:",center*1e-9
        safe_rx = 3.0 #dBm, setting based off of values seeing in tests
        a -= safe_rx #shift parabola to safety threshold
        safe_crossing = (-b+r_[-sqrt(b**2-4*a*c),sqrt(b**2-4*a*c)])/2/c
        safe_crossing.sort()
        start_f,stop_f = safe_crossing
        freq = linspace(start_f,stop_f,n_freq_steps)
        self.set_power(dBm_increment+self.cur_pwr_int/10.)
        return self.freq_sweep(freq)

    # ### Need an increase_power_zoom function for zooming in on the tuning dip:
    # delete the following function
    def increase_power_zoom(self, dBm_increment = 3, n_freq_steps = 100):
        """Zoom in on freqs at half maximum of previous RX power, increase power by 3dBm, and run freq_sweep again.

        Parameters
        ==========
        dBm_increment: float
            Increase the power by this many dB.
        n_freq_steps: int
            In the increased power frequency sweep, use this many linearly interpolated frequency steps.

        Returns
        =======
        rxvalues: array
            An array of floats, same length as freq, containing the receiver (reflected) power in dBm at each frequency.
        txvalues: array
            An array of floats, same length as freq, containing the transmitted power in dBm at each frequency.
        """    
        assert self.frq_sweep_10dBm_has_been_run, "You're trying to run increase_power_zoom before you ran a frequency sweep at 10 dBm -- something is wonky!!!"
        rx = self.tuning_curve_data[self.last_sweep_name+'_rx']
        freq = self.tuning_curve_data[self.last_sweep_name+'_freq']
        rx1 = rx[1:]
        rx_midpoint = 0.25*max(rx1)+0.75*min(rx1)
        if hasattr(self,'last_rx_midpoint') and self.last_rx_midpoint > rx_midpoint:
            rx_midpoint = self.last_rx_midpoint
        else:
            self.last_rx_midpoint = rx_midpoint
        # {{{ construct two lists of lists that store the contiguous blocks where frequencies are under and over, respectively, the rx midpoint
        under_midpoint = []
        over_bool = rx1 > rx_midpoint
        currently_over = True
        for j,val in enumerate(over_bool):
            if currently_over:
                if not val:
                    start_under = j
                    currently_over = False
            else:
                if val:
                    under_midpoint.append([start_under,j])
                    currently_over = True

        under_midpoint_lengths = diff(array(under_midpoint),axis=0)
        if len(under_midpoint_lengths) > 1:
            longest_under_range = under_midpoint_lengths.argmax()
        else:
            longest_under_range = 0
        start_idx,stop_idx = array(under_midpoint[longest_under_range])+1 # for where the dip is underneath the midpoint
        # }}}
        freq = linspace(freq[start_idx], freq[stop_idx], n_freq_steps)
        self.set_power(dBm_increment+self.cur_pwr_int/10.)#will this even work? wouldn't the current power be 0 after the first tuning curve is obtained?
        return self.freq_sweep(freq)
        #if this is good, we could make a loop to run this iteratively, zooming in and ramping up the power each time :)
    def __enter__(self):
        self.bridge12_wait()
        self._inside_with_block = True
        return self
    def safe_shutdown(self):
        try:
            self.set_power(0)
        except Exception as e:
            print "error on standard shutdown during set_power -- running fallback shutdown"
            print "original error:"
            print e
            self.write('power %d\r'%0)
            self.write('rfstatus %d\r'%0)
            self.write('wgstatus %d\r'%0)
            self.close()
            return
        try:
            self.set_rf(False)
        except Exception as e:
            print "error on standard shutdown during set_rf -- running fallback shutdown"
            print "original error:"
            print e
            self.write('power %d\r'%0)
            self.write('rfstatus %d\r'%0)
            self.write('wgstatus %d\r'%0)
            self.close()
            return
        try:
            self.set_wg(False)
        except Exception as e:
            print "error on standard shutdown during set_wg -- running fallback shutdown"
            print "original error:"
            print e
            self.write('power %d\r'%0)
            self.write('rfstatus %d\r'%0)
            self.write('wgstatus %d\r'%0)
            self.close()
            return
        self.close()
        return
    def __exit__(self, exception_type, exception_value, traceback):
        self.safe_shutdown()
        return
