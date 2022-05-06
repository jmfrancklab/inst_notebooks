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
            #HP.set_current(2,0.4)
            print(HP.output(1,0))
            print(HP.output(2,0))
            print(HP.output(3,0))
            print(HP.check_output(1))
            print(HP.check_output(2))
            print(HP.check_output(3))
            print(HP.output(1,1))
            print(HP.output(2,1))
            print(HP.output(3,1))
            print(HP.check_output(1))
            print(HP.check_output(2))
            print(HP.check_output(3))
            print("Current on channel 1 is",HP.get_current(2))
            #HP.set_voltage(2,0.2)
            #print("Current on channel 1 is",HP.get_voltage(2))
            print("*** *** ***")
            quit()

