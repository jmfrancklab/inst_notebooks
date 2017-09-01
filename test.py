from Instruments import *
from pyspecdata import *

# set the sine wave

with AFG() as a:
    a.reset()
    x = r_[-6:6:200j]
    a.digital_ndarray(exp(-x**2))

# grab it on the scope

with GDS_scope() as g:
    g.autoset()
    data = g.waveform(ch=2)
plot(data.human_units())

show()
