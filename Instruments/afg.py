from pylab import *
from pyspecdata import nddata,strm
from .serial_instrument import SerialInstrument

import logging
logger = logging.getLogger('AFG Scope Class')

class AFG_Channel_Properties (object):
    """This class controls the channel properties (burst, output, etc.).
    
    By setting these up as properties, we allow tab completion, and for sensible manipulation of parameters.
    """
    def __init__(self,ch,afg):
        """initialize a new `AFG_Channel_Properties` class
        
        Properties
        ----------

        ch : int

            the AFG channel you are manipulating or learning about

        afg : AFG

            the AFG instance that initialized this
        """
        self.ch = ch
        self.afg = afg
        return
    @property
    def burst(self):
        cmd = 'SOUR%d:BURS:STAT?'%self.ch
        return bool(int(self.afg.respond(cmd)))
    @burst.setter
    def burst(self,onoff):
        if onoff:
            self.afg.write('SOUR%d:BURS:STAT ON'%self.ch)
        else:
            self.afg.write('SOUR%d:BURS:STAT OFF'%self.ch)
        self.afg.check_idn()
        return
    @property
    def output(self):
        cmd = 'OUTP%d?'%self.ch
        return bool(int(self.afg.respond(cmd)))
    @output.setter
    def output(self,onoff):
        if onoff:
            self.afg.write('OUTP%d ON'%self.ch)
        else:
            self.afg.write('OUTP%d OFF'%self.ch)
        self.afg.check_idn()
        return
    #ADDED AAB 171309 ***
    @property
    def sweep(self):
        cmd = 'SOUR%d:SWE:STAT?'%self.ch
        return bool(int(self.afg.respond(cmd)))
    @sweep.setter
    def sweep(self,onoff):
        if onoff:
            self.afg.write('SOUR%d:SWE:STAT ON'%self.ch)
        else:
            self.afg.write('SOUR%d:SWE:STAT OFF'%self.ch)
        self.afg.check_idn()
        return
    
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
    def binary_block(self,data):
        assert all(abs(data)<1), "all data must have absolute value less than 1"
        data = int16(data*511).tostring()
        data_len = len(data)
        data_len = str(data_len)
        assert (len(data_len) < 10), "the number describing the data length must be less than ten digits long, but your data length is "+data_len
        initialization = '#'+str(len(data_len))+data_len
        return initialization+data
    def digital_ndarray(self,data,ch=1):
        cmd = 'SOUR%d:DATA:DAC VOLATILE, '%ch
        cmd += self.binary_block(data)
        self.write(cmd)
        self.write('SOUR%d:ARB:OUTP'%ch)
        self.check_idn()
        return
    def set_sweep(self, start=3e3, stop=5e3, time=1, ch=1):
        assert time>=1e-3, "It seems like the AFG will only allow time values set to 1ms or higher"
        #self.write('SOUR%d:APPL:SIN'%ch)
        def make_regexp(x):
            '''generate the appropriate search string for the number x'''
            # generate the scientific notation representation we want
            x = '%+0.3E'%x
            # escape dots and plusses, which have a special meaning
            x = x.replace('.',r'\.').replace('+',r'\+')
            # ditch the last digit before the E, and allow anything to go there
            e_idx = x.find('E')
            x = x[:e_idx-1] + '.*' + x[e_idx:]
            return x
        f_str = '%+0.4E'%start
        self.write('SOUR%d:FREQ:STAR %+0.4E'%(ch,start))
        self.demand('SOUR%d:FREQ:STAR?'%ch,
                make_regexp(start))
        self.write('SOUR%d:FREQ:STOP %+0.4E'%(ch,stop))
        self.demand('SOUR%d:FREQ:STOP?'%ch,
                make_regexp(stop))
        self.write('SOUR%d:SWE:TIME %+0.4E'%(ch,time))
        self.demand('SOUR%d:SWE:TIME?'%ch,
                make_regexp(time))
        return
    @property
    def CH1(self):
        "Properties of channel 1 (on, burst, etc.) -- given as a :class:`AFG_Channel_Properties` object"
        if hasattr(self,'_ch1_class'):
            return self._ch1_class
        else:
            self._ch1_class = AFG_Channel_Properties(1,self)
        return self._ch1_class
    @CH1.deleter
    def CH1(self):
        del self._ch1_class
    @property
    def CH2(self):
        "Properties of channel 2 (on, burst, etc.) -- given as a :class:`AFG_Channel_Properties` object"
        if hasattr(self,'_ch2_class'):
            return self._ch2_class
        else:
            self._ch2_class = AFG_Channel_Properties(2,self)
        return self._ch2_class
    @CH2.deleter
    def CH2(self):
        del self._ch2_class

