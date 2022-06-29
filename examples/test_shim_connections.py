"""
HP Shim Power Supply
====================

Just go through and set the voltage on a bunch of shim coils, and verify
that the power supply believes that the currents have been changed."""
from pylab import *
from Instruments import HP6623A, prologix_connection, gigatronics
from Instruments.bridge12 import convert_to_power, convert_to_mv
from serial import Serial

voltage_array = r_[0.:1.:0.025]

with prologix_connection() as p:
        with HP6623A(prologix_instance=p, address=3) as HP:
            print("*** *** ***")
            for index,this_val in enumerate(voltage_array):
                print(index)
                print(this_val)
                HP.set_voltage(2,this_val)
                print("Current on channel 2 is",HP.get_current(2))
                input("Check?")
                print("Current on channel 2 is",HP.get_current(2))
                print("** *** ***")
            print("Voltage on channel 2 is",HP.get_voltage(2))
            print("About to turn on output..")
            HP.output(2,True)
            HP.check_output(2)
            print("About to turn off output..")
            HP.output(2,False)
            HP.check_output(2)
            print("*** *** ***")
