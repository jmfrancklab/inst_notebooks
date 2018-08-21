
# coding: utf-8

# In[1]:

from pyspecdata import *
from pyspecdata.plot_funcs.image import imagehsv
import os
import sys
import matplotlib.style
import matplotlib as mpl


mpl.rcParams['image.cmap'] = 'jet'
fl = figlist_var()

carrier_f = 14.4289e6

check_time = False 
for date,id_string,numchan,field_axis,cycle_time, in [
        #('180717','SE_sweep_3',2,linspace(3390,3400,420*4),168),
        #('180718','SE_sweep',2,linspace((3395-25/2),(3395+25/2),1050*4),168),
        #('180718','SE_sweep_2',2,linspace((3407-15/2),(3407+15/2),654*4),int(21.3*8)) 
        #('180718','SE_sweep_3',2,linspace((3407-3/2),(3407+3/2),1296*4),int(21.129*8)) 
        #('180718','SE_sweep_4',2,linspace((3407.05-0.1/2),(3407.05+0.1/2),425*4),int(21.3125*8)) 
        #('180719','SE_sweep',2,linspace((3407.3-1.0/2),(3407.3+1.0/2),425*4),int(20.9375*8)) 
        #('180719','SE_sweep_2',2,linspace((3407.3-0.1/2),(3407.3+0.1/2),420*4),int(20.975*8)), 
        #('180719','SE_sweep_3',2,linspace((3407.4-0.1/2),(3407.4+0.1/2),420*4),int(21.875*8)) 
        #('180725','SE_sweep',2,linspace((3407.30-500./2),(3407.30+500./2),2340*4),int(21.865*8)) 
        ('180726','SE_sweep',2,linspace((3407.30-50./2),(3407.30+50./2),2340*4),int(21.8325*8)) 
        ]:
    filename = date+'_'+id_string+'.h5'
    nodename = 'this_capture'
    #{{{ for checking time difference between captures
    # use this to find cycle_time variable, which will print if no AFG error is found
    if check_time:
        timing_node = 'timing_data'
        q = nddata_hdf5(filename+'/'+timing_node,
                directory = getDATADIR(exp_type='test_equip'))
        big_delay = False
        time_diff_list = []
        for x in xrange(ndshape(q)['t']):
            try :
                time_diff = q['t',x+1].data - q['t',x].data
            except :
                time_diff = q['t',x].data - q['t',x-1].data
            time_diff_list.append(time_diff)
            if time_diff > 25:
                big_delay = True
                print "\n\t*** *** ***"
                print "AFG error"
                print "\t*** *** ***\n"
            #print time_diff
        if not big_delay:
            time_diff_nddata = nddata(time_diff_list,[-1],['t']).labels('t',r_[0:len(time_diff_list)])
            avg_delay = time_diff_nddata.mean('t',return_error=False).data
            print "Did not find AFG error"
            print "Average delay between phase cycling steps:",avg_delay,"s"
        quit()
    #}}}
    if not check_time :
        s = nddata_hdf5(filename+'/'+nodename,
                directory = getDATADIR(exp_type='test_equip'))
        s.set_units('t','s')
        s.setaxis('ph1', r_[0:4]*0.25)
        s.setaxis('ph2', r_[0:4:2]*0.25)
        #s.setaxis('full_cyc',r_[0:ndshape(s)['full_cyc']]*0.25)
        s_raw = s.C.reorder('t',first=False)

        s.ft('t',shift=True)
        s = s['t':(0,None)]
        s.setaxis('t',lambda f: f-carrier_f)
        s.ift('t')

        fl.next('raw data') 
        fl.plot(s_raw['ch',1]['full_cyc',0]['ph2',0].reorder('t').real)
        #{{{ applying time-shift (i.e., defining new, more convenient x-axis below)
        # note, pulse length used below is manually determined
        pulse_slice = s_raw['t':(6.47267e-6,14.1078e-6)]['ch',1].real
        normalization = (pulse_slice**2).integrate('t')
        # this creates an nddata of the time averages for each 90 pulse
        average_time = (pulse_slice**2 * pulse_slice.fromaxis('t')).integrate('t')/normalization
        average_time.reorder('full_cyc',first=False)
        # shift the time axis down by the average time, so that 90 is centered around t=0
        s_raw.setaxis('t', lambda t: t-average_time.data.mean())
        # NOTE: check that this centers 90 around 0 on time axis
        #fl.next('time-shifted data')
        #fl.image(s_raw)
        #}}}
        pulse_slice = s_raw['t':(-4e-6,4e-6)]['ch',1].real
        # re-determine nddata of the time averages for the newly centered data
        average_time = (pulse_slice**2 * pulse_slice.fromaxis('t')).integrate('t')/normalization
        print average_time
        average_time.reorder('full_cyc',first=False)
        # take analytic, and apply phase correction based on the time averages 
        analytic = s_raw.C.ft('t',shift=True)['t':(0,None)]
        analytic.setaxis('t',lambda f: f-carrier_f)
        phase_factor = analytic.fromaxis('t',lambda x: 1j*2*pi*x)
        phase_factor *= average_time
        phase_factor.run(lambda x: exp(x))
        analytic *= phase_factor
        analytic.ift('t')
        # verify that we have phased the measured signal
        #fl.next('analytic signal, phased, time domain (ref ch)')
        #fl.image(analytic)

        # beginning phase correction now
        raw_corr = s_raw.C.ft('t',shift=True)
        # sign on 1j matters here, difference between proper cycling or off cycling
        phase_factor = raw_corr.fromaxis('t',lambda x: 1j*2*pi*x)
        phase_factor *= average_time
        phase_factor.run(lambda x: exp(x))
        raw_corr *= phase_factor
        # here zero filling or else signal amplitude will vary due to changes made in the f dimension 
        raw_corr.ift('t',pad=30*1024)
        # with time-shifted, phase corrected raw data, now take analytic
        # measured phase is phase of each 90 after time-shifting and phase correcting
        analytic = raw_corr['ch',1].C.ft('t')['t':(0,16e6)].setaxis('t', lambda f: f-carrier_f).ift('t').reorder(['full_cyc','t'],first=False)
        measured_phase = analytic['t':(-4e-6,4e-6)].mean('t',return_error=False).mean('ph2',return_error=True).mean('full_cyc',return_error=True)
        measured_phase /= abs(measured_phase)
        print "measured phase"
        print measured_phase
        # expected phase is how we expect the phases to cycle, and how it is programmed in the pulse sequence
        expected_phase = nddata(exp(r_[0,1,2,3]*pi/2*1j),[4],['ph1'])
        # phase correcting analytic signal by difference between expected and measured phases
        analytic *= expected_phase/measured_phase
        #fl.next('analytic signal, ref ch')
        #fl.image(analytic['t':(-2e-6,75e-6)])
        # switch to coherence domain
        fl.next('coherence domain, ref ch')
        coherence_domain = analytic.C.ift(['ph1','ph2'])
        fl.image(coherence_domain['t':(-2e-6,75e-6)])

        # apply same analysis as on reference ch to test ch
        s_analytic = raw_corr['ch',0].C.ft('t')['t':(13e6,16e6)].setaxis('t', lambda f: f-carrier_f).ift('t').reorder(['full_cyc','t'],first=False)
        s_analytic *= expected_phase/measured_phase
        #s_analytic.ift(['ph1','ph2'])
        #fl.next('Testing coherence domain')
        #fl.image(s_analytic)
        #fl.show()
        #quit()
        s_analytic.name('Amplitude').set_units('V')
        #{{{ here plotting sweep data several ways
        s_analytic.rename('full_cyc','magnetic_field')
        # slice out region containing spin echo to get clear frequency domain plots
        #s_analytic = s_analytic['t':(110e-6,None)]
        for x in xrange(ndshape(s_analytic)['magnetic_field']):
            s_analytic.getaxis('magnetic_field')[x] = field_axis[x*cycle_time]
            print field_axis[x*cycle_time]
            s_analytic.set_units('magnetic_field','G')
        #{{{ this is specifically because field sweep stopped before program finished for '180718_SE_sweep'
        #s_analytic = s_analytic['magnetic_field':(field_axis[0],field_axis[24*cycle_time])]
        #}}}
        print ndshape(s_analytic)
        s_analytic.ift(['ph1','ph2'])
        #{{{ here I am making a copy of this dataset to plot with frequency axis converted to Gauss
        s_analytic_f = s_analytic.C.ft('t')
        s_analytic_f.setaxis('t', lambda x: x/(gammabar_H)*1e4).set_units('t','G')
        s_analytic_f.rename('t',r'$\frac{\Omega}{2 \pi \gamma_{H}}$')
        s_analytic_f.rename('magnetic_field',r'$B_{0}$')
        #}}}
        fl.next('signal(B) as function of '+r'$B_{0}$ (50 G sweep)')
        fl.image(s_analytic_f['ph1',1]['ph2',0])
        signal = s_analytic['ph1',1]['ph2',0].C
        signal.rename('magnetic_field','B0')


