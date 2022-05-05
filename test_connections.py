from pylab import *
from Instruments import HP6623A, prologix_connection, gigatronics
from Instruments.bridge12 import convert_to_power, convert_to_mv
from serial import Serial

#with prologix_connection() as p:
#        with gigatronics(prologix_instance=p, address=7) as g:
#            print("*** *** ***")
#            g.read_power()
#            print("*** *** ***")
#            quit()

with prologix_connection() as p:
        with HP6623A(prologix_instance=p, address=3) as HP:
            print("*** *** ***")
            print("*** *** ***")
            #HP.set_output(channel=1,voltage=None,current=0.2)
            HP.set_output()
            HP.get_output()
            quit()

