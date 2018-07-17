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
def spin_echo(cycle_counter, freq = 14.4289e6, p90 = 2.551e-6, d1 = 63.794e-6, T1 = 200e-3, max_delay = True, complex_exp = True, ph_cyc = True):
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
        y = exp(1j*2*pi*t[1 : -1]*freq_sampling)
        y[int(points_90) : int(points_90+points_d1)] = 0
        y[0] = 0
        y[-1] = 0
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
    with AFG() as a:
        a.reset()
        ch_list = [0]
        for this_ch in ch_list:
            a[this_ch].ampl = 20.e-3
            a[this_ch].digital_ndarray(y, rate=rate)
            a[this_ch].output = True
            a[this_ch].burst = True
            a.set_burst(per=d_interseq)
            a[this_ch].ampl = 10.
            #{{{ for phase cycling
            if ph_cyc:
                num_ph1_steps = 4 
                num_ph2_steps = 2
                raw_input('Begin field sweep')
                start_ph = timer()
                timer_index = 0
                for x in xrange(cycle_counter):
                    for ph2 in xrange(0,4,num_ph2_steps):
                        for ph1 in xrange(num_ph1_steps):
                            y_ph = y.copy()
                            y_ph[1:int(points_90)] *= exp(1j*ph1*pi/2)
                            y_ph[int(points_90+points_d1):-1] *= exp(1j*ph2*pi/2)
                            a[this_ch].ampl = 20e-3
                            a[this_ch].digital_ndarray(y_ph.real, rate=rate)
                            a[this_ch].burst = True
                            a[this_ch].ampl = 10
                            with GDS_scope() as g:
                                g.acquire_mode('average',2)
                                time.sleep(5*d_interseq)
                                print "Acquiring..."
                                ch1_wf = g.waveform(ch=1)
                                ch2_wf = g.waveform(ch=2)
                                time_acq = timer()
                                this_time = time_acq - start_ph
                                g.acquire_mode('sample')
                            #{{{ set up the nddata at the very beginning of the phase cycle
                            if (ph1 == 0 and ph2 == 0 and x == 0):
                                # initialize 'timer' axis to record time of each capture
                                timer_axis = zeros(cycle_counter*num_ph1_steps*num_ph2_steps)
                                t_axis = ch1_wf.getaxis('t')
                                data = ndshape([cycle_counter,len(timer_axis),4,2,len(t_axis),2],['cycle_counter','timer','ph1','ph2','t','ch']).alloc(dtype=float64)
                                data.setaxis('t',t_axis).set_units('t','s')
                                data.setaxis('ch',r_[1,2])
                                data.setaxis('ph1',r_[0:4])
                                data.setaxis('ph2',r_[0,2])
                                data.setaxis('cycle_counter',r_[0:cycle_counter]+1)
                                data.setaxis('timer',timer_axis)
                                #}}}
                            timer_axis[timer_index] = this_time
                            data['cycle_counter',x]['timer',timer_index]['ph1':ph1]['ph2':ph2]['ch',0] = ch1_wf
                            # alternative is to do ['ph1',ph1]['ph2',ph2/2]
                            data['cycle_counter',x]['timer',timer_index]['ph1':ph1]['ph2':ph2]['ch',1] = ch2_wf
                            print "**********"
                            print "CYCLE NO. INDEX",x
                            print "ph1",ph1
                            print "ph2",ph2
                            print "**********"
                            print "Done acquiring"
                            timer_index += 1
                            print "*** PRINTING TIMER AXIS ***"
                            print timer_axis
            #}}}
    print "*** *** *** PRINTING FINAL TIMER AXIS *** *** ***"
    print timer_axis
    data.setaxis('timer',timer_axis)
    data.name("this_capture")
    data.hdf5_write(date+"_"+id_string+".h5")
    end_ph = timer()
    return start_ph,end_ph 
#}}}

date = '180717'
id_string = 'SE_test'
num_cycles = 2 
t1,t2 = spin_echo(cycle_counter = num_cycles)
#raw_input("Start magnetic field sweep")
#start_acq = timer()
#acquire(date,id_string,captures)
#end_acq = timer()
print "Time:",t2-t1,"s"
