"""
started from Eli Bendersky (eliben@gmail.com), updated
by Ondrej Holesovsky.  License: this code is in the
public domain.

then use this:
https://www.pythonguis.com/tutorials/pyqt-layouts/
which is a good layout reference

JF updated to plot a sine wave
"""
import Instruments
import Instruments.power_control_server
from Instruments import Bridge12
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

class TuningWindow(QMainWindow):
    def __init__(self, B12, myconfig, parent=None):
        self.B12 = B12
        self.myconfig = myconfig
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('B12 tuning!')
        self.setGeometry(20,20,1500,800)

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self._already_fmode = False
        self.line_data = []
        self.x = []
        self.timer = QTimer()
        self.fmode = False
        self.timer.setInterval(100) #.1 seconds
        self.timer.timeout.connect(self.opt_update_frq)
        self.timer.start(1000)
        self.on_recapture()
        #self._n_times_run = 0
    def opt_update_frq(self):
        # if I'm in frequency mode, then update and redraw
        # if not, don't do anything
        if self.fmode:
            self.dip_frq_GHz = self.B12.get_freq() / 1e9
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
         (or click "Re-Capture")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    
    def set_default_choices(self):
        self.myconfig['HP_power'] = 2.0

    def orig_zoom_limits(self):
        for ini_val, w in [('9810000',self.textbox1),
                ('9830000',self.textbox2)]:
            w.setText(ini_val)
            w.setMinimumWidth(8)
            w.editingFinished.connect(self.on_textchange)
            self.textboxes_vbox.addWidget(w)
        return
    def on_zoomclicked(self):
        self._curzoomclicked = (str(self.slider_min.value()), str(self.slider_max.value()))
        if (hasattr(self,'_prevzoomclicked') and
                self._prevzoomclicked ==
                self._curzoomclicked
                ):
            self.orig_zoom_limits()
            self.on_textchange()
            del self._prevzoomclicked
            return
        self.textbox1.setText(self._curzoomclicked[0])
        self.textbox2.setText(self._curzoomclicked[1])
        self.on_textchange()
        self._prevzoomclicked = self._curzoomclicked
        return
    def on_textchange(self):
        self.left_slider_lim = int(self.textbox1.text())
        self.right_slider_lim = int(self.textbox2.text())
        if self.right_slider_lim < self.left_slider_lim:
            self.right_slider_lim = self.left_slider_lim+1
            self.textbox1.setText(str(self.left_slider_lim))
            self.textbox2.setText(str(self.right_slider_lim))
        for w in [
                self.slider_min,
                self.slider_max]:
            w.setRange(self.left_slider_lim,
                    self.right_slider_lim) # requires integers!
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
        self.B12.set_power(self.myconfig['HP_power'])
        temp, tx = self.B12.freq_sweep(self.x[-1]*1e3)
        self.line_data.append(temp)
        if hasattr(self,'interpdata'):
            del self.interpdata
            del self.dip_frq_GHz
        return
    def on_recapture(self):
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
                self.B12.set_freq(self.dip_frq_GHz*1e9)
                self._already_fmode = True
            #    if hasattr(self, 'frq_log'):
            #        del self.frq_log
            #        del self.rx_log
            #    self.twin_ax = self.axes.twinx()
            #    self.frq_log = []
            #    self.time_log = []
            #    self.rx_log = []
            #self.frq_log.append(self.B12.freq_int())
            #self.rx_log.append(self.B12.rxpowermv_float())
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
            self.axes.set_xlabel(r'$\nu_{B12}$ / GHz')
            self.axes.set_ylabel(r'Rx / mV')
            self.axes.axvline(x=dip_frq_GHz, ls='--', c='r')
            self.B12.set_freq(dip_frq_GHz*1e9) # always do this, so that it should be safe to slightly turn up the power
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
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Other GUI controls
        # 
        # {{{ text boxes control slider limits
        self.textboxes_vbox = QVBoxLayout()
        self.textbox1 = QLineEdit()
        self.textbox2 = QLineEdit()
        self.orig_zoom_limits()
        # }}}
        
        # {{{ buttons
        self.button_vbox = QVBoxLayout()
        self.draw_button = QPushButton("&Re-Capture")
        self.combo_power = QComboBox()
        self.combo_power.addItem("low power")
        self.combo_power.addItem("medium power")
        self.combo_power.addItem("high power")
        self.combo_power.activated[str].connect(self.power_changed)
        self.set_default_choices()
        self.textboxes_vbox.addWidget(self.combo_power)
        self.draw_button.clicked.connect(self.on_recapture)
        self.button_vbox.addWidget(self.draw_button)
        self.zoom_button = QPushButton("&Zoom Limits")
        self.zoom_button.clicked.connect(self.on_zoomclicked)
        self.button_vbox.addWidget(self.zoom_button)
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
        for ini_val,w in [(9810000,self.slider_min),
                (9830000,self.slider_max)]:#these values MUST match the values on line 84
            self.on_textchange()
            w.setValue(ini_val)
            w.setTracking(True)
            w.setTickPosition(QSlider.TicksBothSides)
            w.valueChanged.connect(self.regen_plots)
            self.slider_vbox.addWidget(w)
        # }}}
        
        # {{{ Layout with box sizers
        hbox = QHBoxLayout()
        hbox.addLayout(self.boxes_vbox)
        hbox.addLayout(self.textboxes_vbox) # requires a different command!
        hbox.addLayout(self.button_vbox) # requires a different command!
        hbox.addLayout(self.boxes_vbox) # requires a different command!
        for w in [  slider_label]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
        hbox.addLayout(self.slider_vbox) # requires a different command!
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        # }}}
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    def power_changed(self,arg):
        my_power = {"low power":2.0,
                "medium power": 8.0,
                "high power": 10.0}
        self.myconfig['HP_power'] = my_power[arg]
        print("changing power to",self.myconfig['HP_power'])

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
    with Bridge12() as b:
        b.set_wg(True)
        b.set_rf(True)
        b.set_amp(True)
        time.sleep(5)
        #print(myconfig['HP_power'])
        #b.set_power(myconfig['HP_power'])
        tunwin = TuningWindow(b,myconfig)
        tunwin.show()
        app.exec_()
        final_frq = b.get_freq()
    print("dip found at",final_frq)
    myconfig["uw_dip_center_GHz"] = final_frq / 1e9
    myconfig["carrierFreq_MHz"] = myconfig["uw_dip_center_GHz"]*myconfig["guessed_MHz_to_GHz"]
    myconfig.write()
