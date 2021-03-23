from Instruments.XEPR_eth import xepr

with xepr() as x:
    result = x.set_field(3506.3)
    print("I set the field to %f"%result)