# In[ ]:

# Pull the dataset generated in the processing code,
# save to a checkpoint for later reference
# and other preliminary jupyternb things


# In[2]:

get_ipython().magic(u'load_ext pyspecdata.ipy')
fl = figlist_var()
raw = signal.C


# In[3]:

s = raw.C # checkpoint


# In[4]:

s.set_error(None)
s.setaxis('t', lambda t: t - 107.5e-6)
s = s['t':(-12e-6,None)]
print ndshape(s)


# In[ ]:

get_ipython().magic(u'matplotlib inline')


# In[ ]:

# Choose one dataset to phase, and then apply these phase corrections to the rest


# In[ ]:

for x in xrange(ndshape(s)['B0']):
    figure('time %s'%x);title('time %s'%x)
    plot(s['B0',x],alpha=0.4)
#xlim(100,None)
# Choosing data set 31


# In[ ]:

# Check that regions definde by max_hw (max half width) and window_hw contain signal and not noise


# In[5]:

s_choice = s['B0',31].C

figure('check our windows');title('check our windows')
max_hw = 27
window_hw = 15
index_max = abs(s_choice).argmax('t', raw_index = True).data
s_choice.setaxis('t', lambda t: t - s_choice.getaxis('t')[index_max])
s.setaxis('t', lambda t: t - s.getaxis('t')[index_max]) # NOTE: Need to do this in order to use the Hermitian cost
# function summed over the indirection dimension...
plot(abs(s_choice), alpha=0.5)
center_idx = where(s_choice.getaxis('t') == 0)[0][0]
for win_name,check_hw in [('max symm halfwidth',max_hw),('window halfwidth',window_hw)]:
    s_slice = s_choice['t', center_idx - check_hw : center_idx + check_hw + 1]
    span_min = s_choice.getaxis('t')[center_idx - check_hw]
    span_max = s_choice.getaxis('t')[center_idx + check_hw + 1]
    plot(abs(s_choice),':', c='violet')
    plot(abs(s_slice), c='blue', alpha = 0.5)
    axvline(span_min, c='k')
    axvline(span_max, c='k')
    gridandtick(gca())
