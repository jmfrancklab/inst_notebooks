from pyspecdata import *

f = raw_input("Input resonant frequency in MHz: ")
f = float(f)*1e6
print f
c = raw_input("Input capacitance in pF: ")
c = float(c)*1e-12
print c
w = f*2.*pi
L = 1./(w*w*c)
print "Inductance of coil in uH:"
print L



