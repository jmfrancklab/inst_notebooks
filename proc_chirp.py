from pyspecdata import *
#import logging
#init_logging(level=logging.DEBUG)
mixdown = 15e6
capture_num = 1
f_axis = linspace(100e3,500e3,100) # must match sweep_frequencies_sqw
with figlist_var(filename='chirp.pdf') as fl:
    expno=0
    for date, id_string in [
            ('180606','chirp_probe_old_1'),
            ('180606','chirp_probe_old_2'),
            ('180606','chirp_probe_old_3'),
            ('180606','chirp_probe_old_4'),
            ('180606','chirp_probe_new_1'),
            ('180606','chirp_probe_new_2'),
            ('180606','chirp_probe_new_3'),
            ('180606','chirp_probe_new_4'),
            ('180606','chirp_probe_new_5'),
            ('180606','chirp_probe_new_6'),
            ('180606','chirp_probe_new_7'),
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
        ranges = abs(d)['ch',0].contiguous(lambda x: x > 0.09*x.data.max())
        ranges = tuple(ranges[0,:].tolist())
        d = d['t':ranges]
        d.setaxis('t', lambda x: x-d.getaxis('t')[0])
        d.setaxis('t', lambda x: 25e6-x*25e6/4096e-8).set_units('t','Hz')
        label=id_string
        fl.next('channel 1')
        fl.plot(d['ch',0],'+',alpha=0.2,label='%s'%label)
        fl.next('channel 2')
        fl.plot(d['ch',1],'+',alpha=0.2,label='%s'%label)
        fl.next('s11: analytic')
#        d.setaxis('t', lambda x: x-d.getaxis('t')[0])
        fl.plot(2*abs(d['ch',1]/d['ch',0]),'-', alpha=0.38, label='%s'%label)
        fl.next('s11: phase')
#        d.setaxis('t', lambda x: x-d.getaxis('t')[0])
        fl.plot((d['ch',1]/d['ch',0]).angle/pi, '.', alpha=0.2, label='%s'%label)
        expno += 1 
