from Instruments import *
from pyspecdata import *

# set the sine wave

with AFG() as a:
    a.sin(f=15e6, ch=1)

# grab it on the scope

with GDS_scope() as g:
    g.autoset()
    data = g.waveform(ch=2)
plot(data.human_units())

show()
