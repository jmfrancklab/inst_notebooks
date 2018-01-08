from pyspecdata import *

mixdown = 15e6
capture_num = 1
f_axis = linspace(100e3,500e3,100) # must match sweep_frequencies_sqw
with figlist_var(filename='chirp.pdf') as fl:
    j=0
    for date, id_string in [
            ('180104','820_LCs'),
            ('180104','cable'),
            ('180104','Lw'),
            ('180104','wC'),
            ('180104','ww'),
            ('180108','LCR')
            
            ]:
        try:
            # capture2 only present when capture1 was bad
            d = nddata_hdf5(date+'_'+id_string+'.h5/capture2_'+date,
                        directory=getDATADIR(exp_type='test_equip'))
        except:
            d = nddata_hdf5(date+'_'+id_string+'.h5/capture1_'+date,
                        directory=getDATADIR(exp_type='test_equip'))
        if j == 0:
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
        if j == 0:
            fl.plot(d)
            fl.next('analytic signal, abs')
        d.ft('t',shift=True)
        d = d['t':(0,100e6)] # throw out negative frequencies and low-pass
        d.reorder('ch', first=False) # move ch last
        d.ift('t')
        collated_unmixed = d.copy()
        d *= d.fromaxis('t', lambda t: exp(-1j*2*pi*mixdown*t))
        if j == 0:
            fl.plot(abs(d))
            fl.next('analytic signal, phase')
            fl.plot(d.angle)
        fl.next('analytic signal, ratio', legend=True)
        fl.plot(abs(2*d['ch',1]/d['ch',0]), label=id_string)
        fl.next('ratio, real', legend=True)
        fl.plot((2*d['ch',1]/d['ch',0]), label=id_string)
        fl.next('ratio, imag', legend=True)
        fl.plot((2*d['ch',1]/d['ch',0]).imag, label=id_string)
        fl.next('analytic signal, phase difference', legend=True)
        fl.plot((d['ch',1]/d['ch',0]).angle/pi, '.', label=id_string)
        j += 1
