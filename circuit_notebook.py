
# coding: utf-8

# In[1]:

get_ipython().magic(u'pylab inline')
from pyspecdata import *
from IPython.display import Markdown,display
get_ipython().magic(u'load_ext pyspecdata.ipy')


# to run this, run py convert.py circuit_notebook.py, and run the ipynb file output

# # Part 1: simulating a series circuit

# In[2]:

C_tune = 12.5e-12
C_match = 6e-13
L = 9.026e-6
R = 2.0


# first calculate the resonant frequency

# In[3]:

C_resonant = 1./((2*pi*15e6)**2*L)
print C_resonant/1e-12,'pF'


# Now, pick a reasonable capacitance, and simulate the result that we expect.  I define $Z$ as a function, so that I can set the resistance easily.

# In[4]:

C = 12e-12
nu = r_[10:20:5000j]*1e6
omega = 2*pi*nu
f_expect = 1/sqrt(L*C)/2/pi/1e6
print "expected resonance",f_expect,'MHz'

Z = lambda R: 1./(1j*omega*C) + R + 1j*omega*L


# show the phase of the impedance (which is not actually observed)

# In[5]:

plot(nu,angle(Z(1))/pi)
ylabel('phase angle / (rad/$\pi$)')
ylim(-1,1)
title('phase of impedance')


# Now we show the phase of the reflection, which is what we actually observe.
# Here, I'm verifying that **with the series circuit, we should definitely see a nice phase inflection**.

# In[6]:

reflection = lambda R: (Z(R)-50.)/(Z(R)+50)
for R in linspace(1e-3,60,10):
    plot(nu,angle(reflection(R))/pi,label='%0.2f $\\Omega$'%R,
        alpha=0.5)
ylabel('phase angle / (rad/$\pi$)')
ylim(-1,1)
legend(**dict(bbox_to_anchor=(1.05,1),loc = 2,borderaxespad=0.))
title('phase of reflection')


# Above, I'm showing that the peak to peak amplitude of the inflection isn't really affected by the resistance of the circuit, until we exceed the characteristic impedance.  This is good, because it means that we have a very robust method for identifying our impedance.  On the other hand, it means this is not the best way to identify the $Q$ of our circuit.
# 
# In the following, I use resistance over reactancce to calculate the $Q$ of the circuit, and note that I have at least a qualitative idea of the $Q$ from the peak-to-peak height and width of the imaginary part of the reflection.  Unfortunately, the peak-to-peak width doesn't seem to relate in a straightforward way to $Q=\frac{f_0}{\Delta f}$ the way that I would like.

# In[7]:

for R in linspace(1e-2,60,10):
    plot(nu/1e6,reflection(R).imag,label='%0.2f $\\Omega$'%R,
        alpha=0.5)
    Q = (2*pi*f_expect*1e6*L)/R
    display(Markdown(r'at %0.2f $\Omega$, $Q=%0.2f$, $\Delta f = \frac{f_0}{Q}=%0.2f MHz$'%(R,Q,f_expect/Q)))
ylabel('fraction')
xlabel('frequency / MHz')
ylim(-1,1)
legend(**dict(bbox_to_anchor=(1.05,1),loc = 2,borderaxespad=0.))
title('imaginary part of reflection')


# here I save the reflection data for later

# In[8]:

r = nddata(reflection(1.),['f'])
r.setaxis('f',nu)


# I also show the magnitude of the reflection.
# I show this on a scale of 0 to 1, because if the blip looks small on this scale, we *probably can't see it*.
# As I would expect, unless I artificially add in a lot of resistance, I'm not really going to see a dip here.

# In[9]:

for R in linspace(1e-3,60,10):
    plot(nu,abs(reflection(R)),label='%0.2f $\\Omega$'%R,
        alpha=0.5)
ylabel('fraction')
legend(**dict(bbox_to_anchor=(1.05,1),loc = 2,borderaxespad=0.))
ylim(0,1.1)
title('magnitude of reflection')


# ### Verify that I can determine the resonance frequency from the phase
# 
# to make this work, I updated pyspecdata on the franck_devel branch -- so don't worry about running this block

# In[10]:

import scipy.optimize as o
imd = r.C
imd.data = r.imag.data
fn = imd.interp('f',None,return_func=True)
print "measured resonance frequency is",o.newton(fn,15e6)/1e6,"MHz vs. expected",f_expect,'MHz'


# # Part 2: Use sympy to calculate 

# In[11]:

import sympy as s
s.init_printing()