dw = diff(s_choice.getaxis('t')[r_[0,1]])[0]
max_t_shift = (max_hw - window_hw) * dw


# In[6]:

s_copy = s_choice.C


# In[ ]:

# Generate cost function using Hermitian property of spin echo


# In[7]:

s_choice = s_copy.C # checkpoint


# In[8]:

N = 60.
fl.next('hermitian cost func')
s_check = s_choice.C
s_check = s_check['t',center_idx - max_hw : center_idx + max_hw + 1]
print ndshape(s_check)
sliced_center_idx = where(s_check.getaxis('t') == 0)[0][0]
s_check.ft('t')
ph0 = nddata(r_[-0.5:0.5:1j*N],'ph0').set_units('ph0','cyc')
ph0 = exp(1j*2*pi*ph0)
ph1 = nddata(r_[-max_t_shift:max_t_shift:1j*N],'ph1').set_units('ph1','s')
ph1 = exp(1j*2*pi*ph1*s_check.fromaxis('t'))
s_check *= ph1
s_check.ift('t')
s_check *= ph0
deviation = s_check['t',sliced_center_idx - window_hw : sliced_center_idx + window_hw + 1]
deviation = deviation['t',::-1].C.run(conj) - deviation
deviation.run(lambda x: abs(x)**2).sum('t')
fl.image(-1*deviation)


