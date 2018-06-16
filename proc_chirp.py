from pyspecdata import *
#import logging
#init_logging(level=logging.DEBUG)
#{{{ boolean statement for processing data before modification to generate chirp
#   that sets voltage of ref (CH1 of scope) and DUT (CH2 of scope) to same value
corrected_volt = True
#}}}
with figlist_var(filename='chirp.pdf') as fl:
    expno=0
    for date, id_string,corrected_volt in [
#            ('180616','chirp_test',True),
            ('180615','chirp_TX_L',False),
            ]:
#{{{ finding file
        try:
            try:
                # capture2 only present when capture1 was bad
                d = nddata_hdf5(date+'_'+id_string+'.h5/capture2_'+date,
                            directory=getDATADIR(exp_type='test_equip'))
            except:
                d = nddata_hdf5(date+'_'+id_string+'.h5/capture1_'+date,
                            directory=getDATADIR(exp_type='test_equip'))
        except:
            try:
                # for captures of different file naming format
                d = nddata_hdf5(date+'_'+id_string+'.h5/capture2',
                            directory=getDATADIR(exp_type='test_equip'))
            except:
                d = nddata_hdf5(date+'_'+id_string+'.h5/capture1',
                            directory=getDATADIR(exp_type='test_equip'))
                #}}}
        d.set_units('t','s')
        fl.next('plot ch 0')
        fl.plot(d['ch',0],alpha=0.15,label='raw data')
        fl.next('plot ch 1')
        fl.plot(d['ch',1],alpha=0.15,label='raw data')
        d.ft('t',shift=True)
        d = d['t':(0,100e6)] # throw out negative frequencies and low-pass
        d.reorder('ch', first=False) # move ch dimension last
        d.ift('t')
        ranges = abs(d)['ch',0].contiguous(lambda x: x > 0.09*x.data.max())
        ranges = ranges[0,:].tolist()
        print 'Slicing chirp from',ranges[0]*1e6,'to',ranges[1]*1e6,'us...'
        d = d['t':tuple(ranges)]
        fl.next('plot ch 0')
        fl.plot(d['ch',0],alpha=0.3,label='processed')
        fl.next('plot ch 1')
        fl.plot(d['ch',1],alpha=0.3,label='processed')
        label=id_string
        d.setaxis('t', lambda x: x-d.getaxis('t')[0]) #
        d.setaxis('t', lambda x: 25e6-x*25e6/4096e-8)
        d.rename('t','f').set_units('f','Hz')
        fl.next('$S_{11}$ : analytic')
        if corrected_volt:
            fl.plot(abs(d['ch',1]/d['ch',0]),'-', alpha=0.7, label='%s'%label)
        if not corrected_volt:
            fl.plot(2*abs(d['ch',1]/d['ch',0]),'-', alpha=0.7, label='%s'%label)
        fl.next('$S_{11}$ : phase')
        fl.plot((d['ch',1]/d['ch',0]).angle/pi, '.', alpha=0.2, label='%s'%label)
        expno += 1 
