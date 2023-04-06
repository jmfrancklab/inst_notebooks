from Instruments import HP8672A, prologix_connection, gigatronics
from Instruments.bridge12 import convert_to_power, convert_to_mv
with prologix_connection() as p:
    with gigatronics(prologix_instance=p) as g:
        print("I see a power of",g.read_power())