# In[9]:

## Adjust with frequency correction if axes are rotated


# In[10]:

s_choice = s_copy.C # checkpoint


# In[11]:

N = 60.
fl.next('hermitian cost func, adjust')
frq_corr = 70.3e-3/5.1e-6
s_choice *= exp(-1j*2*pi*frq_corr*s_choice.fromaxis('t'))
s_check = s_choice.C
s_check = s_check['t',center_idx - max_hw : center_idx + max_hw + 1]
print ndshape(s_check)
sliced_center_idx = where(s_check.getaxis('t') == 0)[0][0]
s_check.ft('t')
ph0 = nddata(r_[-0.5:0.5:1j*N],'ph0').set_units('ph0','cyc')
ph0 = exp(1j*2*pi*ph0)
ph1 = nddata(r_[-max_t_shift:max_t_shift:1j*N],'ph1').set_units('ph1','s')
ph1 = exp(1j*2*pi*ph1*s_check.fromaxis('t'))
s_check *= ph1
s_check.ift('t')
s_check *= ph0
deviation = s_check['t',sliced_center_idx - window_hw : sliced_center_idx + window_hw + 1]
deviation = deviation['t',::-1].C.run(conj) - deviation
deviation.run(lambda x: abs(x)**2).sum('t')
fl.image(-1*deviation) # easier to see the red
ph1_corr = 3.97e-6
ph0_corr = -178.4e-3


# In[12]:

## Annotate the selected region used to find the phase corrections


# In[13]:

s_choice = s_copy.C # checkpoint


# In[14]:

N = 60.
fl.next('hermitian cost func, adjust, correction')
frq_corr = 70.3e-3/5.1e-6
s_choice *= exp(-1j*2*pi*frq_corr*s_choice.fromaxis('t'))
s_check = s_choice.C
s_check = s_check['t',center_idx - max_hw : center_idx + max_hw + 1]
print ndshape(s_check)
sliced_center_idx = where(s_check.getaxis('t') == 0)[0][0]
s_check.ft('t')
ph0 = nddata(r_[-0.5:0.5:1j*N],'ph0').set_units('ph0','cyc')
ph0 = exp(1j*2*pi*ph0)
ph1 = nddata(r_[-max_t_shift:max_t_shift:1j*N],'ph1').set_units('ph1','s')
ph1 = exp(1j*2*pi*ph1*s_check.fromaxis('t'))
s_check *= ph1
s_check.ift('t')
s_check *= ph0
deviation = s_check['t',sliced_center_idx - window_hw : sliced_center_idx + window_hw + 1]
deviation = deviation['t',::-1].C.run(conj) - deviation
deviation.run(lambda x: abs(x)**2).sum('t')
fl.image(-1*deviation) # easier to see the red
ph1_corr = 4.05e-6
ph0_corr = 327e-3
fl.plot(ph0_corr/1e-3,ph1_corr/1e-6,'x',c='white')


# In[ ]:

### NEW APPROACH


# In[ ]:

### FOR FASTER PHASE CORRECTION


# In[ ]:

### SUM OVER THE INDIRECT (REPEAT/FIELD SWEEP) DIMENSIONS
### INSTEAD OF JUST PICKING ONE DIMENSION AND PHASING, THEN APPLYING


# In[15]:

