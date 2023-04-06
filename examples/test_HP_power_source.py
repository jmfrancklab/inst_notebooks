"""
h power source to replace B12 synthesizer
==========================================

Test that we can turn the power source on and chagne the power/frequency
"""
from Instruments import HP8672A, prologix_connection, gigatronics
from Instruments.bridge12 import convert_to_power, convert_to_mv
from serial import Serial
desired_atten_reading = -10 # this should be a negative number!
output_power = desired_atten_reading + 20
with prologix_connection() as p:
    with HP8672A(prologix_instance=p,address=19) as h:
        h.set_frequency(9.820701e9)#try setting MHz first
        h.set_power(output_power-37.0)


