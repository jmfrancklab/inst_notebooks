#!/usr/bin/python
# use https://github.com/OE-FET/customxepr/blob/fc3ff0407d89f955a106056112e50b71a3ae8756/customxepr/main.py as a reference
import numpy as np
import matplotlib.pyplot as plt
import sys
import time
sys.path.append('/opt/Bruker/xepr/sharedProDeL/Standard/XeprAPI/')
import XeprAPI
x = XeprAPI.Xepr()
x.XeprOpen()
h = x.XeprExperiment('AcqHidden')
freq = h["FrequencyMon"].value  # get current frequency
h["OpMode"].value = "Tune"
time.sleep(2.0)
print("the mode zoom is",h["ModeZoom"].value,"and the attenuation is",h["PowerAtten"].value,
    "the display is initially logarithmic",h["LogScaleEnab"].value)
print("setting to linear scale and 33 dB atten")
h["LogScaleEnab"].value = False
h["PowerAtten"].value = 33
n_points = int(h["DataRange"][1])
tune_data = {}
h["RefArm"].value = "On"
for mode_zoom in [1,2,4,8]:
    y_data = np.zeros(n_points)
    x_data = np.linspace(-0.5/mode_zoom,0.5/mode_zoom,n_points)
    h['ModeZoom'].value = mode_zoom
    time.sleep(2.0)
    print("capture now...")
    for i in range(0, n_points):
        y_data[i] += h["Data"][i]
    tune_data['y%d'%mode_zoom] = y_data
    tune_data['x%d'%mode_zoom] = x_data

tune_data_hpnoref = {}
h["RefArm"].value = "Off"
h["PowerAtten"].value = 20
time.sleep(2.0) # takes longer to turn up power
for mode_zoom in [1,2,4,8]:
    y_data = np.zeros(n_points)
    x_data = np.linspace(-0.5/mode_zoom,0.5/mode_zoom,n_points)
    h['ModeZoom'].value = mode_zoom
    time.sleep(2.0)
    print("capture now...")
    for i in range(0, n_points):
        y_data[i] += h["Data"][i]
    tune_data_hpnoref['y%d'%mode_zoom] = y_data
    tune_data_hpnoref['x%d'%mode_zoom] = x_data
h["RefArm"].value = "On"

for thisdata in (tune_data,tune_data_hpnoref):
    plt.figure()
    for mode_zoom in [1,2,4,8]:
        y_data = thisdata['y%d'%mode_zoom]
        x_data = thisdata['x%d'%mode_zoom]
        plt.plot(x_data,y_data,'o', alpha=0.5, label='zoom level %d'%mode_zoom)
    plt.legend()
plt.show()
