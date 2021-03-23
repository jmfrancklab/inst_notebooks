from Instruments.XEPR_eth import xepr
from Instruments.power_control import power_control

with xepr() as x:
    with power_control() as p:
        result = x.set_field(3506.3)
        print("I set the field to %f"%result)
