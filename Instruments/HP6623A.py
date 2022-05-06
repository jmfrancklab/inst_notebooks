from pylab import *
from .gpib_eth import gpib_eth
from .log_inst import logger

class HP6623A (gpib_eth):
    def __init__(self, prologix_instance=None, address=None):
        super().__init__(prologix_instance,address)
        self.stepsize = 0.5e6
    def set_output(self):
        self.write("VSET 1,0.0")
    def get_output(self):
        self.write("VOUT? 1")
        self.write("ENTER A")
        self.respond("DISP A")
    #def set_output(self,channel,voltage=None,current=None):
    #    if current is None:
    #        self.write("VSET %d,%f"%(channel,voltage))
    #    if voltage is None:
    #        self.write("ISET %d,%f"%(channel,current))
        #self.respond('ENTER A')
        #self.respond('DISP A', lines=2)
        #self.respond('DISP A', lines=2)
        #self.respond('OUTPUT 703;"VOUT? 1"',lines=2)
        #self.write('P%08dZ0'%int(round(frequency*1e-3)))# just use the 10 GHz setting, and fill out all the other decimal places with zeros
        return
    def close(self):
        #self.write(self.gpibaddress,'DE')         # Display Enable
##        self.write(self.gpibaddress,'HP')# if we don't do this, the display freezes
##        self.write(self.gpibaddress,'RP')# no longer output only mode
##        self.write(self.gpibaddress,'FP')# turn off "fast mode"??
##        self.write(self.gpibaddress,'R0')# switch back to high res
        super().close()
