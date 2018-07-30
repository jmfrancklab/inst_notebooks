
# coding: utf-8

# In[ ]:


from pyspecdata import *
from pyspecdata.plot_funcs.image import imagehsv
import os
import sys
import matplotlib.style
import matplotlib as mpl


mpl.rcParams['image.cmap'] = 'jet'
fl = figlist_var()
gain_factor_dcasc12 = sqrt(114008.55204672)   #gain in units of V
max_window = 30e-6
carrier_f = 14.4289e6

indirect_range = None
s = nddata_hdf5('180725_SE.h5/this_capture',
        directory = getDATADIR(exp_type='test_equip'))

s.set_units('t','s')
is_nutation = False
if 't_90' in s.dimlabels:
    s.rename('t_90','indirect')
    is_nutation = True
    logger.info('This is a nutation curve')
if 'full_cyc' in s.dimlabels:
    s.rename('full_cyc','indirect')
if 'average' in s.dimlabels:
    s.rename('average','indirect')

s /= gain_factor_dcasc12 # get into units of input-referred Volt
s_raw = s.C.reorder('t',first=False)

s.ft('t',shift=True)
#s = s['t':(0,None)]
s.setaxis('t',lambda f: f-carrier_f)
s.ift('t')

single_90 = False 
confirm_triggers = False 
fl.next('raw')
fl.plot(s['indirect',0]['ch',1]['ph1',0]['ph2',0])
xlim(6,15)
#fl.show()

def average_time(d):
    pulse_slice = d['ch',1].real
    normalization = (pulse_slice**2).integrate('t')
    return (pulse_slice**2 * pulse_slice.fromaxis('t')).integrate('t')/normalization
avg_t = average_time(s_raw['t':(6e-6,25e-6)]).data.mean()
pulse_slice = s_raw['t':(avg_t-max_window/2,avg_t+max_window/2)]

fl.image(pulse_slice)
#fl.show()

avg_t = average_time(pulse_slice)
print avg_t
# this creates an nddata of the time averages for each 90 pulse
logger.debug(strm('dimensions of average_time:',ndshape(avg_t)))
# shift the time axis down by the average time, so that 90 is centered around t=0
s_raw.setaxis('t', lambda t: t-avg_t.data.mean())
fl.next('check that this centers 90 around 0 on time axis')
fl.image(s_raw)
xlim(-10,10)
#fl.show()

avg_t = average_time(s_raw['t':(-max_window/2,max_window/2)])
s_raw.ft('t',shift=True)
phase_factor = s_raw.fromaxis('t',lambda x: 1j*2*pi*x)
phase_factor *= avg_t
s_raw *= exp(phase_factor)
s_raw.ift('t')

avg_t = average_time(s_raw['t':(-max_window/2,max_window/2)])
s_raw.setaxis('t', lambda t: t-avg_t.data.mean())
analytic = s_raw.C.ft('t')['t':(13e6,16e6)]
analytic.setaxis('t',lambda f: f-carrier_f)
analytic.set_units('indirect','s')
phase_factor = analytic.fromaxis('t',lambda x: 1j*2*pi*x)
phase_factor *= avg_t
analytic *= exp(phase_factor)
analytic.ift('t')

raw_corr = s_raw.C.ft('t')
phase_factor = raw_corr.fromaxis('t',lambda x: 1j*2*pi*x)
phase_factor *= avg_t
raw_corr *= exp(phase_factor)
raw_corr.ift('t',pad=30*1024)
measured_phase = analytic['t':(-max_window/2,max_window/2)].mean('t',return_error=False)
measured_phase /= abs(measured_phase)
expected_phase = nddata(exp(r_[0,1,2,3]*pi/2*1j),[4],['ph1'])
analytic *= expected_phase/measured_phase
print ndshape(analytic)
analytic.reorder(['indirect','t'],first=False)
print ndshape(analytic)

fl.next('analytic signal, ref ch')
fl.image(analytic)
fl.next('coherence domain, ref ch')
coherence_domain = analytic.C.ift(['ph1','ph2'])
fl.image(coherence_domain['ch',1])
#fl.show()

s_analytic = analytic['ch',0].C
s_analytic.ift(['ph1','ph2'])
fl.next('coherence, sig ch, t domain')
fl.image(s_analytic)
print ndshape(s_analytic)
#fl.show()

s_analytic.mean('indirect',return_error=False)
s_analytic.set_units('V')
signal = s_analytic['ph1',1]['ph2',0]

print ndshape(signal)
plot(signal)

signal.name('Amplitude')
print ndshape(signal)

fl.next(r'$\Delta_{c_{1}}$ = -1, $\Delta_{c_{2}}$ = 0,$\pm 2$')
fl.plot(signal.real,alpha=0.4,label='real')
fl.plot(signal.imag,alpha=0.4,label='imag')

#fl.show()


# In[ ]:


q = open('spin_echo.txt', 'wb')

for i in xrange(len(signal.getaxis('t'))):
    data = signal.data[i]
    time = signal.getaxis('t')[i]
    q.write("%f %f\n" % (data, time))

q.close()

