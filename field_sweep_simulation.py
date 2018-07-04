from pyspecdata import *
fl = figlist_var()
#{{{ Carried over from NMR SNR calculations -- can be reduced/cleaned up
## Physical constants
mu = 4*pi*1e-7 #[T*m/Amp]
gH = 2*pi*gammabar_H #[Hz/T]
kB = 1.381e-23 #[J/K]
hbar = 6.626e-34/2/pi #[J*s]
nuclear_spin = 0.5 #angular momentum
## Solenoid geometry
length = 22.89e-3
outer_diameter = 8.25e-3
volume_coil = pi*length*(outer_diameter/2)**2 #[m**3]
print "Volume of solenoid in probe",volume_coil,"m^3"
## Quality factor
f_resonant = 14.4495e6 #[Hz]
omega_resonant = f_resonant*2*pi
df = (14.9353e6 - 14.0719e6) #[Hz]
Q = f_resonant/df
print Q
## Other parameters
pulse_power = 51.87 #[W]
temperature = 290 #[K]
resistance = 50. #[Ohms]
bandwidth = 22e6 #[Hz]
N = 2*55*6.02e23*1e3 #[1H spins/m^3]
M = N*gH*omega_resonant*hbar**2*(nuclear_spin*(nuclear_spin+1))/2/kB/temperature #[Magnetization]
## Calculating B1, 90-time, signal
B1 = sqrt(pulse_power*Q*mu/volume_coil/2/omega_resonant)
tau_90 = pi/B1/gH
volume_sample = pi*length*((4.93e-3-2*0.53e-3)/2)**2
V_signal = omega_resonant*M*(B1/sqrt(pulse_power))*volume_sample*sqrt(resistance)
#}}}
### Where simulation begins
time_space = linspace(1e-6,9e-6,25) #Initially, I wanted 25,000 pulse lengths
freq_space = linspace(-1e6*2*pi,1e6*2*pi,25) #and 6,000 offset frequencies
f_array = omega_resonant - freq_space
nd_time = nddata((time_space),('pulse_length'))
nd_omega = nddata((f_array),('offset'))
# Practice axes - save for troubleshooting
#this_t = linspace(1,26,25)
#this_f = linspace(-5,5,60)
# Practice axes, but more realistic
#this_t = linspace(1e-6,9e-6,25)
#this_f = linspace(-1e6,1e6,60)
this_t = time_space
this_f = f_array

column = []
for x in xrange(len(this_t)):
    empty_array = []
    column.append(empty_array)
print shape(column)

### Most important part of simulation below --

signal_array = []
for t in this_t:
    print "****",t,"****"
    print list(this_t).index(t) #this is cool
    b1 = pi/t/gH
    column[list(this_t).index(t)] = []
    print shape(column)
    for f in this_f:
        signal = (omega_resonant-f)*M*(b1/sqrt(pulse_power))*volume_sample*sqrt(resistance)
        column[list(this_t).index(t)].append(signal)
    #signal_array[list(this_f).index(f)].append(column)
        signal_array.append(column)
print shape(signal_array) # I think this is what I want...

signal_nd = nddata(array(signal_array),['signal','pulse_time','freq'])

signal_nd.setaxis('pulse_time',nd_time.getaxis('pulse_length'))
signal_nd.setaxis('freq',nd_omega.getaxis('offset'))

fl.next('Test')
fl.image(signal_nd)

fl.show()
