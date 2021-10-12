from Instruments.XEPR_eth import xepr
import sys

with xepr() as x:
    field = float(sys.argv[1])
    print("About to set field to %f"%field)
    assert field < 3700, "are you crazy??? field is too high!"
    assert field > 3300, "are you crazy?? field is too low!"
    field = x.set_field(field)
    print("field set to ",field)
