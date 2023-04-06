from Instruments import HP8672A, prologix_connection, gigatronics, power_control
from Instruments.bridge12 import convert_to_power, convert_to_mv
with prologix_connection() as prx:
    with gigatronics(prologix_instance=prx,address=7) as g:
        print("I see a power of",g.read_power())
        input("start the server")
        with power_control() as p:
            this_f = p.dip_lock(9.81,9.83)
            p.set_power(10)
            print("Now the power is", g.read_power())
