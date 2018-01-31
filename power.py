from pyspecdata import *
atten = 10**(-40./10)
Vpp = raw_input('Enter Vpp from scope: ')
print ''+Vpp+' Vpp'
Vpp = float(Vpp)
Vpp = Vpp/2.
W = (Vpp/2./sqrt(2))**2/50.
print 'Corresponding power is:'
W = str(W)
print ''+W+' Watts'


