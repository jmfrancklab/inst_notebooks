
# coding: utf-8

#get_ipython().magic(u'load_ext pyspecdata.ipy')
from pyspecdata import *
from serial.tools.list_ports import comports
import serial

# the following just sets up a log file -- ignore
# (copy of pyspecdata init_logging)


import logging,os
init_logging() # from pyspecdata --> goes to ~/pyspecdata.log
def strm(*args):
    return ' '.join([str(j) for j in args])
FORMAT = "--> %(filename)s(%(lineno)s):%(name)s %(funcName)20s %(asctime)20s\n%(levelname)s: %(message)s"
#log_filename = os.path.join(os.path.expanduser('~'),'pyspecdata.log')
#if os.path.exists(log_filename):
#    # manually remove, and then use append -- otherwise, it won't write to
#    # file immediately
#    os.remove(log_filename)
#logging.basicConfig(format=FORMAT,
#        filename=log_filename,
#        filemode='a',
#        )
logger = logging.getLogger('GDS_scope')
logger.setLevel(logging.DEBUG)


# Here, I search through the comports in order to identify the instrument that I'm interested in.  This (or something like this) should work on either Windows or Mac/Linux.
# I can use this to initialize a class.
# Note that later, we might want to replace this with a class that relies on pyVISA rather than directly calling the serial connection.


class SerialInstrument (object):
    """Class to describe an instrument connected using pyserial.
    Provides initialization (:func:`__init__`) to start the connection,
    as well as :func:`write` :func:`read` and :func:`respond` functions.
    Can be used inside a with block.
    """
    def __init__(self,textidn, **kwargs):
        """Initialize a serial connection based on the identifier string
        `textidn`, and assign it to the `connection` attribute

        Parameters
        ==========

        textidn : str
            
            A string used to identify the instrument.
            Specifically, the instrument responds to the ``*idn?`` command
            with a string that includes ``textidn``.
            If textidn is set to None, just show the available instruments.
        """
        if textidn is None:
            self.show_instruments()
        self.connection = serial.Serial(self.id_instrument(textidn), **kwargs)
        assert self.connection.isOpen(), "For some reason, I couldn't open the connection!"
        logger.debug('opened serial connection, and set to connection attribute')
        return
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        self.connection.close()
        return
    def write(self,*args):
        """Send info to the instrument.  Take a comma-separated list of
        arguments, which are converted to strings and separated by a space.
        (Similar to a print command, but directed at the instrument)"""
        text = ' '.join([str(j) for j in args])
        logger.debug(strm("when trying to write, port looks like this:",self.connection))
        self.connection.write(text+'\n')
        return
    def read(self, *args, **kwargs):
        return self.connection.read(*args, **kwargs)
    def flush(self):
        """Flush the input (say we didn't read all of it, *etc.*)
        
        Note that there are routines called "flush" in serial, but these
        seem to not be useful.
        """
        old_timeout = self.connection.timeout
        self.connection.timeout = 1
        result = 'blah'
        while len(result)>0:
            result = self.connection.read(2000)
        self.connection.timeout = old_timeout
        return
    def respond(self,*args, **kwargs):
        """Same a write, but also returns the result
        
        Parameters
        ----------
        message_len : int

            If present, read a message of a specified number of bytes.
            if not present, return a text line (readline).
        """
        message_len = None
        if 'message_len' in kwargs:
            message_len = kwargs.pop('message_len')
        self.write(*args)
        old_timeout = self.connection.timeout
        self.connection.timeout = None
        if message_len is None:
            retval = self.connection.readline()
        else:
            retval = self.connection.read(message_len)
        self.connection.timeout = old_timeout
        return retval
    def show_instruments(self):
        """For testing.  Same as :func:`id_instrument`, except that it just prints the idn result from all com ports.
        """
        old_timeout = self.connection.timeout
        self.connection.timeout = 0.1
        for j in comports():
            port_id = j[0] # based on the previous, this is the port number
            with serial.Serial(port_id) as s:
                assert s.isOpen(), "For some reason, I couldn't open the connection for %s!"%str(port_id)
                s.write('*idn?\n')
                result = s.readline()
                print result
        self.connection.timeout = old_timeout
    def id_instrument(self,textidn):
        """A helper function for :func:`init` Identify the instrument that returns an ID string containing ``textidn``
        """
        old_timeout = self.connection.timeout
        self.connection.timeout = 0.1
        for j in comports():
            port_id = j[0] # based on the previous, this is the port number
            with serial.Serial(port_id) as s:
                assert s.isOpen(), "For some reason, I couldn't open the connection for %s!"%str(port_id)
                s.write('*idn?\n')
                result = s.readline()
                if textidn in result:
                    self.connection.timeout = old_timeout
                    return port_id
        self.connection.timeout = old_timeout
        raise RuntimeError("I looped through all the com ports and didn't find "+textidn)


# Note that I can now use ``SerialInstrument`` in place of ``serial.Serial``, except that ``SerialInstrument`` accepts a string identifying the instrument, and adds and changes various functions inside the class to make them more convenient.


s = SerialInstrument(None)



#with SerialInstrument('GDS-3254') as s:
s = SerialInstrument('GDS-3254')
logger.debug("running identify using the SerialInstrument class")
logger.debug(strm("SerialInstrument instance looks like this:",s))
print s.respond('*idn?')
logger.debug("done running identify")
s.close()


# Next, we can define a class for the scope, based on `pyspecdata`


class GDS_scope (SerialInstrument):
    def __init__(self,model='3254'):
        super(self.__class__,self).__init__('GDS-'+model)
        logger.debug(strm("identify from within GDS",super(self.__class__,self).respond('*idn?')))
        logger.debug("I should have just opened the serial connection")
        return
    def waveform(self,instname='GDS-3254'):
        """Retrieve waveform and associated parameters form the scope.

        Comprises the following steps:

        * opens the port to the scope
        * acquires what is saved in memory as string
        * Divides this string at hashtag which separates settings from waveform

        Parameters
        ==========

        instname : str

            The instrument name.  Specifically, a string that's returned as
            part of the response to the ``*idn?`` command.

        Returns
        =======

        x_axis : ndarray

            The *x*-axis (time-base) of the data.

        data : ndarray

            A 1-d array containing the scope data.

        params : dict

            A dictionary of the parameters returned by the scope.
        """
        self.write(':ACQ1:MEM?')
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


# The previous cell only ***defines*** the function ``retrieve_waveform``.  Now I have to actually call (run) it!:


with GDS_scope() as g:
    data = g.waveform()


# At this point, I went through and inspected `data.other_info` (`other_info` is an attribute of `nddata` whose elements can be retrieved with `get_prop`) to see what info was left in the parameter dictionary, and if I could use and pop anything else from the dictionary.


data.other_info



print data.get_prop('Memory Length')
print type(data.get_prop('Memory Length'))
print data.get_prop('Horizontal Scale')
print type(data.get_prop('Horizontal Scale'))


# Now, we can look at the data quick and dirty


data


# We can select a portion of the data:


data['t':(0,0.3e-6)]


# Manually average a bunch of times, just because I'm curious how long it takes, and because it's an easy way of getting around the 8 bit resolution


get_ipython().run_cell_magic(u'time', u'', u'# gives the execution time -- %%timeit will run multiple and find best\nn_shots = 20\nwith GDS_scope() as g:\n    for j in range(n_shots):\n        if j == 0:\n            data = g.waveform()\n        else:\n            data += g.waveform()\n    data /= n_shots')



data['t':(0,0.3e-6)]


# the following is just so I can also run this as a script


show()

