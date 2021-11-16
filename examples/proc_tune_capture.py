from pyspecdata import *
import matplotlib.pyplot as plt
fl = figlist_var()
filename = search_filename('211115_120mM_TEMPOL.npz', exp_type='francklab_esr/alex', unique=True) 
set_1 = np.load(filename, allow_pickle=True, encoding='bytes')
print([j for j in set_1.keys()])
print(set_1.data)
set_1 = set_1['data'].item()
zoom1 = set_1[b'zoom1']
zoom2 = set_1[b'zoom2']
zoom4 = set_1[b'zoom4']
zoom8 = set_1[b'zoom8']
zoom1_nd = nddata(zoom1[0][0],['frequency'])
zoom2_nd = nddata(zoom2[0][0],['frequency'])
zoom4_nd = nddata(zoom4[0][0],['frequency'])
zoom8_nd = nddata(zoom8[0][0],['frequency'])
zoom1_nd.setaxis('frequency',zoom1[1][0])
zoom2_nd.setaxis('frequency',zoom2[1][0])
zoom4_nd.setaxis('frequency',zoom4[1][0])
zoom8_nd.setaxis('frequency',zoom8[1][0])
fl.next('zoom1')
fl.plot(zoom1_nd,'o')
fl.next('zoom2')
fl.plot(zoom2_nd,'o')
fl.next('zoom4')
fl.plot(zoom4_nd,'o')
fl.next('zoom8')
fl.plot(zoom8_nd,'o')
fl.next('tune capture')
fl.plot(zoom1_nd,'o',label='zoom 1')
fl.plot(zoom2_nd,'o',label='zoom 2')
fl.plot(zoom4_nd,'o',label='zoom 4')
fl.plot(zoom8_nd,'o',label='zoom 8')
fl.show()

