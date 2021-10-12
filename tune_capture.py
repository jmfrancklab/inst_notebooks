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
y_data = np.zeros(n_points)
for i in range(0, n_points):
    y_data[i] += h["Data"][i]
plt.plot(y_data)
plt.show()
