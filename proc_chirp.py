from pyspecdata import *
#import logging
#init_logging(level=logging.DEBUG)
mixdown = 15e6
capture_num = 1
f_axis = linspace(100e3,500e3,100) # must match sweep_frequencies_sqw
with figlist_var(filename='chirp.pdf') as fl:
    expno=0
    for date, id_string in [
#            ('180410','bandpass_90_1L'),
#            ('180410','bandpass_90_2L'),
#            ('180410','bandpass_90_3L'),
            ('180502','bandpass_2L'),
            ('180502','bandpass_3L'),
            ('180502','bandpass_3L_220pf'),
            ('180502','duplexer_bp_2'),
            ('180502','duplexer_bp_3'),
            ('180503','duplexer_1N5818'),
            ('180503','duplexer_2pi'),
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
        if expno == 1:
            label = '3L'       
        if expno == 2:
            label = '3L,220pF'       
        if expno == 3:
            label = 'Duplexer (3L bp)'       
        if expno == 4:
            label = 'Duplexer (2L bp)'       
        if expno == 5:
            label = 'Duplexer (1N5818)'       
        if expno == 6:
            label = 'Duplexer (2pi)'       
        fl.next('chirp')
        fl.plot(d['ch',0],'+',alpha=0.2,label='%s'%label)
        fl.next('Bandpass S12: Analytic signal')
#        d.setaxis('t', lambda x: x-d.getaxis('t')[0])
        fl.plot(abs(d['ch',0]/d['ch',1]),'-', alpha=0.38, label='%s'%label)
        fl.next('Bandpass S12: Phase')
#        d.setaxis('t', lambda x: x-d.getaxis('t')[0])
        fl.plot((d['ch',0]/d['ch',1]).angle/pi, '.', alpha=0.2, label='%s'%label)
        expno += 1 
