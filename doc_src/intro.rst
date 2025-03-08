This repo is very much focused on the instrumentation aspect of our lab (e.g., Instek oscilloscope, Instek frequency generator, HP microwave Frequency source, Bridge12, Gigatronics power meter). A primary server 'FLInst' acts as the glue between all instruments for user friendly integration. 

FLInst
======
This package includes a power control server that acts as an integral communication between instrumentation as well as between the computer running SpinCore and the computer running XEPR for seamless acquisition. The FLInst allows the user to set desired fields, initiate communication between instruments, as well as initiating several GUI programs for streamlining the acquisition process.

The GUIs
========
We are slowly implementing GUIs for simple, fast and user friendly methods of getting on NMR resonance, as well as minimizing the reflection of the microwaves by adjusting the iris screw. 
FLInst MWtune
-------------
Using the command 'FLInst MWtune' the HP powersource is started up, and the reflection of the microwaves is recorded on an easy to read plot. The user can then zoom in on frequencies of interest and recapture. Specifically, our lab will capture the reflection at increasing powers (all with the click of a button) and adjust the iris screw to minimize the reflection at the higher powers.
FLInst NMRsignal
----------------
We also have implemented a GUI for getting on NMR resonance using the command 'FLInst NMRsignal'. This command initiates communication between the computer running XEPR and instructs the proper field be set utilizing acquisition parameters from your configuration file (See SpinCore_apps repo for more details). The GUI will automatically phase cycle, and find the signal peak on a 1D plot of the signal. Once found the GUI sends the necessary adjustments to the configuration file so that on the next acquisition ('acquire NMR' button) the signal will be on resonance. There is a drop down menu for the user to adjust the spectral width to set values of 200, 24 and 3.9 kHz. The user will notice that at zoomed in spectral widths they can clearly discern the different coherence transfer pathways, the average signal, as well as the std of the noise, allowing access to further information that typically would not be seen.
.. toctree::

    auto_examples/index

