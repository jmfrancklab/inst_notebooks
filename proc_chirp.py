from pyspecdata import *
#import logging
#init_logging(level=logging.DEBUG)
mixdown = 15e6
capture_num = 1
f_axis = linspace(100e3,500e3,100) # must match sweep_frequencies_sqw
with figlist_var(filename='chirp.pdf') as fl:
    expno=0
    for date, id_string in [
#            ('180513','test_M8653x3_1'),
#            ('180513','test_M8653x3_2'),
#            ('180513','test_M8653x3_3'),
#            ('180513','test_M8653x3_4'),
#            ('180514','test_M8653x3_1'),
            ('180514','test_M8653x3_2'),
            ('180514','test_M8653x3_3'),
            ('180514','test_M8653x3_4'),
#            ('180514','test_M8653x3_5'),
#            ('180514','test_M8653x3_6'),
            ('180514','test_M8653x3_7'),
            ('180514','test_M8653x3_8'),
            ]:

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
                # capture2 only present when capture1 was bad
                d = nddata_hdf5(date+'_'+id_string+'.h5/capture2',
                            directory=getDATADIR(exp_type='test_equip'))
            except:
                d = nddata_hdf5(date+'_'+id_string+'.h5/capture1',
                            directory=getDATADIR(exp_type='test_equip'))
        d.set_units('t','s')
        d -= d['t':(0,3.5e-6)].runcopy(mean,'t')
        d.ft('t',shift=True)
        d = d['t':(0,100e6)] # throw out negative frequencies and low-pass
        d.reorder('ch', first=False) # move ch last
        d.ift('t')
        if expno == 0:
            fl.next('analytic signal, abs')
            fl.plot(abs(d))
        ranges = abs(d)['ch',1].contiguous(lambda x: x > 0.2*x.data.max())
        ranges = tuple(ranges[0,:].tolist())
        d = d['t':ranges]
        d.setaxis('t', lambda x: x-d.getaxis('t')[0])
        d.setaxis('t', lambda x: 25e6-x*25e6/4096e-8).set_units('t','Hz')
        if expno == 0:
            fl.next('analytic signal, phase')
            fl.plot(d.angle)
        d.ft
        fl.next('FT(chirp)')
        fl.plot(d['ch',0])

        fl.next('which ch1')
        fl.plot(d['ch',1])

        if expno == 0:
            label = '2L'
#        if expno == 1:
#            label = '2L,220pF'
#        if expno == 2:
#            label = '3L'       
#        if expno == 3:
#            label = '3L,220pF'       
#        if expno == 4:
#            label = 'Duplexer (3L bp)'       
#        if expno == 5:
#            label = 'Duplexer (2L bp)'       
        fl.next('chirp')
        fl.plot(d['ch',0],'+',alpha=0.2,label='%s'%label)
        fl.next('bandpass s12: analytic signal')
#        d.setaxis('t', lambda x: x-d.getaxis('t')[0])
        fl.plot(2*abs(d['ch',0]/d['ch',1]),'-', alpha=0.38, label='%s'%label)
        fl.next('bandpass s12: phase')
#        d.setaxis('t', lambda x: x-d.getaxis('t')[0])
        fl.plot((d['ch',0]/d['ch',1]).angle/pi, '.', alpha=0.2, label='%s'%label)
        expno += 1 
