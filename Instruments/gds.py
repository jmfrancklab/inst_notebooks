from pylab import *
from pyspecdata import nddata,strm
from .serial_instrument import SerialInstrument

import logging
logger = logging.getLogger('GDS Scope Class')

class GDS_scope (SerialInstrument):
    """Next, we can define a class for the scope, based on `pyspecdata`"""
    def __init__(self,model='3254'):
        super(self.__class__,self).__init__('GDS-'+model)
        logger.debug(strm("identify from within GDS",super(self.__class__,self).respond('*idn?')))
        logger.debug("I should have just opened the serial connection")
        return
    def autoset(self):
        self.write(':AUTOS')
    def waveform(self,ch=1):
        """Retrieve waveform and associated parameters form the scope.

        Comprises the following steps:

        * opens the port to the scope
        * acquires what is saved in memory as string
        * Divides this string at hashtag which separates settings from waveform

        Parameters
        ==========

        ch : int
            
            Which channel do you want?

        Returns
        =======

        data : nddata

            The scope data, as a pyspecdata nddata, with the
            extra information stored as nddata properties
        """
        self.write(':ACQ%d:MEM?'%ch)
        def upto_hashtag():
            this_char = self.read(1)
            this_line = ''
            while this_char != '#':          
                this_line += this_char
                this_char = self.read(1)
            return this_line

        #Further divides settings
        preamble = upto_hashtag().split(';')
        
        #Retrieves 'memory' of 25000 from settings
        #Waveform data is 50,000 bytes of binary data (2*mem)
        mem = int(preamble[0].split(',')[1])
        
        #Generates list of parameters in the preamble
        param = dict([tuple(x.split(',')) for x in preamble if len(x.split(',')) == 2])
        
        #Reads waveform data of 50,000 bytes
        self.read(6)# length of 550000
        data = self.read(50001)
        assert data[-1] == '\n', "data is not followed by newline!"
        data = data[:-1]

        # convert the binary string
        data_array = fromstring(data,dtype='i2')
        data_array =  double(data_array)/double(2**(2*8-1))

        # I could do the following
        #x_axis = r_[0:len(data_array)] * float(param['Sampling Period'])
        # but since I'm "using up" the sampling period, do this:
        x_axis = r_[0:len(data_array)] * float(param.pop('Sampling Period'))
        # r_[... is used by numpy to construct arrays on the fly

        # Similarly, use V/div scale to scale the y values of the data
        data_array *= float(param.pop('Vertical Scale'))/0.2 # we saw
        #              empirically that 0.2 corresponds to about 1 division
        data = nddata(data_array,['t']).setaxis('t',x_axis)
        data.set_units('t',param.pop('Horizontal Units').replace('S','s'))
        data.set_units(param.pop('Vertical Units'))
        name = param.pop('Source')
        # the last part is not actually related to the nddata object -- for convenience,
        # I'm just converting the data type of the remaining parameters
        def autoconvert_number(inpstr):
            try:
                retval = float(inpstr)
                isnumber = True
            except:
                retval = inpstr
                isnumber = False
            if isnumber:
                try:
                    intval = int(inpstr)
                    if str(intval) == inpstr:
                        retval = intval
                except:
                    pass
            return retval
        for j in param.keys():
            param[j] = autoconvert_number(param[j])
        data.other_info.update(param)
        data.name(name)
        return data
