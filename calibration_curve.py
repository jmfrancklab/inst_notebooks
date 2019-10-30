from pyspecdata import *
from Instruments import Bridge12,HP8672A, prologix_connection, gigatronics
import time

id_string = '191030_HP_calib_coupler_2'

start_power = -40
stop_power = -5 
# If running through amplifier (Bridge12) do not exceed
# -5 dBm or you will damage the meter!!
power_points = 10
HP_powers = linspace(start_power,stop_power,power_points)

raw_points = 250
raw_powers = zeros(raw_points*power_points)

count = 0
with Bridge12() as b:
    b.set_wg(True)
    b.set_rf(True)
    b.set_amp(True)
    b.calib_set_freq(9.85e9)
    b.calib_set_power(10)
    time.sleep(5)
    with prologix_connection() as p:
        with HP8672A(prologix_instance=p, address=19) as h:
            with gigatronics(prologix_instance=p, address=7) as g:
                for hp_setting in HP_powers:
                        print "*** *** ***"
                        print "SETTING POWER",hp_setting
                        print "*** *** ***"
                        h.set_frequency(9.85e9)
                        h.set_power(hp_setting)
                        for x in xrange(raw_points):
                            raw_powers[count] = g.read_power()
                            count += 1

avg_powers = zeros(power_points)
for x in xrange(power_points):
    avg_powers[x] = raw_powers[raw_points*x:raw_points*(x+1)].mean()

savez(id_string,prog_powers=HP_powers,read_powers=avg_powers)

with prologix_connection() as p:
    with HP8672A(prologix_instance=p, address=19) as h:
        print "SETTING HP SOURCE TO LOW POWER SETTING"
        h.set_power(-110)

figure()
title('calibration curve')
plot(HP_powers,avg_powers,'.')
show()
