from pyspecdata import *

f = raw_input("Input resonant frequency in MHz: ")
f = float(f)*1e6
print f
L = raw_input("Input inductance in uH: ")
L = float(L)*1e-6
print L 
w = f*2.*pi
C = 1./(w*w*L)
print "Capacitance of circuit in pF:"
print C
