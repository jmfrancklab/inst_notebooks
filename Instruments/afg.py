from pylab import *
from pyspecdata import nddata,strm
from .serial_instrument import SerialInstrument

import logging
logger = logging.getLogger('AFG Scope Class')

class AFG (SerialInstrument):
    """Next, we can define a class for the scope, based on `pyspecdata`"""
    def __init__(self,model='2225'):
        super(self.__class__,self).__init__('AFG-'+model)
        logger.debug(strm("identify from within AFG",super(self.__class__,self).respond('*idn?')))
        logger.debug("I should have just opened the serial connection")
        return
    def sin(self,ch=1,V=1,f=1e6):
        """Outputs a sine wave of a particular frequency

        Parameters
        ==========

        
        ch : int
            
            On which channel do you want to ouput the sine wave?

        f : double

            frequency of the sine wave in SI units
        """
        # {{{ loop through units, and find the right one
        # Note that it interprets mhz in any case as mHz
        unit_list = ['mHZ','HZ','KHZ']
        f_list = [1e-3,1.0,1e3]
        for j,thisunit in enumerate(unit_list):
            thisf = f_list[j]
            if f < thisf: break
            unit_chosen = thisunit
            f_chosen = thisf
        # }}}
        cmd = 'SOUR%d:APPL:SIN %0.3f%s,1,0'%(ch,f/f_chosen,unit_chosen)
        print cmd
        self.write(cmd)
