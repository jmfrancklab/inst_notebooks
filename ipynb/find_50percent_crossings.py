
# coding: utf-8

# 


get_ipython().magic(u'pylab inline')


# 


x = r_[-10:10:100j]
gauss = 1-exp(-x**2/2)
plot(x,gauss)
ylim(0,1.1)
axhline(y=0.5)
crossovers = diff(gauss < 0.5) 
plot(x[:-1],crossovers)
# find the two points where I cross the 50% line
x_crossings = x[argwhere(diff(gauss<0.5))].flatten()
plot(x_crossings,r_[0.5,0.5],'o')


# 




