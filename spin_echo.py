from Instruments import *
from pyspecdata import *
import time
from timeit import default_timer as timer
from serial.tools.list_ports import comports
import serial
import pprint
from scipy import signal

fl = figlist_var()

print "These are the instruments available:"
SerialInstrument(None)
print "done printing available instruments"

with SerialInstrument('GDS-3254') as s:
    print s.respond('*idn?')
    
with SerialInstrument('AFG-2225') as s:
    print s.respond('*idn?')

#{{{ calls scope and acquires signal
def acquire(date,id_string,captures):
#{{{ documentation
    r'''Captures displayed waveform on scope as an hdf5 file
    saved with filename 'date_id_string'; data is stored in
    an accumulated node, different from earlier versions.
    Parameters
    ==========
    date : string 

        Date of data collection

    id_string : string 

        Name associated with data collection

    captures : numpy.ndarray

        An array, beginning with 1, that specifies number of times
        scope should capture signal - e.g., captures = linspace(1,100,100) 
        will capture signal 100 times, beginning with capture1 and ending
        with capture100
    
    '''
    #}}}
    cap_len = len(captures)
    datalist = []
    print "about to load GDS"
    with GDS_scope() as g:
    #    g.timscal(5e-6)  #setting time scale to 500 ns/div
    #    g.voltscal(1,500e-3) #setting volt scale on channel 1 to 500 mV/div
        print "loaded GDS"
        for x in xrange(1,cap_len+1):
            print "entering capture",x
            ch1_waveform = g.waveform(ch=1)
#            ch2_waveform = g.waveform(ch=2)
            data = concat([ch1_waveform],'ch').reorder('t')
            if x == 1:
                channels = ((ndshape(data)) + ('capture',cap_len)).alloc()
                channels.setaxis('t',data.getaxis('t')).set_units('t','s')
                channels.setaxis('ch',data.getaxis('ch'))
            channels['capture',x-1] = data
    # {{{ in case it pulled from an inactive channel
    if not isfinite(data.getaxis('t')[0]):
        j = 0
        while not isfinite(data.getaxis('t')[0]):
            data.setaxis('t',datalist[j].getaxis('t'))
            j+=1
            if j == len(datalist):
                raise ValueError("None of the time axes returned by the scope are finite, which probably means no traces are active??")
    # }}}
    s = channels
    s.labels('capture',captures)
    s.name('accumulated_'+date)
    s.hdf5_write(date+'_'+id_string+'.h5')
    print "name of data",s.name()
    print "units should be",s.get_units('t')
    print "shape of data",ndshape(s)
    return
#}}}
#{{{ spin echo function
def spin_echo(freq = 14.5e6, p90 = 2.8e-6, d1 = 50e-6, ch1_only=True):
#{{{ documentation
    r'''generates spin echo (90 - delay - 180) pulse sequence, defined by
    the frequency, 90 time, and delay time, and outputs on scope.
    fr
    
    Parameters
    ==========
    freq : float

        Frequency of RF pulse

    p90 : float

        90 time of RF pulse

    d1 : float

        Delay time between 90 and 180 pulse; set to deadtime

    ch1_only : boolean

        When True, sequence is output on CH1 only.
        When False, sequence is output on both CH1 and CH2.
    
    '''
    #}}}
    start_seq = timer()
    #{{{ generating sequence array; want to do this once 
    rate = freq*4
    t_seq = p90 + d1 + 2*p90
    pts_seq = int(t_seq*rate/4 + 0.5)*4
    
    t_sp = t_seq/pts_seq
    pts_p90 = int(p90/t_sp/4 + 0.5)*4
    pts_d1 = int(d1/t_sp/4 + 0.5)*4
    pts_p180 = int(2*p90/t_sp/4 + 0.5)*4

    pts_seq = int((pts_p90 + pts_d1 + pts_p180)/4 + 0.5)*4

    freq = 14.5e6
    p90 = 2.8e-6
    d1 = 50.e-6
    
    rate = freq*4
    t_seq = p90 + d1 + 2*p90
    pts_seq = int(t_seq*rate/4 + 0.5)*4
    
    t_sp = t_seq/pts_seq
    pts_p90 = int(p90/t_sp/4 + 0.5)*4
    pts_d1 = int(d1/t_sp/4 + 0.5)*4
    pts_p180 = int(2*p90/t_sp/4 + 0.5)*4

    pts_seq = int((pts_p90 + pts_d1 + pts_p180)/4 + 0.5)*4
    
    assert pts_seq < 4097
    
    y = zeros(pts_seq)
    y[0::4] = 0
    y[1::4] = 1
    y[2::4] = 0
    y[3::4] = -1
    y[-1] = 0
    y[pts_p90:(pts_seq-pts_p180)] = 0
    end_seq = timer()
    #}}}
    with AFG() as a:
        a.reset()
        #{{{ output of array, takes 4 seconds
        ch_list = [0]
        for this_ch in ch_list:
            a[this_ch].ampl = 10.
            a[this_ch].digital_ndarray(y, rate=rate)
            end_loadseq = timer()
            start_out = timer()
            a[this_ch].output = True
            a[this_ch].burst = True
            end_out = timer()
            d_interseq = 5*200e-3
            a.set_burst(per=d_interseq) #per=T2 of sample
            #}}}
    return start_seq,end_seq,end_loadseq,start_out,end_out
#}}}

date = '180628'
id_string = 'spin_echo_exp2'
captures = linspace(1,10000,10000)

t1,t2,t3,t4,t5 = spin_echo()
start_acq = timer()
acquire(date,id_string,captures)
end_acq = timer()

print "Time to generate sequence array:",t2-t1,"s"
print "Time to generate + load sequence into AFG:",t3-t1,"s"
print "Time to output sequence:",t5-t4,"s"
print "Time for captures:",end_acq - start_acq,"s"
