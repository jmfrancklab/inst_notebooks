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
            #('180920','test_probe',True),      # varC+100 pF tune
            #('180920','test_probe_2',True),
            #('180920','test_probe_3',True),
            #('180920','test_probe_4',True),
            #('180920','test_probe_5',True),
            #('180920','test_probe_6',True),    
            #('180920','test_probe_7',True),
            #('180920','test_probe_1_2',True), # varC+56 pF tune
            #('180920','test_probe_2_1',True), # varC+100 pF tune, varC+13 pF match
            #('180920','test_probe_3_1',True), # varC+100 pF tune (verifying soldering etc)
            #('180920','test_probe_3_2',True),
            #('180920','test_probe_3_3',True),
            #('180920','test_probe_3_4',True),
            #('180920','test_probe_3_5',True),
            #('180920','test_probe_4_1',True), # varC+113 pF tune
            #('180920','test_probe_4_2',True),
            #('180920','test_probe_4_3',True),
            #('180920','test_probe_4_4',True),
            #('180920','test_probe_4_5',True),
            #('180920','test_probe_4_6',True),
            #('180920','test_probe_4_7',True),
            #('180920','test_probe_4_8',True),
            #('180920','test_probe_4_9',True),
            #('180925','sprobe',True),
            #('180926','sprobe',True),
            #('180926','sprobe_2',True),
            #('180926','sprobe_3',True),
            #('180926','sprobe_4',True),
            #('180926','sprobe_5',True),
            #('180926','sprobe_6',True),
            ('180926','sprobe_7',True),
            #('180927','sprobe',True),
            #('180927','sprobe_2',True),
            #('180927','sprobe_3',True),
            #('180927','sprobe_4',True),
            #('180927','sprobe_5',True),
            #('180927','sprobe_6',True),
            #('180927','sprobe_7_',True),
            ('180927','sprobe_8',True),
            ('180927','sprobe_9',True),
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
        if 'pulse' in id_string:
            pulse_90 = True
        else :
            pulse_90 = False
        d.set_units('t','s')
        d.name('Amplitude $/$ $V$')
        #fl.next('plot ch 0 %s'%id_string)
        #fl.plot(d['ch',0],alpha=0.6,label='raw data')
        #fl.next('plot ch 1 %s'%id_string)
        #fl.plot(d['ch',1],alpha=0.6,label='raw data')
        d.ft('t',shift=True)
        d = d['t':(0,100e6)] # throw out negative frequencies and low-pass
        d.reorder('ch', first=False) # move ch dimension last
        d.ift('t')
        d *= 2
        if not pulse_90:
            ranges = abs(d)['ch',0].contiguous(lambda x: x > 0.09*x.data.max())
        if pulse_90:
            ranges = abs(d)['ch',0].contiguous(lambda x: x > 0.03*x.data.max())
        ranges = ranges[0,:].tolist()
        print 'Slicing chirp for',id_string,'from',ranges[0]*1e6,'to',ranges[1]*1e6,'us...'
        d = d['t':tuple(ranges)]
        #fl.next('plot ch 0 %s'%id_string)
        #fl.plot(d['ch',0],':',alpha=0.9,label='processed')
        ##xlim(8,18)
        #fl.next('plot ch 1 %s'%id_string)
        #fl.plot(d['ch',1],':',alpha=0.9,label='processed')
        ##xlim(8,18)
        label=id_string
        d.setaxis('t', lambda x: x-d.getaxis('t')[0])
        if not pulse_90:
            d.setaxis('t', lambda x: 25e6-x*25e6/4096e-8)
            d.rename('t','f').set_units('f','Hz')
        fl.next('$S_{11}$ : analytic amplitude')
        ratio = d['ch',1]/d['ch',0]
        ratio.name('Reflection')
        plot_params = dict(alpha=0.8,
                markersize=2,
                label='%s'%label
                )
        #if 'control' in label:
        #    plot_params['color'] = 'k'
        if corrected_volt:
            fl.plot(abs(ratio),'-', **plot_params) 
        if not corrected_volt:
            fl.plot(2*abs(ratio),'.', **plot_params)
        axhline(0.47, color='gray', alpha=0.5)
        fl.next('$S_{11}$ : phase')
        fl.plot((ratio).angle/pi, '.', **plot_params)
        expno += 1 
    fl.next('$S_{11}$ : phase')
    gridandtick(gca())
    #xlim(10,20)
    #ylim(-1.0,1.0)
    axvline(14.4289,linestyle=':', color='black')
    fl.next('$S_{11}$ : analytic amplitude')
    gridandtick(gca())
    #xlim(10,20)
    #ylim(0,1)
    axvline(14.4289,linestyle=':', color='black')
