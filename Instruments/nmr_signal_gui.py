"""
started from Eli Bendersky (eliben@gmail.com), updated
by Ondrej Holesovsky.  License: this code is in the
public domain.

then use this:
https://www.pythonguis.com/tutorials/pyqt-layouts/
which is a good layout reference

JF updated to plot a sine wave
"""
from .XEPR_eth import xepr as xepr_from_module
from scipy.interpolate import interp1d
import time
import sys, os, random
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import SpinCore_pp # just for config file, but whatever...

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import numpy as np

class NMRWindow(QMainWindow):
    def __init__(self, xepr, myconfig, parent=None):
        self.xepr = xepr
        self.myconfig = myconfig
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('NMR signal finder')
        self.setGeometry(20,20,1500,800)

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        self.nPhaseSteps = 4
        self.npts = 2**14/self.nPhaseSteps

        self._already_fmode = False
        self.line_data = []
        self.x = []
        self.timer = QTimer()
        self.fmode = False
        self.timer.setInterval(100) #.1 seconds
        self.timer.timeout.connect(self.opt_update_frq)
        self.timer.start(1000)
        self.acq_NMR()
        #self._n_times_run = 0
    def opt_update_frq(self):
        # if I'm in frequency mode, then update and redraw
        # if not, don't do anything
        if self.fmode:
            self.dip_frq_GHz = self.xepr.get_freq() / 1e9
            self.regen_plots()
    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path, ext = QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices)
        path = path.encode('utf-8')
        if not path[-4:] == file_choices[-4:].encode('utf-8'):
            path += file_choices[-4:].encode('utf-8')
        if path:
            self.canvas.print_figure(path.decode(), dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:
        
         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter
         (or click "Acquire NMR")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    
    def set_default_choices(self):
        self.textbox_apo.setText("10 ms")
        self.textbox_apo.setMinimumWidth(10)
        self.SW = 200
    def on_zoomclicked(self):
        self._curzoomclicked = (str(self.slider_min.value()), str(self.slider_max.value()))
        if (hasattr(self,'_prevzoomclicked') and
                self._prevzoomclicked ==
                self._curzoomclicked
                ):
            self.set_default_choices()
            self.on_textchange()
            del self._prevzoomclicked
            return
        self.textbox_apo.setText(self._curzoomclicked[0])
        self.combo_sw.setText(self._curzoomclicked[1])
        self.on_textchange()
        self._prevzoomclicked = self._curzoomclicked
        return
    def on_textchange(self):
        print("you changed your apodization
                to",self.textbox_apo.text(),
                "but I'm not yet programmed to do anything about that!")
        return

    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        
        QMessageBox.information(self, "Click!", msg)
    
    def generate_data(self):
        #{{{let computer set field
        print("I'm assuming that you've tuned your probe to",
                self.myconfig['carrierFreq_MHz'],
                "since that's what's in your .ini file")
        Field = self.myconfig['carrierFreq_MHz']/self.myconfig['gamma_eff_MHz_G']
        print("Based on that, and the gamma_eff_MHz_G you have in your .ini file, I'm setting the field to %f"%Field)
        assert Field < 3700, "are you crazy??? field is too high!"
        assert Field > 3300, "are you crazy?? field is too low!"
        change_field = True
        if self.xepr.exp_has_been_run:# in independent script, this isn't going to be true, because we spin up a new xepr object each time
            print("yes, xepr has been run")
            prev_field = self.xepr.get_field()
            if abs(prev_field-Field) < 0.02:# 0.02 G is about 85 Hz
                change_field = False
        if change_field:
            Field = self.xepr.set_field(Field)
            print("field set to ",Field)
        else:
            print("it seems like you were already on resonance, so I'm not going to change the field")
        #}}}
        #{{{acquire echo
        self.echo_data = run_spin_echo(
                nScans=self.myconfig['nScans'],
                indirect_idx = 0,
                indirect_len = 1,
                adcOffset = self.myconfig['adc_offset'],
                carrierFreq_MHz = self.myconfig['carrierFreq_MHz'],
                nPoints = self.npts,
                nEchoes = self.myconfig['nEchoes'],
                p90_us = self.myconfig['p90_us'],
                repetition = self.myconfig['repetition_us'],
                tau_us = self.myconfig['tau_us'],
                SW_kHz = self.myconfig['SW_kHz'],
                output_name = filename,
                ret_data = None)
        #}}}
        #{{{setting acq_params
        self.echo_data.set_prop("postproc_type","proc_Hahn_echoph")
        self.echo_data.set_prop("acq_params",self.myconfig.asdict())
        #}}}
        #{{{ chunking
        self.echo_data.chunk('t',['ph1','t2'],[4,-1])
        self.echo_data.setaxis('ph1',r_[0.,1.,2.,3.]/4)
        if self.myconfig['nScans'] > 1:
            self.echo_data.setaxis('nScans',r_[0:self.myconfig['nScans']])
        self.echo_data.reorder(['ph1','nScans','t2'])
        self.echo_data.squeeze()
        self.echo_data.set_units('t2','s')
        #}}}    
        self.myconfig.write()
        return
    def acq_NMR(self):
        self.generate_data()
        self.regen_plots()
        return
    def regen_plots(self):
        """ Redraws the figure
        """
        self.echo_data.ft('ph1', unitary=True)
        print(ndshape(self.echo_data))
        if 'nScans' in self.echo_data.dimlabels:
            self.echo_data.mean('nScans')
        self.echo_data.ft('t2', shift=True)
        # {{{ show raw data with peak pick
        fl.next('raw ft')
        for j in self.echo_data.getaxis('ph1'):
            fl.plot(abs(self.echo_data['ph1':j]), label=f'Δp={j}', alpha=0.5)
        centerfrq = abs(self.echo_data['ph1',+1]).argmax('t2').item()
        axvline(x=centerfrq/1e3,ls=':',color='r',alpha=0.25)
        # }}}
        d_fullsw = self.echo_data.C
        fl.next('zoomed')
        for j in self.echo_data.getaxis('ph1'):
            fl.plot(abs(self.echo_data['ph1':j]['t2':tuple(r_[-3e3,3e3]+centerfrq)]), label=f'Δp={j}', alpha=0.5)
        noise = self.echo_data['ph1',r_[0,2,3]]['t2':centerfrq].run(std,'ph1')
        signal = abs(self.echo_data['ph1',1]['t2':centerfrq])
        self.echo_data = self.echo_data['t2':tuple(r_[-3e3,3e3]+centerfrq)]
        self.echo_data.ift('t2')
        fl.next('time domain, filtered')
        filter_timeconst = 10e-3
        myfilter = exp(-abs((self.echo_data.fromaxis('t2')-config_dict['tau_us']*1e-6))/filter_timeconst)
        for j in self.echo_data.getaxis('ph1'):
            fl.plot(abs(self.echo_data['ph1':j]), label=f'Δp={j}', alpha=0.5)
        fl.plot(myfilter*abs(self.echo_data['ph1',1]['t2':config_dict['tau_us']*1e-6]))
        # {{{ show filtered data with peak pick
        self.echo_data = d_fullsw
        self.echo_data.ift('t2')
        self.echo_data *= exp(-abs((self.echo_data.fromaxis('t2')-config_dict['tau_us']*1e-6))/filter_timeconst)
        self.echo_data.ft('t2')
        fl.next('apodized ft')
        for j in self.echo_data.getaxis('ph1'):
            fl.plot(abs(self.echo_data['ph1':j]), label=f'Δp={j}', alpha=0.5)
        centerfrq = abs(self.echo_data['ph1',+1]).argmax('t2').item()
        axvline(x=centerfrq/1e3,ls=':',color='r',alpha=0.25)
        # }}}
        if signal > 3*noise:
            Field = config_dict['carrierFreq_MHz'] / config_dict['gamma_eff_MHz_G']
            config_dict['gamma_eff_MHz_G'] -= centerfrq*1e-6/Field
            config_dict.write()
        else:
            print('*'*5 + "warning! SNR looks bad! I'm not adjusting γ!!!" + '*'*5) # this is not yet tested!
        print(fl)
        return
    def create_main_frame(self):
        self.main_frame = QWidget()
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        # {{{ need both of these to get background of figure transparent,
        #     rather than white
        self.fig.set_facecolor('none')
        self.canvas.setStyleSheet("background-color:transparent;")
        # }}}
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)
        # Bind the 'pick' event
        self.canvas.mpl_connect('pick_event', self.on_pick)
        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        # {{{ bottom left with SW, apo, and acquire
        #     button
        self.bottomleft_vbox = QVBoxLayout()
        self.textbox_apo = QLineEdit()
        self.combo_sw = QComboBox()
        self.combo_sw.addItem("200")
        self.combo_sw.addItem("24")
        self.combo_sw.addItem("3.9")
        self.combo_sw.activated[str].connect(self.SW_changed)
        self.set_default_choices()
        self.textbox_apo.editingFinished.connect(self.on_textchange)
        self.bottomleft_vbox.addWidget(self.textbox_apo)
        self.acquire_button = QPushButton("&Acquire NMR")
        self.acquire_button.clicked.connect(self.acq_NMR)
        self.bottomleft_vbox.addWidget(self.textbox_apo)
        # }}}
        # {{{ box to stack checkboxes
        self.boxes_vbox = QVBoxLayout()
        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.grid_cb.stateChanged.connect(self.regen_plots)
        self.boxes_vbox.addWidget(self.grid_cb)
        self.fmode_cb = QCheckBox("Const &Frq &Mode")
        self.fmode_cb.setChecked(False)
        self.fmode_cb.stateChanged.connect(self.regen_plots)
        self.boxes_vbox.addWidget(self.fmode_cb)
        # }}}
        slider_label = QLabel('Bar width (%):')
        # {{{ box to stack sliders
        self.slider_vbox = QVBoxLayout()
        self.slider_vbox.setContentsMargins(0, 0, 0, 0)
        #self.slider_vbox.setSpacing(0)
        self.slider_min = QSlider(Qt.Horizontal)
        self.slider_max = QSlider(Qt.Horizontal)
        for ini_val,w in [(9819000,self.slider_min),
                (9825000,self.slider_max)]:
            self.on_textchange()
            w.setValue(ini_val)
            w.setTracking(True)
            w.setTickPosition(QSlider.TicksBothSides)
            w.valueChanged.connect(self.regen_plots)
            self.slider_vbox.addWidget(w)
        # }}}
        # {{{ we stack the bottom vboxes side by side
        bottom_hbox = QHBoxLayout()
        bottom_hbox.addLayout(self.bottomleft_vbox)
        bottom_hbox.addLayout(self.boxes_vbox)
        bottom_hbox.addWidget(slider_label)
        bottom_hbox.setAlignment(slider_label, Qt.AlignVCenter)
        bottom_hbox.addLayout(self.slider_vbox) # requires a different command!
        # }}}
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(self.mpl_toolbar)
        main_layout.addLayout(bottom_hbox)
        self.main_frame.setLayout(main_layout)
        self.setCentralWidget(self.main_frame)
    
    def SW_changed(self,arg):
        my_sw = {"200":200.0,
                "24":24.0,
                "3.9":3.9}
        self.SW = my_sw[arg]
        print("changing SW to",self.SW)

    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

def main():
    myconfig = SpinCore_pp.configuration("active.ini")
    app = QApplication(sys.argv)
    with xepr_from_module as x:
        tunwin = NMRWindow(x,myconfig)
    tunwin.show()
    app.exec_()
    myconfig.write()
