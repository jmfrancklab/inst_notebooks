from Instruments import AFG
import time
from pyspecdata import *

with AFG() as a:
    a.reset()
    print a.CH1.sweep
    a.CH1.sweep = True
    print a.CH1.sweep
    a.set_sweep(start=1e3,stop=20e6,time=1e-3)
    a.CH1.output = True
