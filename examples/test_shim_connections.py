"""
HP Shim Power Supply
====================

Just go through and set the voltage on a bunch of shim coils, and verify
that the power supply believes that the currents have been changed."""
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

current_array = r_[0.,0.3]
for index,this_current in enumerate(current_array):
    print(index)
quit()

with prologix_connection() as p:
        with HP6623A(prologix_instance=p, address=3) as HP:
            print("*** *** ***")
            # by setting voltage to 5, enter CC mode
            HP.set_voltage(2,5)
            # at this point, can enter desired current
            HP.set_current(2,0.3)
            input("Check?")
            print("Current on channel 2 is",HP.get_current(2))
            print("Voltage on channel 2 is",HP.get_voltage(2))
            print("About to turn on output..")
            HP.output(2,True)
            HP.check_output(2)
            print("About to turn off output..")
            HP.output(2,False)
            HP.check_output(2)
            print("*** *** ***")