o, Cm, Rm, Ct, Cs, Cr, Rt, Ls = s.symbols('omega C_match R_match C_tune C_sum C_ratio R_tune L',real=True,positive=True)


# Initially, I planned to include a resistance that could be in series with the inductor and/or tuning capacitor as well.  On messing around below, I find that this really complicates things, leading to four solutions, etc.

# In[12]:

Z = -1j/o/Cm + Rm + 1/(1/(1j*o*Ls)+1/(-1j/Ct/o))
Z = s.simplify(Z)
Z


# Calculate the resonance frequency by finding the frequency at which the imaginary part of the impedance is zero

# In[13]:

res_freq = s.solve(s.Eq(s.simplify(s.im(Z)),0),o)
res_freq


# Here, I had gotten two solutions, but when I set positive=True above, it only gives me the positive solution (since $\omega$ is positive), which is pretty sweet

# In[14]:

res_freq = res_freq[0]


# Now I ask what impedance I get at that resonance frequency

# In[15]:

s.simplify(Z.subs(o,res_freq))


# This unpleasantly doesn't allow me to vary the impedance at resonance by varying the tuning and matching.  This does make sense -- without any resistance in the parallel part of the circuit, it has an impedance that is purely imaginary, and when attempting to tune, the best we can do is to set it to zero.

# ### Redo everything in terms of sum and ratio capacitances
# To try to make life easier proceeding forward, I'm going to define
# $C_{sum} = C_{tune} (1 + C_{ratio})$
# where $C_{ratio}$ is unitless and gives the fractional ratio between the match capacitance and the tune ($C_{match}=C_{ratio} C_{tune}$)

# In[16]:

Z = Z.subs(Cm,Cr*Ct).simplify().subs(Ct,Cs/(1+Cr)).simplify()
Z


# Calculate the resonance frequency by finding the frequency at which the imaginary part of the impedance is zero

# In[17]:

res_freq = s.solve(s.Eq(s.simplify(s.im(Z)),0),o)[0]
res_freq


# Now I ask what impedance I get at that resonance frequency

# In[18]:

s.simplify(Z.subs(o,res_freq))


# ### Add in tune resistance
# With the simpler form, try to add in tune resistance, and see what happens

# In[19]:

Z = -1j/o/Cm + Rm + 1/(1/(1j*o*Ls + Rt)+1/(-1j/Ct/o + Rt))
Z = Z.subs(Cm,Cr*Ct).simplify().subs(Ct,Cs/(1+Cr)).simplify()


# the following shows that just finding the solutions isn't great, because substituting back in for $R_{tune}$ doesn't return me to the answer above.

# In[20]:

#res_freq = s.solve(s.Eq(s.simplify(s.im(Z)),0),o)
#len(res_freq) # to see how many solutions


# In[21]:

#i=1
#for j in range(4):
#    display(res_freq[j].subs(Rt,0).simplify())


# Using a Taylor expansion to first order, I see how this is a fourth-order equation, giving rise to the difficulties above.

# In[22]:

order = 1
taylor_exp = sum(Rt**j/s.factorial(j)*Z.diff(Rt,j).subs(Rt,0).simplify() for j in range(order+1))
taylor_exp


# let's instead ask -- if I have a circuit of a particular resonance, what Csum is required to tune it?
# 
# It chokes on a direct solution

# In[25]:

#res_freq = s.solve(s.Eq(s.simplify(s.im(Z)),0),Cs)


# But if we use the taylor expansion to first order in $R_{tune}$, it tells us that we want the same $C_{sum}$ as above:

# In[26]:

res_freq = s.solve(s.Eq(s.simplify(s.im(taylor_exp)),0),Cs)
res_freq


# So, let's just ask what the impedance is at that frequency:

# In[ ]:

res_freq = 1/s.sqrt(Ls*Cs)
imp_at_approx_res = s.simplify(Z.subs(o,res_freq))
imp_at_approx_res


# Note that this is a decent thing to do, since we are at least somewhat close to resonance, and we're getting an idea of what our impedance is like near resonance:

# In[31]:

s.re(imp_at_approx_res).simplify()


# So, as we expect, the $C_{ratio}$ does allow us to adjust the real part of our impedance (so we can target 50 $\Omega$), but the value we want will depend very strongly on the built-in resistances in the circuit, which we don't really control.

# In[41]:

Cn = s.symbols('C_{new}',positive=True,real=True)
# Cn = (Cr+1)/Cs
s.numer(s.im(Z).subs(Cr,Cn*Cs-1).simplify())


# In[ ]:



