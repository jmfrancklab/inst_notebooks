
# coding: utf-8

# 

get_ipython().magic(u'load_ext pyspecdata.ipy')
from scipy.linalg import expm
# this next part is not something I expected you to do -- I provide it here to provide nice matrix printing
import IPython.display as d
fl = figlist_var()


# 

Iz = 0.5*array([[1,0],[0,-1]],dtype=complex128)

Ix = 0.5*array([[0,1],[1,0]],dtype=complex128)

Iy = 0.5*array([[0,-1j],[1j,0]],dtype=complex128)

E = array([[1,0],[0,1]],dtype=complex128)

Iz = 0.5*array([[1,0],[0,-1]],dtype=complex128)
Ix = 0.5*array([[0,1],[1,0]],dtype=complex128)
Iy = 0.5*array([[0,-1j],[1j,0]],dtype=complex128)
E = array([[1,0],[0,1]],dtype=complex128)

Ip = Ix + 1j*Iy
Im = Ix - 1j*Iy

map(d.display,[Iz,Ix,Iy,E,Ip,Im])


# 

t90 = 2.1e-6
omega1_nominal = 2*pi/(4*t90)
results = ndshape([100,1000],['omega1','Omega']).alloc()
omega1_axis = linspace(0,3*omega1_nominal,ndshape(results)['omega1'])
omega_axis = linspace(-omega1_nominal*3,omega1_nominal*3,ndshape(results)['Omega'])
results.labels(['omega1','Omega'],[omega1_axis/2/pi,omega_axis/2/pi])
tau = 50e-6
for i,omega1 in enumerate(omega1_axis):
    for j,Omega in enumerate(omega_axis):
        U90 = expm(-1j*omega1*t90*Ix-1j*Omega*t90*Iz)
        U180 = expm(-1j*omega1*2*t90*Ix-1j*Omega*2*t90*Iz)
        Uev = expm(-1j*Omega*tau*Iz)
        Uev_echo = expm(-1j*Omega*(tau+2*t90/pi)*Iz)
        Utot = Uev.dot(U180).dot(Uev).dot(U90)
        rho = Utot.dot(Iz).dot(Utot.T.conj())
        results['omega1',i]['Omega',j] = rho[1,0]
results.set_units('omega1','Hz').set_units('Omega','Hz')
results.rename('omega1',r'$\omega_1/2\pi$').rename('Omega',r'$\Omega/2\pi$')


# 

fl.next('original simulation w phase',figsize=(14,14)) # I want figsize, and I need fl so that it handles the units
fl.image(results, black=True)


# 

fl.next('original simulation abs',figsize=(14,14)) # I want figsize, and I need fl so that it handles the units
fl.image(abs(results))


# 

# try varying B1 amplitude to get the 180 instead (half-amplitude 180 pulse for the 90)
t90 = 2.1e-6
omega1_nominal = 2*pi/(4*t90)
results = ndshape([100,1000],['omega1','Omega']).alloc()
omega1_axis = linspace(0,3*omega1_nominal,ndshape(results)['omega1'])
omega_axis = linspace(-omega1_nominal*3,omega1_nominal*3,ndshape(results)['Omega'])
results.labels(['omega1','Omega'],[omega1_axis/2/pi,omega_axis/2/pi])
tau = 50e-6
for i,omega1 in enumerate(omega1_axis):
    for j,Omega in enumerate(omega_axis):
        U90 = expm(-1j*omega1*t90*Ix-1j*Omega*2*t90*Iz)
        U180 = expm(-1j*omega1*2*t90*Ix-1j*Omega*t90*Iz)
        Uev = expm(-1j*Omega*tau*Iz)
        Uev_echo = expm(-1j*Omega*(tau+4*t90/pi)*Iz)
        Utot = Uev.dot(U180).dot(Uev).dot(U90)
        rho = Utot.dot(Iz).dot(Utot.T.conj())
        results['omega1',i]['Omega',j] = rho[1,0]
results.set_units('omega1','Hz').set_units('Omega','Hz')
results.rename('omega1',r'$\omega_1/2\pi$').rename('Omega',r'$\Omega/2\pi$')


# 

fl.next('two amps simulation w phase',figsize=(14,14)) # I want figsize, and I need fl so that it handles the units
fl.image(results, black=True)


# 

fl.next('two amps simulation abs',figsize=(14,14)) # I want figsize, and I need fl so that it handles the units
fl.image(abs(results))


# 

# how far do we have to go to not see signal at all?
t90 = 2.1e-6
omega1_nominal = 2*pi/(4*t90)
results = ndshape([100,1000],['omega1','Omega']).alloc()
omega1_axis = linspace(0,3*omega1_nominal,ndshape(results)['omega1'])
omega_axis = linspace(-omega1_nominal*10,omega1_nominal*10,ndshape(results)['Omega'])
results.labels(['omega1','Omega'],[omega1_axis/2/pi,omega_axis/2/pi])
tau = 50e-6
for i,omega1 in enumerate(omega1_axis):
    for j,Omega in enumerate(omega_axis):
        U90 = expm(-1j*omega1*t90*Ix-1j*Omega*t90*Iz)
        U180 = expm(-1j*omega1*2*t90*Ix-1j*Omega*2*t90*Iz)
        Uev = expm(-1j*Omega*tau*Iz)
        Uev_echo = expm(-1j*Omega*(tau+2*t90/pi)*Iz)
        Utot = Uev.dot(U180).dot(Uev).dot(U90)
        rho = Utot.dot(Iz).dot(Utot.T.conj())
        results['omega1',i]['Omega',j] = rho[1,0]
results.set_units('omega1','Hz').set_units('Omega','Hz')
results.rename('omega1',r'$\omega_1/2\pi$').rename('Omega',r'$\Omega/2\pi$')


# 

fl.next('original simulation zoomed out abs',figsize=(14,14)) # I want figsize, and I need fl so that it handles the units
fl.image(abs(results))


# 

3e6/gammabar_H/1e-4


# 

1e6/gammabar_H/1e-4


# 

500e-4*gammabar_H/1e6


# 

500e-4/4.258e7

