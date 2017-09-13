from Instruments import AFG
import time
from pyspecdata import *

with AFG() as a:
    a.reset()
    print a.CH1.sweep
    a.CH1.sweep = True
    print a.CH1.sweep
    a.set_sweep()

