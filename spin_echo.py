from Instruments import *
from pyspecdata import *
import time
from timeit import default_timer as timer
from serial.tools.list_ports import comports
import serial
import pprint
from scipy import signal

fl = figlist_var()
#{{{ Initialize instruments
print "These are the instruments available:"
SerialInstrument(None)
print "done printing available instruments"

with SerialInstrument('GDS-3254') as s:
    print s.respond('*idn?')
    
with SerialInstrument('AFG-2225') as s:
    print s.respond('*idn?')
    #}}}
#{{{ acquire function, calls only scope and captures; for field sweep
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
    #cap_time = zeros(cap_len)
    print "about to load GDS"
    with GDS_scope() as g:
    #    g.timscal(5e-6)  #setting time scale to 500 ns/div
    #    g.voltscal(1,500e-3) #setting volt scale on channel 1 to 500 mV/div
        print "loaded GDS"
        for x in xrange(1,cap_len+1):
            print "entering capture",x
            #cap_time[x-1] = timer() - start_acq
            ch1_waveform = g.waveform(ch=1)
            ch2_waveform = g.waveform(ch=2)
            data = concat([ch1_waveform,ch2_waveform],'ch').reorder('t')
            if x == 1:
                channels = ((ndshape(data)) + ('capture',cap_len)).alloc()
                channels.setaxis('t',data.getaxis('t')).set_units('t','s')
                channels.setaxis('ch',data.getaxis('ch'))
#              channels.setaxis('cap_time',cap_time).set_units('t','s')
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
#{{{ spin echo function with phase cycling capability
def spin_echo(freq = 14.4917e6, p90 = 2.592e-6, d1 = 63.794e-6, T1 = 200e-3, max_delay = True, complex_exp = True, ph_cyc = True):
#{{{ documentation
    r'''generates spin echo (90 - delay - 180) pulse sequence, defined by
    the frequency, 90 time, and delay time, and outputs on scope.
    fr
    
    Parameters
    ==========
    freq : float

        Frequency of RF pulse; i.e., carrier frequency

    p90 : float

        90 time of RF pulse

    d1 : float

        Delay time between 90 and 180 pulse, akin to 'tau'; at minimum, should set to deadtime. 
        This delay time is only applicable if max_delay = False.

    T1 : float

        T1 of sample, determines the burst period (i.e., the amount of time between output of pulse sequence)
        For 13 mM [NiSO4], T1 = 200ms; with this as input, the burst period is set to 1 second.

    max_delay : boolean 

        Currently only set for complex_exp waveform generation.
        If set to True, then program maximizes the delay time between the 90 pulse and the 180 pulse, which is
        constrained by the sampling rate of the arbitrary waveform on the scope.
        If set to False, then delay time between the 90 pulse and the 180 pulse
        T1 of sample, determines the burst period (i.e., the amount of time between output of pulse sequence)
        For 13 mM [NiSO4], T1 = 200ms; with this as input, the burst period is set to 1 second.
    
    complex_exp : boolean 

        If set to True, then program generates arbitrary waveform via a complex exponential. This is the only waveform that supports 
        phase cycling. This is used as of July 2018.
        If set to False, then program generates arbitrary waveform by setting the values of an array via 4-step slicing. This was
        the previous waveform used for generating pulses.

    ph_cyc : boolean

        If set to True, then program will phase shift the 180 pulse and the 90 pulse separately, capturing each shift. The phase cycle cannot
        be set through commands yet. Note that with this set to True, there is no need to call acquire.
        If set to False, then program does not phase shift; to capture signal, will need to call acquire (for field sweeps). 

    '''
    #}}}
    start_seq = timer()
