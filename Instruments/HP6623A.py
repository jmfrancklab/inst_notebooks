from pylab import *
from .gpib_eth import gpib_eth
from .log_inst import logger

class HP6623A (gpib_eth):
    def __init__(self, prologix_instance=None, address=None):
        super().__init__(prologix_instance,address)
        self.stepsize = 0.5e6
    def set_voltage(self, ch, val):
        self.write("VSET %s,%s"%(str(ch),str(val)))
    def get_voltage(self, ch):
        self.write("VOUT? %s"%str(ch))
        return float(self.read())
    def set_current(self, ch, val):
        self.write("ISET %s,%s"%(str(ch),str(val)))
    def get_current(self, ch):
        self.write("IOUT? %s"%str(ch))
        return float(self.read())
    def output(self, ch, trigger):
        # trigger 0 is off, trigger 1 is on
        self.write("OUT %s,%s"%(str(ch),str(trigger)))
    def check_output(self, ch):
        self.write("OUT? %s"%str(ch))
        retval = float(self.read())
        if retval == 0:
            print("Ch %s output is OFF"%ch)
        elif retval == 1:
            print("Ch %s output is ON"%ch)
        return 
    def close(self):
        #self.write(self.gpibaddress,'DE')         # Display Enable
##        self.write(self.gpibaddress,'HP')# if we don't do this, the display freezes
##        self.write(self.gpibaddress,'RP')# no longer output only mode
##        self.write(self.gpibaddress,'FP')# turn off "fast mode"??
##        self.write(self.gpibaddress,'R0')# switch back to high res
        super().close()
