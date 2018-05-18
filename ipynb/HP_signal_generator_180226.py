
# coding: utf-8

# In[1]:

from Instruments import HP8672A

# This next block is how I found the correct GPIB address (set a frequency that matches the address)

# In[ ]:

for j in range(50):
    testaddr = j+1
    with hp8672a(gpibaddress=testaddr) as h:
        h.set_frequency(10e9+0.1e9*testaddr)

# Note that the manual makes it seem like there might be a different address for receiving info from the instrument, but I also didn't find any info about commands where you can get it to speak to you. 

# In[3]:

with HP8672A(gpibaddress=19) as h:
    h.set_frequency(9.2e9)


# In[4]:

with HP8672A(gpibaddress=19) as h:
    h.set_power(-40)


# In[ ]:

import socket


# In[ ]:

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)


# In[ ]:

s.connect(('jmfrancklab-prologix.syr.edu',1234))


# In[ ]:

s.send('++ver\r')
import StringIO
buff = StringIO.StringIO(2048)          # Some decent size, to avoid mid-run expansion
while True:
    data = s.recv(2048)                  # Pull what it can
    buff.write(data)                    # Append that segment to the buffer
    if '\n' in data or '\r' in data: break              # If that segment had '\n', break

# Get the buffer data, split it over newlines, print the first line
print buff.getvalue().splitlines()[0]


# In[ ]:



