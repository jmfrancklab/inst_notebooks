from pyspecdata import *
L_0 = 0.54e-6
C_tune = 220e-12
C_tune2 = 10e-12
C_TUNE = C_tune + C_tune2

# Without using the correction described in Fukushima p413
print "*** WITHOUT INDUCTANCE CORRECTION ***"
C_match = 10e-12
print "As I increase the variable tune capacitor"
print "Match at its lowest setting"
for C_tune2 in xrange(10,50,10):
    C_tune2 *= 1e-12
    C_TUNE = C_tune + C_tune2
    omega = 1./(sqrt(L_0*(C_match + C_TUNE)))
    print 1e-6*omega/(2*pi)
print "***"
C_match = 45e-12
print "As I increase the variable tune capacitor,"
print "Match at its highest setting"
for C_tune2 in xrange(10,50,10):
    C_tune2 *= 1e-12
    C_TUNE = C_tune + C_tune2
    omega = 1./(sqrt(L_0*(C_match + C_TUNE)))
    print 1e-6*omega/(2*pi)
print "***"
print "If I remove the variable tune capacitor"
print "Match at its lowest setting"
C_match = 10e-12
C_tune2 = 0
C_tune2 *= 1e-12
C_TUNE = C_tune + C_tune2
omega = 1./(sqrt(L_0*(C_match + C_TUNE)))
print 1e-6*omega/(2*pi)
print "***"
print "If I remove the variable tune capacitor"
print "Match at its highest setting"
C_match = 45e-12
C_tune2 = 0
C_tune2 *= 1e-12
C_TUNE = C_tune + C_tune2
omega = 1./(sqrt(L_0*(C_match + C_TUNE)))
print 1e-6*omega/(2*pi)

# Now include the correction
print "*** WITH INDUCTANCE CORRECTION ***"
C_match = 10e-12
print "As I increase the variable tune capacitor"
print "Match at its lowest setting"
for C_tune2 in xrange(10,50,10):
    C_tune2 *= 1e-12
    C_TUNE = C_tune + C_tune2
    corr = (1.+(C_match/C_TUNE))**2
    L = L_0/corr # L should be smaller than L_0
    omega = 1./(sqrt(L*(C_match + C_TUNE)))
    print 1e-6*omega/(2*pi)
print "***"
C_match = 45e-12
print "As I increase the variable tune capacitor,"
print "Match at its highest setting"
for C_tune2 in xrange(10,50,10):
    C_tune2 *= 1e-12
    C_TUNE = C_tune + C_tune2
    corr = (1.+(C_match/C_TUNE))**2
    L = L_0/corr
    omega = 1./(sqrt(L*(C_match + C_TUNE)))
    print 1e-6*omega/(2*pi)
print "***"
print "If I remove the variable tune capacitor"
print "Match at its lowest setting"
C_match = 10e-12
C_tune2 = 0
C_tune2 *= 1e-12
C_TUNE = C_tune + C_tune2
corr = (1.+(C_match/C_TUNE))**2
L = L_0/corr
omega = 1./(sqrt(L*(C_match + C_TUNE)))
print 1e-6*omega/(2*pi)
print "***"
print "If I remove the variable tune capacitor"
print "Match at its highest setting"
C_match = 45e-12
C_tune2 = 0
C_tune2 *= 1e-12
C_TUNE = C_tune + C_tune2
corr = (1.+(C_match/C_TUNE))**2
L = L_0/corr
omega = 1./(sqrt(L*(C_match + C_TUNE)))
print 1e-6*omega/(2*pi)



