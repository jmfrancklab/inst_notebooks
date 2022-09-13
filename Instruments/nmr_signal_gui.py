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
    def __init__(self, xepr, parent=None):
        self.xepr = xepr
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('NMR signal finder')
        self.setGeometry(20,20,1500,800)

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        self.phcyc = 4
        self.npts = 2**14/self.phcyc

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
        print("slider min",
                self.slider_min.value(),
                "slider max",
                self.slider_max.value())
        if len(self.line_data) > 6:
            self.line_data.pop(0)
            self.x.pop(0)
        self.x.append(np.r_[
                self.slider_min.value():
                self.slider_max.value():
                15j])
        temp, tx = self.xepr.freq_sweep(self.x[-1]*1e3)
        self.line_data.append(temp)
        if hasattr(self,'interpdata'):
            del self.interpdata
            del self.dip_frq_GHz
        return
    def acq_NMR(self):
        self.generate_data()
        self.regen_plots()
        return
    def regen_plots(self):
        """ Redraws the figure
        """
        self.fmode = self.fmode_cb.isChecked()
        self.axes.clear()        
        # clear the axes and redraw the plot anew
        self.axes.grid(self.grid_cb.isChecked())
        if self.fmode:
            if not self._already_fmode:
                self.xepr.set_freq(self.dip_frq_GHz*1e9)
                self._already_fmode = True
            #    if hasattr(self, 'frq_log'):
            #        del self.frq_log
            #        del self.rx_log
            #    self.twin_ax = self.axes.twinx()
            #    self.frq_log = []
            #    self.time_log = []
            #    self.rx_log = []
            #self.frq_log.append(self.xepr.freq_int())
            #self.rx_log.append(self.xepr.rxpowermv_float())
            #self.axes.plot(self.frq_log)
            #self.twin_ax.plot(self.rx_log)
            #time.sleep(0.1)
            self.axes.text(
                    0.1,0.5,
                    f"entered frequency mode with {self.dip_frq_GHz:0.6f} GHz",
                    transform=self.axes.transAxes)
            self.canvas.draw()
        else:
            self._already_fmode = False
            for j in range(len(self.line_data)):
                self.axes.plot(self.x[j]/1e6,self.line_data[j],'o-',
                        alpha=0.5*(j+1)/len(self.line_data))
            # {{{ for the last trace, interpolate, and find the min
            if hasattr(self, 'interpdata'):
                xx, yy = self.interpdata
                dip_frq_GHz = self.dip_frq_GHz
            else:
                x,y = self.x[-1], self.line_data[-1]
                minidx = np.argmin(y)
                zoomidx = np.r_[minidx-2:minidx+3]
                print("1 zoomidx",zoomidx)
                zoomidx = zoomidx[zoomidx < len(x)]
                print("2 zoomidx",zoomidx)
                zoomidx = zoomidx[zoomidx > 0]
                print("3 zoomidx",zoomidx)
                if len(zoomidx) > 3:
                    whichkind = 'cubic'
                elif len(zoomidx) > 2:
                    whichkind = 'quadratic'
                else:
                    whichkind = 'linear'
                f = interp1d(x[zoomidx], y[zoomidx], kind=whichkind)
                xx = np.linspace(x[zoomidx[0]],
                        x[zoomidx[-1]], 100)
                yy = f(xx)
                dip_frq_GHz = xx[np.argmin(yy)]/1e6
                self.interpdata = xx, yy
                self.dip_frq_GHz = dip_frq_GHz
                # }}}
            self.axes.plot(xx/1e6, yy, 'r', alpha=0.5)
            self.axes.set_xlabel(r'$\nu_{xepr}$ / GHz')
            self.axes.set_ylabel(r'Rx / mV')
            self.axes.axvline(x=dip_frq_GHz, ls='--', c='r')
            self.xepr.set_freq(dip_frq_GHz*1e9) # always do this, so that it should be safe to slightly turn up the power
            self.axes.set_xlim(self.slider_min.value()/1e6,
                    self.slider_max.value()/1e6)
            self.canvas.draw()
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
        tunwin = NMRWindow(x)
    tunwin.show()
    app.exec_()
    myconfig.write()
