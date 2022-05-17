from pylab import *
from .gpib_eth import gpib_eth
from .log_inst import logger

class HP6623A (gpib_eth):
    def __init__(self, prologix_instance=None, address=None):
        super().__init__(prologix_instance,address)
        # here, call ID? to verify the ID of the instrument -- we have
        # used this in the past to, e.g. cycle through and find an
        # instrument by identifying where no error is thrown (or
        # something like this,  but I remember the ID being useful)
        idstring = self.respond('ID?') # Check ID command
    def set_voltage(self, ch, val):
        r"""set voltage
        
        Parameters
        ----------
        ch: int
            channel (1, 2, or 3)
        val: float
            voltage (in Volts) to be output on specified
            channel (see limits specific to each
            ch)
        """
        self.write("VSET %s,%s"%(str(ch),str(val)))
    def get_voltage(self, ch):
        r"""get voltage at channel as measured by supply
        meter
        
        Parameters
        ----------
        ch: int
            channel (1, 2, or 3)
        """
        self.write("VOUT? %s"%str(ch))
        return float(self.read())
    def set_current(self, ch, val):
        r"""set voltage
        
        Parameters
        ----------
        ch: int
            channel (1, 2, or 3)
        val: float
            current (in Amps) to be output on specified
            channel (see limits specific to each
            ch)
        """
        self.write("ISET %s,%s"%(str(ch),str(val)))
    def get_current(self, ch):
        r"""get current at channel as measured by supply
        meter
        
        Parameters
        ----------
        ch: int
            channel (1, 2, or 3)
        """
        self.write("IOUT? %s"%str(ch))
        return float(self.read())
    def output(self, ch, trigger):
        r"""set channel to be on and off (i.e., output
        or not)
        
        Parameters
        ----------
        ch: int
            channel (1, 2, or 3)
        trigger: int
            set to False to turn OFF output,
            set to True to turn ON output
        """
        self.write("OUT %s,%s"%(str(ch),str(int(trigger))))
    def check_output(self, ch):
        r"""check output status of specified
        channel
        
        Parameters
        ----------
        ch: int
            channel (1, 2, or 3)
        """
        self.write("OUT? %s"%str(ch))
        retval = float(self.read())
        if retval == 0:
            print("Ch %s output is OFF"%ch)
        elif retval == 1:
            print("Ch %s output is ON"%ch)
        return 
    def close(self):
        super().close()
