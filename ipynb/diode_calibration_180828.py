
# coding: utf-8

# 

get_ipython().magic(u'load_ext pyspecdata.ipy')
from IPython.display import Markdown as md
md('test *yes*')
import pandas as pd


# 

d = pd.read_excel('bridge12_diode_calib.xlsx')
d = d.loc[2:] #truncate the stuff that's too low in power


# 

d = nddata(d['"Rx" reading'].values,['dBm']).labels({'dBm':double(d['Expected Real Value'].values)})
d


# 

# ## since I want to use inverse interpolation, check that it looks OK

plot(d)
yvals = linspace(3,390,100)
xvals = d.C.invinterp('dBm',yvals)
plot(xvals)


# 

readings = r_[13.4,277.9,320.9]
for reading in readings:
    dBm_val = d.C.invinterp('dBm',reading).getaxis('dBm').item().real
    display(md('A reading of %f mV corresponds to %f dBm'%(reading,dBm_val)))




