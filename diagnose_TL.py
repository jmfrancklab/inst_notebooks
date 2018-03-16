from pyspecdata import *
import winsound
#import logging
#init_logging(level=logging.DEBUG)
fl = figlist_var()

def process_series(date,id_string):
    """Process a series of pulse data.
    
    Lumping this as a function so we can do things like divide series, etc.

    Parameters
    ----------
    date: str
        date used in the filename
    id_string: str
        filename is called date_id_string
    V_AFG: array
        list of voltage settings used on the AFG

    Returns
    -------
    V_anal: nddata
        The analytic signal, filtered to select the fundamental frequency (this is manually set).
    V_harmonic: nddata
        The analytic signal, filtered to set the second harmonic (this is manually set)
    V_pp: nddata
        After using the analytic signal to determine the extent of the pulse, find the min and max.
    """
    j = 1
    if j == 1:
        print "loading signal",j
        j_str = str(j)
        d = nddata_hdf5(date+'_'+id_string+'.h5/capture'+j_str+'_'+date,
                directory=getDATADIR(exp_type='test_equip'))
        d.set_units('t','s')
        fl.next('Channel 1, 1')
        fl.plot(d['ch',0], alpha=0.5, label='label %s'%id_string)
        d.ft('t',shift=True)
        fl.next('Raw FT')
        fl.plot(d['ch',0],alpha=0.15,label='label %s'%id_string)
        d.ift('t')
        d.ft('t')
        d_fundamental = d.copy()
        d_harmonics = d.copy()
        d_fundamental = abs(d_fundamental)*abs(d_fundamental)
        d_fundamental['t':(None,-20e6)]=0
        d_fundamental['t':(20e6,None)]=0
        d_harmonics = abs(d_harmonics)*abs(d_harmonics)
        d_harmonics['t':(-20e6,20e6)]=0
        d_harmonics['t':(None,-200e6)]=0
        d_harmonics['t':(200e6,None)]=0
        print 'integrating '+id_string+' fundamental'
        fundamental_sum = d_fundamental['ch',0].integrate('t')
        print fundamental_sum
        print 'integrating '+id_string+' harmonics'
        harmonics_sum = d_harmonics['ch',0].integrate('t')
        print harmonics_sum
    print "done loading all signals for %s"%id_string
    return 

for date,id_string in [
       ('180316','duplexer_pi1'),
       ('180316','duplexer_pi2')
        ]:
    process_series(date,id_string)
fl.show()

