
# coding: utf-8

# In[ ]:


get_ipython().magic(u'load_ext pyspecdata.ipy')
from pyspecdata import strm, gammabar_H, k_B, hbar
def mdown(x):
    import IPython.display as d
    d.display(d.Markdown(x))


# In[ ]:


## Physical constants


# In[ ]:


mu = 4*pi*1e-7 #[T*m/Amp]
gH = 2*pi*gammabar_H #[Hz/T]
kB = 1.381e-23 #[J/K]
hbar = 6.626e-34/2/pi #[J*s]
nuclear_spin = 0.5 #angular momentum


# In[ ]:


## Solenoid geometry


# In[ ]:


length = 22.89e-3
outer_diameter = 8.25e-3
volume_coil = pi*length*(outer_diameter/2)**2 #[m**3]
print "Volume of solenoid in probe",volume_coil,"m^3"


# In[ ]:


## Quality factor


# In[ ]:


f_resonant = 14.4495e6 #[Hz]
omega_resonant = f_resonant*2*pi
df = (14.9353e6 - 14.0719e6) #[Hz]
print f_resonant
print df
Q = f_resonant/df
print Q


# In[ ]:


## Other parameters


# In[ ]:


pulse_power = 51.87 #[W]
temperature = 290 #[K]
resistance = 50. #[Ohms]
bandwidth = 22e6 #[Hz]
N = 2*55*6.02e23*1e3 #[1H spins/m^3]


# In[ ]:


## Calculating B1


# In[ ]:


B1 = sqrt(pulse_power*Q*mu/volume_coil/2/omega_resonant)
print "Magnetic field during pulse:",B1,"Tesla"


# In[ ]:


## Calculating 90-time


# In[ ]:


tau_90 = pi/B1/gH
print "Time needed for pulse to supply desired power,",tau_90,"seconds"


# In[ ]:


## V_rms noise


# In[ ]:


V_noise = sqrt(4*kB*temperature*resistance*bandwidth)
print V_noise


# In[ ]:


## V_rms signal


# In[ ]:


M = N*gH*omega_resonant*hbar**2*(nuclear_spin*(nuclear_spin+1))/2/kB/temperature
print "Magnetization via Curie's Law",M


# In[ ]:


V_sample_new = pi*length*((4.93e-3-2*0.53e-3)/2)**2
V_sample_old = pi*(5e-3/2)**2*length
print "Volume sample assuming length of solenoid",V_sample,"m^3"


# In[ ]:


V_signal_old = omega_resonant*M*(B1/sqrt(pulse_power))*V_sample_old*sqrt(resistance)
print "Using previous volume, signal voltage",V_signal_old,"V_RMS"


# In[ ]:


V_signal_new = omega_resonant*M*(B1/sqrt(pulse_power))*V_sample_new*sqrt(resistance)
print "Using new volume, signal voltage",V_signal_new,"V_RMS"


# In[ ]:




