from pyspecdata import *
import matplotlib.pyplot as plt
fl = figlist_var()
filename = search_filename('211116_120mM_TEMPOL.npz', exp_type='francklab_esr/alex', unique=True)
data = np.load(filename)
zooms = ['zoom1','zoom2','zoom4','zoom8']
nd_data = {}
for value in zooms:
    zoom_data = data['%s'%value].squeeze()
    zoom_data_nd = nddata(zoom_data[0],'frequency')
    zoom_data_nd.setaxis('frequency',zoom_data[1])
    nd_data['%s'%value]=zoom_data_nd
    fl.next('%s'%value)
    fl.plot(zoom_data_nd,'o')
labels = list(nd_data.keys())
fl.next('tuning curve capture')
for j in range(len(labels)):
    fl.plot(nd_data['%s'%labels[j]],'o',label='%s'%labels[j])
fl.show()
