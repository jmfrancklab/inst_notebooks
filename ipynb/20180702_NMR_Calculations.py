
# coding: utf-8

# In[ ]:


get_ipython().magic(u'load_ext pyspecdata.ipy')
from pyspecdata import strm, gammabar_H, k_B, hbar
def mdown(x):
    import IPython.display as d
    d.display(d.Markdown(x))


# In[ ]:


## Physical constants
mu = 4*pi*1e-7 #[T*m/Amp]
gH = 2*pi*gammabar_H #[Hz/T]
kB = 1.381e-23 #[J/K]
hbar = 6.626e-34/2/pi #[J*s]
nuclear_spin = 0.5 #angular momentum


# In[ ]:


## Solenoid geometry
length = 22.89e-3
outer_diameter = 8.25e-3
thick = 1.17e-3
inner_diameter = outer_diameter-thick
volume_coil = pi*length*(inner_diameter/2)**2 #[m**3]
print "*Volume of solenoid in probe* \n",volume_coil,"m^3"


# In[ ]:


## Quality factor
f_resonant = 14.4495e6 #[Hz]
omega_resonant = f_resonant*2*pi
df = (14.9353e6 - 14.0719e6) #[Hz]
print "*Resonant frequency measured from tuning curve*\n",f_resonant*1e-6,"MHz"
print "*Width of resonator tuning dip*\n",df*1e-6,"MHz"
Q = f_resonant/df
print "*Quality factor*\n",Q


# In[ ]:


## Other parameters
pulse_power = 51.87 #[W]
temperature = 290 #[K]
resistance = 50. #[Ohms]
bandwidth = 22e6 #[Hz]
N = 2*55*6.02e23*1e3 #[1H spins/m^3]


# Define the average magnetic field of the pulse:
# $$B_1 = \sqrt{\frac{P \mu Q}{2 V_{coil} \omega_0}}$$

# In[ ]:


## Calculating B1
B1 = sqrt(pulse_power*Q*mu/volume_coil/2/omega_resonant)
print "*B1 field during pulse*\n",B1,"Tesla \n",B1/1e-4,"Gauss"
B1_new = conversion_factor*sqrt(pulse_power)


# Define conversion factor:
# $$\frac{B_1}{\sqrt{P}} = \sqrt{\frac{\mu Q}{2 V_{coil} \omega_0}}$$

# In[ ]:


## Calculating conversion factor
conversion_factor = B1/sqrt(pulse_power)
print "*Conversion factor*\n",conversion_factor,"Tesla/sqrt(W)"
print conversion_factor/1e-4,"Gauss/sqrt(W)"


# Applying radiation $\omega_{1}$ for certain time length $\tau_{p}$ causes rotation $\alpha$:
# $$ \alpha = \omega_{1} \tau_{p} $$
# where $ B_{1} = \frac{\omega_{1}}{\gamma_{H}}$
# 
# For a 90-degree rotation, $\alpha = \pi/2$ and the time length of radiation should be:
# $$\tau_{p} = \frac{\alpha}{\omega_{1}} = \frac{\pi}{2 \omega_{1}} = \frac{\pi}{2 B_{1} \gamma_{H}} $$

# In[ ]:


## Calculating 90-time
tau_90 = pi/2/B1/gH
print "Time needed for pulse to supply desired power,",tau_90,"seconds"


# In[ ]:


## V_rms noise
V_noise = sqrt(4*kB*temperature*resistance*bandwidth)
print V_noise


# In[ ]:


## V_rms signal




M = N*gH*omega_resonant*hbar**2*(nuclear_spin*(nuclear_spin+1))/2/kB/temperature
print "Magnetization via Curie's Law",M




V_sample_new = pi*length*((4.93e-3-2*0.53e-3)/2)**2
V_sample_old = pi*(5e-3/2)**2*length
print "Volume sample assuming length of solenoid",V_sample,"m^3"




V_signal_old = omega_resonant*M*(B1/sqrt(pulse_power))*V_sample_old*sqrt(resistance)
print "Using previous volume, signal voltage",V_signal_old,"V_RMS"




V_signal_new = omega_resonant*M*(B1/sqrt(pulse_power))*V_sample_new*sqrt(resistance)
print "Using new volume, signal voltage",V_signal_new,"V_RMS"