fl.next('hermitian cost func, sum over indirect')
s_check = s.C.reorder('t') # use s containing all data instead of just one data set
# NOTE: s must be treated exactly the same as s_choice -- verify and be careful
s_check = s_check['t',center_idx - max_hw : center_idx + max_hw + 1]
print ndshape(s_check)
sliced_center_idx = where(s_check.getaxis('t') == 0)[0][0]
s_check.ft('t')
ph0 = nddata(r_[-0.5:0.5:1j*N],'ph0').set_units('ph0','cyc')
ph0 = exp(1j*2*pi*ph0)
ph1 = nddata(r_[-max_t_shift:max_t_shift:1j*N],'ph1').set_units('ph1','s')
ph1 = exp(1j*2*pi*ph1*s_check.fromaxis('t'))
s_check *= ph1
s_check.ift('t')
s_check *= ph0
deviation = s_check['t',sliced_center_idx - window_hw : sliced_center_idx + window_hw + 1]
deviation = deviation['t',::-1].C.run(conj) - deviation
deviation.run(lambda x: abs(x)**2).sum('t').sum('B0') # sum over indirect dimension
fl.image(-1*deviation)


# In[16]:

## Annotate the selected region used to find these overall phase corrections


# In[93]:

s_choice = s_copy.C # checkpoint


# In[94]:

fl.next('hermitian cost func, sum over indirect -- corrected')
s_check = s.C.reorder('t') # use s containing all data instead of just one data set
# NOTE: s must be treated exactly the same as s_choice -- verify and be careful
s_check = s_check['t',center_idx - max_hw : center_idx + max_hw + 1]
print ndshape(s_check)
sliced_center_idx = where(s_check.getaxis('t') == 0)[0][0]
s_check.ft('t')
ph0 = nddata(r_[-0.5:0.5:1j*N],'ph0').set_units('ph0','cyc')
ph0 = exp(1j*2*pi*ph0)
ph1 = nddata(r_[-max_t_shift:max_t_shift:1j*N],'ph1').set_units('ph1','s')
ph1 = exp(1j*2*pi*ph1*s_check.fromaxis('t'))
s_check *= ph1
s_check.ift('t')
s_check *= ph0
deviation = s_check['t',sliced_center_idx - window_hw : sliced_center_idx + window_hw + 1]
deviation = deviation['t',::-1].C.run(conj) - deviation
deviation.run(lambda x: abs(x)**2).sum('t').sum('B0') # sum over indirect dimension
fl.image(-1*deviation)
ph1_corr = 1.81e-6
ph0_corr = 311e-3
fl.plot(ph0_corr/1e-3,ph1_corr/1e-6,'x',c='white')


# In[95]:

full = s.C.reorder('t') # NOTE, not a checkpoint...


# In[96]:

full.ft('t')
full *= exp(1j*2*pi*ph0_corr) * exp(1j*2*pi*ph1_corr*full.fromaxis('t'))
full.ift('t')
full = full['t':(0,None)]
full['t',0] *= 0.5
full.ft('t')
# Zero pad begin
full = full['t':(-200e3,200e3)]
full.ift('t')
full.ft('t',pad=1024)
# End zero pad


# In[97]:

# Now make fine adjustments to phase by zooming


# In[98]:

this_string = 'adjusting zeroth order'
figure('%s'%this_string);title('%s'%this_string)
ph0 = nddata(r_[-100e-3:100e-3:1j*N],'ph0').set_units('ph0','cyc')
full_ph0 = full * exp(1j*2*pi*ph0)
print ndshape(full_ph0)
full_ph0.run(real).run(abs).sum('t').sum('B0')
plot(full_ph0, c='k', alpha=0.7)
ph0_corr = full_ph0.C.argmin('ph0').data.item()
full_corr = full * exp(1j*2*pi*ph0_corr)
full_ph0 = full_corr * exp(1j*2*pi*ph0) # verify that this is at 0
full_ph0.run(real).run(abs).sum('t').sum('B0')
plot(full_ph0, ':', c='purple')


# In[99]:

# If the above has been centered to zero,
# then apply zeroth order correction to dataset outright


# In[100]:

print "Fine-tuned zeroth order correction is",ph0_corr,"cycles"
full *= exp(1j*2*pi*ph0_corr) # fine-tuned zeroth order