#{{{ calculating parameters for arbitrary waveform
    d_interseq = 5*T1       #[sec] time between sequence trigger 
    #{{{ this generates spin echo via complex exponential
    if complex_exp:
        freq_carrier = freq     #[Hz] rf pulse frequency
        points_total = 4096     #[pts] total points, property of AFG
        rate = freq_carrier*4   #[pts/sec] AFG requires for arb waveform
        time_spacing = 1/rate   #[sec/pt] time between two points
        time_total = time_spacing * points_total #[sec]
        t_90 = p90              #[sec] pulse length of 90
        t_180 = 2*t_90          #[sec] pulse length of 180
        points_90 = t_90/time_spacing #[pts] points in 90
        points_180 = t_180/time_spacing #[pts] points in 180
        if not max_delay:
            t_d1 = d1
            points_d1 = t_d1/time_spacing
        if max_delay:
            points_d1 = points_total - points_90 - points_180
            t_d1 = points_d1*time_spacing
        time_sequence = t_90 + t_d1 + t_180
        points_sequence = points_90 + points_d1 + points_180
        assert points_sequence < 4097
        #{{{ generating the arbitrary waveform
        t = r_[0:4096]
        freq_sampling = 0.25
        y = 0*t
        y = exp(1j*2*pi*t[1 : -2]*freq_sampling)
        y[int(points_90) : int(points_90+points_d1)] = 0
        y[int(points_90+points_d1+1)] = 0 # this starts the 180 as cosine to match 90
        #}}}
    #}}}
    #{{{ this generates spin echo via alternating array (previous method)
    if not complex_exp:
        rate = freq*4                                           # rate set on AFG
        t_seq = p90 + d1 + 2*p90                                # time length of entire pulse sequence
        pts_seq = int(t_seq*rate/4 + 0.5)*4                     # no. points needed for this time length at given rate
        t_sp = t_seq/pts_seq                                    # time between each point in sequence
        pts_p90 = int(p90/t_sp/4 + 0.5)*4                       # no. points needed for 90 pulse (fit to integer of 4)
        pts_d1 = int(d1/t_sp/4 + 0.5)*4                         # no. points needed for tau (90-180 delay) (int of 4)
        pts_p180 = int(2*p90/t_sp/4 + 0.5)*4                    # no. points needed for 180 pulse (int of 4)
        pts_seq = int((pts_p90 + pts_d1 + pts_p180)/4 + 0.5)*4  # no. points for entire sequence as int of 4 
        assert pts_seq < 4097                                   # no. points total must be less than 4097
        #{{{ generating the arbitrary waveform
        y = zeros(pts_seq)
        y[0::4] = 0
        y[1::4] = 1
        y[2::4] = 0
        y[3::4] = -1
        y[-1] = 0
        y[pts_p90:(pts_seq-pts_p180)] = 0
        #}}}
    #}}}
#}}}
    end_seq = timer()
    with AFG() as a:
        a.reset()
        ch_list = [0]
        for this_ch in ch_list:
            a[this_ch].ampl = 10.
            a[this_ch].digital_ndarray(y, rate=rate)
            a[this_ch].output = True
            a[this_ch].burst = True
            a.set_burst(per=d_interseq)
            #{{{ for phase cycling
            if ph_cyc:
                y_ph = y.copy()
                for ph2 in xrange(0,4,2):
                    y_ph[int(points_90+points_d1+1):-2] *= exp(1j*pi/2*ph2)
                    for ph1 in xrange(4):
                        y_ph[1:int(points_90)] *= exp(1j*pi/2*ph1)
                        a[this_ch].digital_ndarray(y_ph, rate=rate)
                        a[this_ch].burst = True
                        with GDS_scope() as g:
                            ch1_wf = g.waveform(ch=1)
                            ch2_wf = g.waveform(ch=2)
                            #{{{ this could be used to do several rounds of phase cycling
                       #     if (ph1 == 0 + ph2 == 0):
                       #         channels = ((ndshape(data)) + ('capture',cap_len)).alloc()
                       #         channels.setaxis('t',data.getaxis('t')).set_units('t','s')
                       #         channels.setaxis('ch',data.getaxis('ch'))
                       # channels['capture',x-1] = data
                        #}}}
                        data = concat([ch1_wf,ch2_wf],'ch').reorder('t')
                        data_name = str(ph1)+str(ph2)
                        data.name(data_name)
                        data.hdf5_write(date+"_"+id_string+".h5")
                        print "name of data",data.name()
                        print "units should be",data.get_units('t')
                        print "shape of data",ndshape(data)
                #}}}
    return start_seq,end_seq
#}}}

date = '180706'

id_string = 'spin_echo_exp'

t1,t2 = spin_echo()
#raw_input("Start magnetic field sweep")
#start_acq = timer()
#acquire(date,id_string,captures)
#end_acq = timer()

print "Time to generate sequence array:",t2-t1,"s"
#print "Time to generate + load sequence into AFG:",t3-t1,"s"
#print "Time to output sequence:",t5-t4,"s"
#print "Time for captures:",end_acq - start_acq,"s"
