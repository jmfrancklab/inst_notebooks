from pyspecdata import *
import matplotlib as mpl
from matplotlib.pylab import text
from matplotlib.tri import Triangulation, TriAnalyzer, UniformTriRefiner

font = {'family' : 'sans-serif',
        'sans-serif' : 'Times New Roman',
        'weight' : 'normal',
        'size'   : 30}
mpl.rc('font', **font)
rcParams['mathtext.fontset'] = 'cm'

filename = '190610_Katie_drift_test_oil_34dBm_iris'
data = load(getDATADIR(exp_type='test_equip')+filename+'.npz')
f_axis = data[data.files[0]]
rx_axis = data[data.files[1]]
t_axis = data[data.files[2]]
print f_axis
stop_index = where(rx_axis==180)
print "shape of t_axis",shape(t_axis)
# DO NOT index multi-dimensional arrays using a single index -- it creates code that is very hard to read
# I believe this is till a problem in places below, and should be fixed.
# e.g. t_axis[j,:] NEVER t_axis[j] -- this way the reader can jump in and know what dimensionality the code is
figure(figsize=(15,5),
        facecolor=(1,1,1,0))
ax = axes(#frameon=False,
        facecolor=(1,1,1,0.5))
#ax.set_alpha(0.5)

for x in r_[0:len(f_axis)]:
    plot(t_axis[x,:len(t_axis[1])-1],rx_axis[x,:len(t_axis[1])-1]/10.,'o-',label='%0.7f GHz'%(f_axis[x]*1e-9))
fs = filename.split('_')
substance = [j.capitalize()
        for j in fs
        if j.lower() in ['air','oil']
        ]
assert len(substance) == 1
substance = substance[0]
power = [j[:-3]
        for j in fs
        if j[-3:].lower() == 'dbm'
        ]
assert len(power) == 1
power = power[0]
title(substance+' at '+power+' dBm')
xlabel('time (sec)')
ylabel('receiver (mV)')
grid();legend();
lg = legend(**dict(bbox_to_anchor=(1.05,1), loc=2, borderaxespad=0.))
lg.set_alpha(0.5)
savefig(filename+'.png',
        dpi=300,bbox_inches='tight',
        facecolor=(1,1,1,0),
        )
# {{{ generate the surface plot using fancy methods for a nice plot
# creates the Delauney meshing
tri_x = t_axis.ravel()
tri_y = (f_axis[:,newaxis]*ones_like(t_axis)).ravel()
tri = Triangulation(tri_x,
        tri_y)
tri_z = rx_axis.ravel()
# {{{ refining the data -- see https://matplotlib.org/3.1.0/gallery/images_contours_and_fields/tricontour_smooth_delaunay.html#sphx-glr-gallery-images-contours-and-fields-tricontour-smooth-delaunay-py
#     I don't see a difference in the refined vs. unrefined, but I'm quite possibly missing something
refiner = UniformTriRefiner(tri)
subdiv = 3  # Number of recursive subdivisions of the initial mesh for smooth
            # plots. Values >3 might result in a very high number of triangles
            # for the refine mesh: new triangles numbering = (4**subdiv)*ntri
tri_refi, tri_z_refi = refiner.refine_field(tri_z, subdiv=subdiv)
# }}}
figure(figsize=(15,5),
        facecolor=(1,1,1,0))
plot(tri_x,tri_y,'o',
        color='k',alpha=0.3)
triplot(tri,
        color='k',alpha=0.3)
tricontourf(tri,tri_z,
        levels=linspace(tri_z.min(),tri_z.max(),100)
        )
ylabel('frequency')
xlabel('time')
title('unrefined')
# now show refined
figure(figsize=(15,5),
        facecolor=(1,1,1,0))
plot(tri_x,tri_y,'o',
        color='k',alpha=0.3)
triplot(tri,
        color='k',alpha=0.3)
tricontourf(tri,tri_z,
        levels=linspace(tri_z.min(),tri_z.max(),100)
        )
ylabel('frequency')
xlabel('time')
title('refined')
# }}}
show()
