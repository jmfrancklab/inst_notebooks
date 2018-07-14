from pyspecdata import *
#import logging
#init_logging(level=logging.DEBUG)
#{{{ boolean statement for processing data before modification to generate chirp
#   that sets voltage of ref (CH1 of scope) and DUT (CH2 of scope) to same value
corrected_volt = True
#}}}
with figlist_var(filename='chirp.pdf') as fl:
#    fl.next('$S_{11}$ : phase', legend=True)
    expno=0
    for date, id_string,corrected_volt in [
            #('180706','chirp_probe_magnet',True),   # B_0 = 3399.55 G, no sample
            #('180706','chirp_probes_magnet',True),   # B_0 = 3399.55 G, sample   
            #('180706','chirp_probes_magnet_2',True),   # B_0 = 3410.55 G, sample   
            #('180708','chirp_probes_magnet',True),   # B_0 = 3410.55 G, sample   
            #('180708','chirp_probes_magnet_repeat',True),   # B_0 = 3410.55 G, sample   
            #('180708','chirp_probes_magnet_2',True),   # B_0 = 3410.55 G, sample   
            #('180712','test_chirp',True),   # B_0 = 3394.80 G, sample   
            #('180712','test_chirp_2',True),   # B_0 = 3394.80 G, sample   
            ('180713','test_chirp',True),   # no magnetic field   
            ('180713','test_chirp_2',True),   # no magnetic field   
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
#        fl.next('plot ch 0 %s'%id_string)
#        fl.plot(d['ch',0],alpha=0.15,label='raw data')
#        fl.next('plot ch 1 %s'%id_string)
#        fl.plot(d['ch',1],alpha=0.15,label='raw data')
        d.ft('t',shift=True)
        d = d['t':(0,100e6)] # throw out negative frequencies and low-pass
        d.reorder('ch', first=False) # move ch dimension last
        d.ift('t')
        ranges = abs(d)['ch',0].contiguous(lambda x: x > 0.09*x.data.max())
        ranges = ranges[0,:].tolist()
        print 'Slicing chirp for',id_string,'from',ranges[0]*1e6,'to',ranges[1]*1e6,'us...'
        d = d['t':tuple(ranges)]
#        fl.next('plot ch 0 %s'%id_string)
#        fl.plot(d['ch',0],alpha=0.3,label='processed')
#        fl.next('plot ch 1 %s'%id_string)
#        fl.plot(d['ch',1],alpha=0.3,label='processed')
        label=id_string
        d.setaxis('t', lambda x: x-d.getaxis('t')[0]) #
        d.setaxis('t', lambda x: 25e6-x*25e6/4096e-8)
        d.rename('t','f').set_units('f','Hz')
        fl.next('$S_{11}$ : analytic amplitude')
        ratio = d['ch',1]/d['ch',0]
        plot_params = dict(alpha=0.4,
                markersize=2,
                label='%s'%label
                )
        if 'control' in label:
            plot_params['color'] = 'k'
        if corrected_volt:
            fl.plot(abs(ratio),'.', **plot_params) 
        if not corrected_volt:
            fl.plot(2*abs(ratio),'.', **plot_params)
        fl.next('$S_{11}$ : phase')
        fl.plot((ratio).angle/pi, '.', **plot_params)
        expno += 1 
    fl.next('$S_{11}$ : phase')
    gridandtick(gca())
    fl.next('$S_{11}$ : analytic amplitude')
    gridandtick(gca())
