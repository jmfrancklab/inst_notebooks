from pyspecdata import *

mixdown = 15e6
capture_num = 1
f_axis = linspace(100e3,500e3,100) # must match sweep_frequencies_sqw
d = nddata_hdf5('171220_series_chirp.h5/capture2_171220',
            directory=getDATADIR(exp_type='test_equip'))
with figlist_var(filename='chirp_171129.pdf') as fl:
    # {{{ CDF the values of the data to see if it's really digitizing with 14 bit
    vals = d.data.flatten()
    myhist = nddata(linspace(-3,3,1000),'val')
    fl.next('PDF of values (check digitization)')
    # {{{ calculate the CDF
    for j,testval in enumerate(myhist.getaxis('val')):
        myhist['val',j] = sum(vals < testval)
    # }}}
    myhist.diff('val') # to get the PDF
    num_values = len(myhist[lambda x: x>1e-8].data)
    print "number of values along dynamic range",num_values,"log_2 ->",log(num_values)/log(2),"bits"
    fl.plot(myhist, label='Diversity of data matches %0.3f bits'%(log(num_values)/log(2)))
    # }}}
    fl.next('raw')
    d -= d['t':(0,3.5e-6)].runcopy(mean,'t')
    fl.plot(d)
    fl.next('analytic signal, abs')
    d.ft('t',shift=True)
    d = d['t':(0,100e6)] # throw out negative frequencies and low-pass
    d.reorder('ch', first=False) # move ch last
    d.ift('t')
    collated_unmixed = d.copy()
    d *= d.fromaxis('t', lambda t: exp(-1j*2*pi*mixdown*t))
    fl.plot(abs(d))
    fl.next('analytic signal, phase')
    fl.plot(d.angle)
    fl.next('analytic signal, compared')
    fl.plot(abs(d['ch',1]/d['ch',0]), label='ratio')
    fl.plot((d['ch',1]/d['ch',0]).angle/2./pi, label='phase diff.')