# In[ ]:

# Plot properly phased data set as desired


# In[101]:

fl.next('image display of frequency sweep')
fl.image(full)
fl.show()


# In[102]:

fl.next('image display of frequency sweep -- real ')
fl.plot(full, alpha=0.7)
fl.show()


# In[103]:

envelope = full.C
envelope.run(real)[lambda x: x < 0] = 0
envelope.sum('B0')
envelope /= envelope.data.max()
envelope *= full.data.real.max()
fl.plot(envelope, color='k', alpha=0.25, human_units=False)


# In[ ]:

### END NEW APPROACH


# In[ ]:

# Apply phase corrections


# In[ ]:

s_choice = s_copy.C # checkpoint


# In[ ]:

s_choice.ft('t')
s.ft('t') # do to s as do to s choice
s_choice *= exp(1j*2*pi*ph0_corr) * exp(1j*2*pi*ph1_corr*s_choice.fromaxis('t'))
s *= exp(1j*2*pi*ph0_corr) * exp(1j*2*pi*ph1_corr*s.fromaxis('t'))
s_choice.ift('t')
s.ift('t')
figure('show the time domain signal')
plot(abs(s_choice), 'k', alpha=0.5)
plot(s_choice.imag, alpha = 0.5)
s_choice = s_choice['t', center_idx:]
s = s['t', center_idx:]
s_choice['t',0] /= 2.
s['t',0] /= 2.
plot(s_choice, alpha=0.5)
gridandtick(gca())


# In[ ]:

# Plot phase corrected signal in frequency domain
# Is there a baseline error?


# In[ ]:

s_choice.ft('t')
s.ft('t')
figure('ft')
plot(s_choice)
plot(s_choice.imag)


# In[ ]:

# To fix baseline error, generate cost function using traditional phasing method


# In[ ]:

fl.next('traditional cost function')
s_check = s_choice.C
ph0 = nddata(r_[-0.5:0.5:1j*N],'ph0').set_units('ph0','cyc')
ph0 = exp(1j*2*pi*ph0)
ph1 = nddata(r_[-3*dw:3*dw:1j*N],'ph1').set_units('ph1','s')
ph1 = exp(1j*2*pi*ph1*s_check.fromaxis('t'))
s_check *= ph1
s_check *= ph0
s_check.run(real).run(abs).sum('t')
fl.image(-1*s_check)


# In[ ]:

# Annotate where selecting phase corrections using this method


# In[ ]:

fl.next('traditional cost function')
s_check = s_choice.C
ph0 = nddata(r_[-0.5:0.5:1j*N],'ph0').set_units('ph0','cyc')
ph0 = exp(1j*2*pi*ph0)
ph1 = nddata(r_[-3*dw:3*dw:1j*N],'ph1').set_units('ph1','s')
ph1 = exp(1j*2*pi*ph1*s_check.fromaxis('t'))
s_check = s_check * ph1
s_check *= ph0
s_check.run(real).run(abs).sum('t')
fl.image(-1*s_check)
ph1_corr = -29e-9
ph0_corr = -52e-3
fl.plot(ph0_corr/1e-3,ph1_corr/1e-9,'x',c='white')


# In[ ]:

# Apply phase correction and plot in frequency domain
# Is the baseline error gone?


# In[ ]:

s_choice *= exp(1j*2*pi*ph0_corr) * exp(1j*2*pi*ph1_corr*s_choice.fromaxis('t'))
s *= exp(1j*2*pi*ph0_corr) * exp(1j*2*pi*ph1_corr*s.fromaxis('t'))
#s_choice.ift('t')
figure('show the time domain signal, 2')
plot(abs(s_choice), 'k', alpha=0.5)
plot(s_choice.imag, alpha = 0.5)
s_choice = s_choice['t', center_idx:]
s = s['t', center_idx:]
s_choice['t',0] /= 2.
s['t',0] /= 2.
plot(s_choice, alpha=0.5)
gridandtick(gca())

