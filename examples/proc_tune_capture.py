from pyspecdata import *
import matplotlib.pyplot as plt
fl = figlist_var()
set_1 = np.load('empty_tubezoom1.npz')
set_2 = np.load('empty_tubezoom2.npz')
set_3 = np.load('empty_tubezoom4.npz')
set_4 = np.load('empty_tubezoom8.npz')

nd_set_1 = nddata(set_1['data'],['frq'])
nd_set_1.setaxis('frq',set_1['frq'])
nd_set_2 = nddata(set_2['data'],['frq'])
nd_set_2.setaxis('frq',set_2['frq'])
nd_set_3 = nddata(set_3['data'],['frq'])
nd_set_3.setaxis('frq',set_3['frq'])
nd_set_4 = nddata(set_4['data'],['frq'])
nd_set_4.setaxis('frq',set_4['frq'])


fl.next('tune capture')
fl.plot(nd_set_1,'o',label='zoom 1')
fl.plot(nd_set_2,'o',label='zoom 2')
fl.plot(nd_set_3,'o',label='zoom 4')
fl.plot(nd_set_4,'o',label='zoom 8')
fl.show()

