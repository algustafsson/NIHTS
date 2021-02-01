""" NIHTS GUI - NIHTS Exposure Control
    v1.16: 2020-12-07, ag765@nau.edu, A Gustafsson
    Creating NIHTS GUI to avoid scripting. Using PyQt5.
    
    All scripts are copy and pasted into their calls. See comments within script.
    
    ** CURRENT NIHTS VERSION
    Runs with NIHTS Scripts in GUI
    
    To use, enter on the command line in the ipython environment:
    run -i NIHTS_GUI.py
    
    UPDATES:
    - Don't send nan for any buttons
    - Reconfigure NIHTS Panel -> add general Nod script
    - put in checks for sending command 2x

    - Fix scripts to be external
    
    - Terminal Line Toggles on but not off
    - write terminal line script section
    
    - Add save_n feature to ABBA script - currently saving every xcam image
    - * Add status bar
    
    - * set up logging so that it goes in the correct data folder --> logging currently on mac mini desktop
    - create separate log of information from terminal window
        
    NEEDS TESTING:
        - Focus script
        - LMI Mapping Tab
        - NIHTS Shutdown Tab
    
    """

import sys
import os
import os.path
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import argparse
import numpy as np
import time
import datetime as dt
import wx

from astropy.io import fits
import shutil
import glob
import math
import random
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

###############################################

import logging
logger = logging.getLogger(__name__)

###############################################

##
# NIHTS STARTUP SCRIPT
##
from xenics import XenicsCamera
x = XenicsCamera()
# COMMENT 180611: currently need to confirm that camera is powered on at this step
x.set_gain(False)
x.go(1.0, 1, 1, return_images=False)
from xenics import TCS
#from xenics import AOS #Added by AG 01/14/21
from xenics import NIHTS
tcs = TCS()
#aos = AOS()  #Added by AG 01/14/21
nihts = NIHTS()

###############################################

state_0 = []
state_1 = []
state_2 = []
state_3 = []
state_4 = []
state_5 = []
state_6 = []
state_7 = []
state_8 = []

XPosCurrent = []
YPosCurrent = []

ExpFTime = []
FOffset = []

FilterCurrent = []
CommandCurrent = []
StepCurrent = []

CurrentSlit = []
CurrentSlitPos = []

XExpTimeCurrent = []
CoaddsCurrent = []

XPosLMICurrent = []
YPosLMICurrent = []

XPosLMIDesired = []
YPosLMIDesired = []

CurrentBinning = []

TargetCurrent = []
NExpTimeCurrent = []
GuidingCurrent = []
NnseqCurrent = []
OffsetCurrent = []
DirCurrent = []

curr_text = []


###############################################

class QtHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
    def emit(self, record):
        record = self.format(record)
        if record: XStream.stdout().write('%s\n'%record)

logger = logging.getLogger(__name__)
handler = QtHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(asctime)s: %(lineno)d: %(message)s"))
FORMAT = "%(levelname)s: %(asctime)s: %(lineno)d: %(message)s"
logger.addHandler(handler)

###############################################


class XStream(QObject):
    _stdout = None
    _stderr = None
    messageWritten = pyqtSignal(str)
    def flush( self ):
        pass
    def fileno( self ):
        return -1
    def write( self, msg ):
        if ( not self.signalsBlocked() ):
            self.messageWritten.emit(unicode(msg))

    @staticmethod
    def stdout():
        if ( not XStream._stdout ):
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout
    
    @staticmethod
    def stderr():
        if ( not XStream._stderr ):
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr


###############################################

class NIHTS(QMainWindow):
    
    def __init__(self):
        super(NIHTS, self).__init__()
        self.title = 'NIHTS'
        self.left = 0
        self.top = 0
        self.width = 850
        self.height = 400
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.nihts_widget = NIHTSWidget(self)
        self.setCentralWidget(self.nihts_widget)
        
        self.show()

class NIHTSWidget(QWidget):

    def __init__(self, parent):
        
        ##
        # Load Scripts
        ##
        def run_Exit(self):
            logging.info('Request to Close GUI...')
            infoBox = QMessageBox()
            infoBox.setText("Are you sure you want to exit?")
            infoBox.setWindowTitle("Exit GUI")
            infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
            infoBox.setEscapeButton(QMessageBox.Close)
            result = infoBox.exec_()
            if result == QMessageBox.Yes:
                logging.info('--- FINISHED ---')
                app.quit()
            else:
                logging.info('... Not ready to close GUI')
    
        def run_open_xcam(self):
            logging.info('Open Camera')
            
            x.open_camera()
    
        def run_NIHTS_Arcs(self):
            focus_filter = str(FilterCurrent[-1])
            filter_list = ['OPEN','B','V','R','VR','SDSSg','SDSSr','SDSSi','OIII','Ha_on','Ha_off','WC','WN','CT','BC','GC','RC']
            filter = filter_list[int(focus_filter)]
            
            if filter=='OPEN':
                dichroic = 239.95
                offset = 0
            elif filter=='B':
                dichroic = 238.76
                offset = 105
            elif filter=='V':
                dichroic = 238.76
                offset = 105
            elif filter=='R':
                dichroic = 238.36
                offset = 140
            elif filter=='VR':
                dichroic = 237.84
                offset = 185
            elif filter=='SDSSg':
                dichroic = 237.90
                offset = 180
            elif filter=='SDSSr':
                dichroic = 237.90
                offset = 180
            elif filter=='SDSSi':
                dichroic = 237.90
                offset = 180
            elif filter=='OIII':
                dichroic = 237.62
                offset = 205
            elif filter=='Ha_on':
                dichroic = 238.19
                offset = 155
            elif filter=='Ha_off':
                dichroic = 238.19
                offset = 155
            elif filter=='WC':
                dichroic = 238.07
                offset = 165
            elif filter=='WN':
                dichroic =  238.13
                offset = 160
            elif filter=='CT':
                dichroic = 238.01
                offset = 170
            elif filter=='BC':
                dichroic = 237.96
                offset = 175
            elif filter=='GC':
                dichroic = 237.96
                offset = 175
            elif filter=='RC':
                dichroic = 237.96
                offset = 175
            
            infoBox = QMessageBox()
            infoBox.setText("Ask the TO to move the dichroic position to %smm ... Ready?" % dichroic)
            infoBox.setWindowTitle("Arcs Setup")
            infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
            infoBox.setEscapeButton(QMessageBox.Close)
            result = infoBox.exec_()
            if result == QMessageBox.Yes:
                logging.info('Arcs Sequence Begin...')
            
                ##
                # NIHTS_arcs_v3.py
                ##
                """ NIHTS arcs - Take ARCS.
                    v1.3: 2018-04-12, ag765@nau.edu, A Gustafsson
                
                    turn on arc lamp, take 5 arc images with 120 second exposures, and turn lamp back off and take one 120 sec No Lamps exposure. turn on arc lamp, take 3 arc images with 20 second exposures, and turn lamp back off and take one 20 sec No Lamps exposure. Inputs frame type and slit information into headers.
                
                    uses the editted version of nihts.go
                
                    ** GUI Version -- Needs testing
                
                    To use, enter on the command line:
                    python NIHTS_arcs.py
                
                    updates:
                    """
                import time
            
                print('Turning Xenon Lamp ON')
                subprocess.call("pwrusb setone 3 1", shell=True) #lamp on
                subprocess.call("pwrusb status", shell=True)

                print('-----Starting Arc Lamp Sequence 120-s -----')
                
                nihts.go(nexp=5, exptime=120, target='Comparison', frame_type='comparison', comment1='Slit: None, Position: None', aborterror=False)
                nihts.wait4nihts()
                
                print('-----Starting Arc Lamp Sequence 20-s -----')
                
                nihts.go(nexp=3, exptime=20, target='Comparison', frame_type='comparison', comment1='Slit: None, Position: None', aborterror=False)
                nihts.wait4nihts()

                print('-----Arc Lamp ON Sequence Complete -----')

                # Turn off Arc lamp
                print('Turning Xenon Lamp OFF')
                subprocess.call("pwrusb setone 3 0", shell=True) #lamp off
                subprocess.call("pwrusb status", shell=True)

                print('-----Starting No Lamp Sequence 120-s -----')

                nihts.go(nexp=1, exptime=120, target='Comparison - No Lamps', frame_type='comparison', comment1='Slit: None, Position: None', aborterror=False)
                
                nihts.wait4nihts()
                
                print('-----Starting No Lamp Sequence 20-s -----')
                
                nihts.go(nexp=1, exptime=20, target='Comparison - No Lamps', frame_type='comparison', comment1='Slit: None, Position: None', aborterror=False)
                
                nihts.wait4nihts()
                
                print('-----No Lamp Sequence Complete -----')

                ##
                #
                ##
                
                logging.info('... Arcs Sequence End')
            else:
                print("Ask the TO to move the dichroic position to %smm and try again." % dichroic)


        def run_NIHTS_Arcs_short(self):
            focus_filter = str(FilterCurrent[-1])
            filter_list = ['OPEN','B','V','R','VR','SDSSg','SDSSr','SDSSi','OIII','Ha_on','Ha_off','WC','WN','CT','BC','GC','RC']
            filter = filter_list[int(focus_filter)]
            
            if filter=='OPEN':
                dichroic = 239.95
                offset = 0
            elif filter=='B':
                dichroic = 238.76
                offset = 105
            elif filter=='V':
                dichroic = 238.76
                offset = 105
            elif filter=='R':
                dichroic = 238.36
                offset = 140
            elif filter=='VR':
                dichroic = 237.84
                offset = 185
            elif filter=='SDSSg':
                dichroic = 237.90
                offset = 180
            elif filter=='SDSSr':
                dichroic = 237.90
                offset = 180
            elif filter=='SDSSi':
                dichroic = 237.90
                offset = 180
            elif filter=='OIII':
                dichroic = 237.62
                offset = 205
            elif filter=='Ha_on':
                dichroic = 238.19
                offset = 155
            elif filter=='Ha_off':
                dichroic = 238.19
                offset = 155
            elif filter=='WC':
                dichroic = 238.07
                offset = 165
            elif filter=='WN':
                dichroic =  238.13
                offset = 160
            elif filter=='CT':
                dichroic = 238.01
                offset = 170
            elif filter=='BC':
                dichroic = 237.96
                offset = 175
            elif filter=='GC':
                dichroic = 237.96
                offset = 175
            elif filter=='RC':
                dichroic = 237.96
                offset = 175
            
            infoBox = QMessageBox()
            infoBox.setText("Ask the TO to move the dichroic position to %smm ... Ready?" % dichroic)
            infoBox.setWindowTitle("Arcs Setup")
            infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
            infoBox.setEscapeButton(QMessageBox.Close)
            result = infoBox.exec_()
            if result == QMessageBox.Yes:
                logging.info('Arcs Short Sequence Begin...')

                ##
                # NIHTS_arcs_short_v0.py
                ##
                """ NIHTS arcs - Take ARCS.
                    v1.0: 2018-08-29, ag765@nau.edu, A Gustafsson
                    
                    turn on arc lamp, take 3 arc images with 20 second exposures, and turn lamp back off and take one 20 sec No Lamps exposure.
                    
                    uses the editted version of nihts.go
                    
                    ** GUI Version -- Needs testing
                    
                    To use, enter on the command line:
                    python NIHTS_arcs_short.py
                    
                    updates:
                    """
                
                import time
                
                print('Turning Xenon Lamp ON')
                subprocess.call("pwrusb setone 3 1", shell=True) #lamp on
                subprocess.call("pwrusb status", shell=True)
                
                print('-----Starting Arc Lamp Sequence 20-s -----')
                
                nihts.go(nexp=3, exptime=20, target='Comparison', frame_type='comparison', comment1='Slit: None, Position: None', aborterror=False)
                nihts.wait4nihts()
                
                print('-----Arc Lamp ON Sequence Complete -----')
                
                # Turn off Arc lamp
                print('Turning Xenon Lamp OFF')
                subprocess.call("pwrusb setone 3 0", shell=True) #lamp off
                subprocess.call("pwrusb status", shell=True)
                
                print('-----Starting No Lamp Sequence 20-s -----')
                
                nihts.go(nexp=1, exptime=20, target='Comparison - No Lamps', frame_type='comparison', comment1='Slit: None, Position: None', aborterror=False)
                
                nihts.wait4nihts()
                
                print('-----No Lamp Sequence Complete -----')
                
                ##
                #
                ##
                
                logging.info('... Arcs Short Sequence End')
            else:
                print("Ask the TO to move the dichroic position to 237.9mm and try again.") ##Fix this

        
        def run_NIHTS_NTestImage(self):
            logging.info('NIHTS Test Exposure: 1 second')
            
            ##
            # NIHTS_NTestImage.py
            ##
            """ NIHTS Test - Take NIHTS Test Exposure
                v1.1: 2018-05-14, ag765@nau.edu, A Gustafsson
                
                ** GUI Version - Needs Testing
                
                updates:
                -
                
                """
    
            nihts.go(nexp=1, exptime=1, target='test', frame_type='object',  comment1 = 'Slit: None, Position: None', aborterror=False)

            ##
            #
            ##
        
        
        def run_NIHTS_Shutdown(self):
            logging.info('NIHTS Shutdown')
            
            ##
            # NIHTS_Shutdown.py
            ##
            """ NIHTS Shutdown - Turn off the NIHTS Camera
                v1.0: 2018-02-08, ag765@nau.edu, A Gustafsson
    
                Turn Off Arc Lamps
                Turn Off XCAM camera

                ** This is the current version!

                To use, enter on the command line:
                python NIHTS_Shutdown.py

                updates:
                """

            import subprocess

            subprocess.call("pwrusb setone 3 0", shell=True) #arc lamps off
            subprocess.call("pwrusb setone 1 0", shell=True) #xcam camera off
            subprocess.call("pwrusb status", shell=True)

            print('-----NIHTS Shutdown Complete-----')
            
            ##
            #
            ##

            
        def run_NIHTS_Home(self):
            logging.info('Target is at Home')
            
            ##
            # NIHTS_Home.py
            ##
            
            """ NIHTS Home - Declare Target is at home.
                v1.1: 2018-04-12, ag765@nau.edu, A Gustafsson
                
                ** GUI Version - Needs Testing
                
                updates:
                -
                
                """
    
            print('Target is at HOME Location')
    
            tcs.current_target_pt = tcs.home_pt
        
            ##
            #
            ##
            
        def run_NIHTS_ReturnHome(self):
            logging.info('Returning Target to Home Position')
            
            ##
            # NIHTS_ReturnHome.py
            ##
            
            """ NIHTS Return Home - Return Target to Home Location.
                v1.1: 2018-07-17, ag765@nau.edu, A Gustafsson
                
                ** GUI Version - Needs Testing
                
                updates:
                -
                
                """
            
            print('Return target to HOME Location')
            
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.home_pt)
        
        ##
        #
        ##


        def run_NIHTS_XFExp(self):
            logging.info('XCAM Exposure')
            
            ##
            # NIHTS_XFExp
            ##
            """ XCAM Exposure - Take XCAM Exposure
                v1.1: 2018-05-14, ag765@nau.edu, A Gustafsson
                
                ** GUI Version - Needs Testing
                
                updates:
                -
                
                """
            
            print('XCAM Exp Time', ExpFTime[-1])
            
            xtime = ExpFTime[-1]
            print(xtime)
            nihts.wait4nihts()
            x.go(xtime, 1, 1, return_images=False)


        state_0.append(0)
        state_1.append(0)
        state_2.append(0)
        state_3.append(0)
        state_4.append(0)
        state_5.append(0)
        state_6.append(0)
        state_7.append(0)
        state_8.append(0)
        
        XPosCurrent.append(100)
        YPosCurrent.append(100)
        
        ExpFTime.append(3)
        FOffset.append(700)
        
        FilterCurrent.append(5)
        
        CommandCurrent.append(0)
        
        StepCurrent.append(50)
        
        CurrentSlit.append(1)
        CurrentSlitPos.append(0)
        
        XExpTimeCurrent.append(1)
        CoaddsCurrent.append(1)
        
        XPosLMICurrent.append(100)
        YPosLMICurrent.append(100)

        XPosLMIDesired.append(100)
        YPosLMIDesired.append(100)

        CurrentBinning.append(1)
        
        TargetCurrent.append('test')
        NExpTimeCurrent.append(1)
        GuidingCurrent.append(0)
        NnseqCurrent.append(1)
        OffsetCurrent.append(20)
        DirCurrent.append(0)
        
        def run_toggleCommandLine(state_comm):
            print(state_comm)
            if state_comm == Qt.Checked:
                print('Checked')
                grid_t1.addWidget(Terminal1(self), 6, 1, 1, 3)
                grid_t2.addWidget(Terminal2(self), 8, 1, 1, 3)
                grid_t3.addWidget(Terminal3(self), 7, 1, 1, 4)
                grid_t4.addWidget(Terminal4(self), 8, 1, 1, 4)
                grid_t5.addWidget(Terminal5(self), 8, 1, 1, 4)
            elif state_comm != Qt.Checked:
                print('Not Checked')
                #grid_t1.removeWidget(Terminal1(self))
                #Terminal1(self).deleteLater()
        
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        ##
        # Initialize tab screen
        ##
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tab6 = QWidget()
        self.tab7 = QWidget()
        self.tabs.resize(500,200)
        
        ##
        # CREATE TABS
        ##
        self.tabs.addTab(self.tab1,"1. TEST IMAGE")
        self.tabs.addTab(self.tab2,"2. CALIBRATIONS")
        self.tabs.addTab(self.tab3,"3. FOCUS")
        self.tabs.addTab(self.tab4,"4. XCAM")
        self.tabs.addTab(self.tab5,"5. NIHTS")
        self.tabs.addTab(self.tab6,"6. LMI ACQUISITION")
        self.tabs.addTab(self.tab7,"7. SHUTDOWN")

        ##
        # NIHTS TEST TAB
        ##
        grid_t1 = QGridLayout()
        grid_t1.setSpacing(10)

        TestLabel1 = QLabel('Take NIHTS Test Image')
        TestLabel1.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        TestLabel2 = QLabel('* This must be done at the start of each LOUI initialization *')
        TestLabel2.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        TestButton = QPushButton("NIHTS Test Image")
        TestButton.clicked.connect(run_NIHTS_NTestImage)
        OpenCamButton = QPushButton("Open Camera")
        OpenCamButton.clicked.connect(run_open_xcam)
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(run_Exit)
        grid_t1.addWidget(ExitButton, 4, 5, 1, 1)
        
        grid_t1.addWidget(TestLabel1, 1, 1, 1, 5)
        grid_t1.addWidget(TestButton, 2, 3, 1, 1)
        grid_t1.addWidget(TestLabel2, 3, 1, 1, 5)
        grid_t1.addWidget(OpenCamButton, 4, 5, 1, 1)
        grid_t1.addWidget(CheckBox_Comm, 5, 1, 1, 1)
        
        self.tab1.setLayout(grid_t1)

        ##
        # CALIBRATIONS TAB
        ##
        grid_t2 = QGridLayout()
        grid_t2.setSpacing(10)
    
        ArcsLabel = QLabel('Begin Arcs Calibration Sequence')
        ArcsLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        ArcsButton = QPushButton("ARCS LONG")
        ArcsButton.clicked.connect(run_NIHTS_Arcs)
        grid_t2.addWidget(ArcsLabel, 1, 1, 1, 4)
        grid_t2.addWidget(ArcsButton, 2, 2, 1, 1)
        
        ArcsButton = QPushButton("ARCS SHORT")
        ArcsButton.clicked.connect(run_NIHTS_Arcs_short)
        grid_t2.addWidget(ArcsLabel, 1, 1, 1, 4)
        grid_t2.addWidget(ArcsButton, 2, 3, 1, 1)
        
        FlatsLabel = QLabel('Begin Dome Flats Calibration Sequence')
        FlatsLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        FlatsButtonOff = QPushButton("DOME DARKS")
        FlatsButtonOn = QPushButton("DOME FLATS")
        grid_t2.addWidget(FlatsLabel, 3, 1, 1, 4)
        grid_t2.addWidget(FlatsButtonOff, 4, 2, 1, 1)
        grid_t2.addWidget(FlatsButtonOn, 4, 3, 1, 1)
        
        FlatsButtonOff.clicked.connect(DarksStatus)
        FlatsButtonOn.clicked.connect(FlatsStatus)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(run_Exit)
        #grid_t2.addWidget(ExitButton, 6, 4, 1, 1)
        
        #global Progress_t2
        #Progress_t2 = QProgressBar(self)
        #grid_t2.addWidget(Progress_t2, 6, 1, 1, 3)
        
        grid_t2.addWidget(self.createSlitOptions(), 5, 1, 1, 4)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t2.addWidget(CheckBox_Comm, 7, 1, 1, 1)
    
        self.tab2.setLayout(grid_t2)
        
        ##
        # FOCUS TAB
        ##
        grid_t3 = QGridLayout()
        grid_t3.setSpacing(10)
        
        ExposureFButton = QPushButton("Take Exposure") #XCAM Exposure for Focus
        grid_t3.addWidget(ExposureFButton, 1, 3, 1, 1)
        ExposureFButton.clicked.connect(run_NIHTS_XFExp)

        ExposureTime = QLabel('Exp Time')
        ExposureTime.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        ExposureTimeEdit = QDoubleSpinBox()
        ExposureTimeEdit.setDecimals(2)
        ExposureTimeEdit.setValue(3)
        ExposureTimeEdit.valueChanged.connect(self.textchangedExpTime)
        grid_t3.addWidget(ExposureTimeEdit, 1, 2, 1, 1)
        grid_t3.addWidget(ExposureTime, 1, 1, 1, 1)
        
        grid_t3.addWidget(self.createFocusSetup1(), 2, 1, 1, 4)
        grid_t3.addWidget(self.createFocusSetup2(), 3, 1, 1, 4)
        
        FocusButton = QPushButton("RUN FOCUS")
        FocusButton.clicked.connect(self.run_NIHTS_Focus)
        grid_t3.addWidget(FocusButton, 4, 1, 1, 2)
        FocusOffset = QLabel('Best Guess Focus')
        FocusOffset.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        FocusOffsetEdit = QDoubleSpinBox()
        FocusOffsetEdit.setDecimals(0)
        FocusOffsetEdit.setMaximum(10000)
        FocusOffsetEdit.setValue(700)
        FocusOffsetEdit.valueChanged.connect(self.textchangedFOffset)
        grid_t3.addWidget(FocusOffsetEdit, 4, 4, 1, 1)
        grid_t3.addWidget(FocusOffset, 4, 3, 1, 1)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t3.addWidget(CheckBox_Comm, 6, 1, 1, 1)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(run_Exit)
        #grid_t3.addWidget(ExitButton, 5, 4, 1, 1)
        
        #global Progress_t3
        #Progress_t3 = QProgressBar(self)
        #grid_t3.addWidget(Progress_t3, 5, 1, 1, 3)
        
        self.tab3.setLayout(grid_t3)
        
        
        ##
        # XCAM TAB
        ##
        
        grid_t4 = QGridLayout()
        grid_t4.setSpacing(10)
        
        XExpTime = QLabel('Exposure Time')
        XExpTime.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        Coadds = QLabel('# Coadds')
        Coadds.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        grid_t4.addWidget(XExpTime, 1, 1, 1, 1)
        
        XExpTimeBox = QDoubleSpinBox(self)
        grid_t4.addWidget(XExpTimeBox, 1, 2, 1, 1)
        
        XExpTimeBox.setDecimals(2)
        XExpTimeBox.setValue(1)
        XExpTimeBox.valueChanged.connect(self.CurrentXExpTime)
        
        grid_t4.addWidget(Coadds, 1, 3, 1, 1)
        CoaddsBox = QSpinBox(self)
        
        grid_t4.addWidget(CoaddsBox, 1, 4, 1, 1)
        
        CoaddsBox.setValue(1)
        CoaddsBox.valueChanged.connect(self.CurrentCoadds)
        
        XExpButton = QPushButton("XCAM GO")
        XExpButton.clicked.connect(self.run_NIHTS_XExp)
        grid_t4.addWidget(XExpButton, 2, 2, 1, 2)
        
        
        HomeButton = QPushButton("Target is at HOME")
        HomeButton.clicked.connect(run_NIHTS_Home)
        grid_t4.addWidget(HomeButton, 4, 1, 1, 1)
        
        ReHomeButton = QPushButton("Return to HOME")
        ReHomeButton.clicked.connect(run_NIHTS_ReturnHome)
        grid_t4.addWidget(ReHomeButton, 5, 1, 1, 1)
        
        MoveSlit = QLabel('Move to Slit/Pos:')
        MoveSlit.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        grid_t4.addWidget(MoveSlit, 4, 2, 1, 1)
        
        Slit2Box = QComboBox(self)
        Slit2Box.addItem("SED1")
        Slit2Box.addItem("1.34")
        Slit2Box.addItem("0.81")
        Slit2Box.addItem("0.27")
        Slit2Box.addItem("0.54")
        Slit2Box.addItem("1.07")
        Slit2Box.addItem("1.61")
        Slit2Box.addItem("SED2")
        
        Slit2Box.setCurrentIndex(1)
        Slit2Box.currentIndexChanged.connect(self.SlitCurrent)
        
        Pos2Box = QComboBox(self)
        Pos2Box.addItem("A")
        Pos2Box.addItem("B")
        Pos2Box.addItem("Center")
        
        Pos2Box.setCurrentIndex(0)
        Pos2Box.currentIndexChanged.connect(self.SlitPosCurrent)
        
        #print('Current Slit', str(CurrentSlit[-1]))
        #print('Current Slit Pos', str(CurrentSlitPos[-1]))
        
        grid_t4.addWidget(Slit2Box, 4, 3, 1, 1)
        grid_t4.addWidget(Pos2Box, 4, 4, 1, 1)
        
        MoveButton = QPushButton("MOVE")
        MoveButton.clicked.connect(self.run_NIHTS_Move)
        grid_t4.addWidget(MoveButton, 5, 3, 1, 2)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t4.addWidget(CheckBox_Comm, 7, 1, 1, 1)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(run_Exit)
        #grid_t4.addWidget(ExitButton, 6, 4, 1, 1)
        
        #global Progress_t4
        #Progress_t4 = QProgressBar(self)
        #grid_t4.addWidget(Progress_t4, 7, 1, 1, 3)
        
        self.tab4.setLayout(grid_t4)
        
        ##
        # NIHTS TAB
        ##
        grid_t5 = QGridLayout()
        grid_t5.setSpacing(10)
        
        grid_t5.addWidget(self.createNIHTSSetup1(), 1, 1, 1, 4)
        
        NIHTSTestButton = QPushButton("NIHTS Test")
        NIHTSTestButton.clicked.connect(self.run_NIHTS_NTest)
        grid_t5.addWidget(NIHTSTestButton, 2, 1, 1, 2)
        
        NIHTSButton = QPushButton("NIHTS")
        NIHTSButton.clicked.connect(self.run_NIHTS_NExp)
        grid_t5.addWidget(NIHTSButton, 2, 3, 1, 2)
        
        ABButton = QPushButton("AB")
        ABButton.clicked.connect(self.run_NIHTS_AB)
        grid_t5.addWidget(ABButton, 3, 1, 1, 2)
        
        ABBAButton = QPushButton("ABBA")
        ABBAButton.clicked.connect(self.run_NIHTS_ABBA)
        grid_t5.addWidget(ABBAButton, 3, 3, 1, 2)
        
        grid_t5.addWidget(self.createNIHTSSetup2(), 4, 1, 1, 4)
        
        CenOffButton = QPushButton("CEN-SKY")
        CenOffButton.clicked.connect(self.run_NIHTS_CenSky)
        grid_t5.addWidget(CenOffButton, 5, 3, 1, 2)
        
        CenOffButton = QPushButton("OFFSET TARGET")
        CenOffButton.clicked.connect(self.run_NIHTS_Offset)
        grid_t5.addWidget(CenOffButton, 5, 1, 1, 2)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t5.addWidget(CheckBox_Comm, 7, 1, 1, 1)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(run_Exit)
        #grid_t5.addWidget(ExitButton, 6, 4, 1, 1)
        
        #global Progress_t5
        #Progress_t5 = QProgressBar(self)
        #grid_t5.addWidget(Progress_t5, 6, 1, 1, 3)
        
        self.tab5.setLayout(grid_t5)
        
        ##
        # LMI ACQUISITION TAB
        ##
        
        grid_t6 = QGridLayout()
        grid_t6.setSpacing(10)
        
        CurrLMIXPos = QLabel('Current X Position')
        CurrLMIXPos.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        CurrLMIYPos = QLabel('Current Y Position')
        CurrLMIYPos.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        DesLMIXPos = QLabel('HOME X Position')
        DesLMIXPos.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        DesLMIYPos = QLabel('HOME Y Position')
        DesLMIYPos.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        CurrLMIXPosEdit = QDoubleSpinBox(self)
        CurrLMIXPosEdit.setMaximum(3000)
        CurrLMIXPosEdit.setValue(100)
        CurrLMIXPosEdit.setDecimals(2)
        CurrLMIXPosEdit.valueChanged.connect(self.CurrXPosChanged)
        CurrLMIYPosEdit = QDoubleSpinBox(self)
        CurrLMIYPosEdit.setMaximum(3000)
        CurrLMIYPosEdit.setValue(100)
        CurrLMIYPosEdit.setDecimals(2)
        CurrLMIYPosEdit.valueChanged.connect(self.CurrYPosChanged)
        
        DesLMIXPosEdit = QDoubleSpinBox(self)
        DesLMIXPosEdit.setMaximum(3000)
        DesLMIXPosEdit.setValue(100)
        DesLMIXPosEdit.setDecimals(2)
        DesLMIXPosEdit.valueChanged.connect(self.DesXPosChanged)
        DesLMIYPosEdit = QDoubleSpinBox(self)
        DesLMIYPosEdit.setMaximum(3000)
        DesLMIYPosEdit.setValue(100)
        DesLMIYPosEdit.setDecimals(2)
        DesLMIYPosEdit.valueChanged.connect(self.DesYPosChanged)
        
        Binning = QLabel('LMI Binning:')
        Binning.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        grid_t6.addWidget(Binning, 1, 3, 1, 1)
        
        BinningBox = QComboBox(self)
        BinningBox.addItem("1x1")
        BinningBox.addItem("2x2")
        BinningBox.addItem("3x3")
        BinningBox.addItem("4x4")
        
        BinningBox.setCurrentIndex(1)
        BinningBox.currentIndexChanged.connect(self.BinningCurrent)
        
        #print('Current Binning', str(CurrentBinning[-1]))
        
        grid_t6.addWidget(BinningBox, 1, 4, 1, 1)
        
        grid_t6.addWidget(DesLMIXPos, 3, 1, 1, 1)
        grid_t6.addWidget(DesLMIXPosEdit, 3, 2, 1, 1)
        grid_t6.addWidget(DesLMIYPos, 3, 3, 1, 1)
        grid_t6.addWidget(DesLMIYPosEdit, 3, 4, 1, 1)
        grid_t6.addWidget(CurrLMIXPos, 5, 1, 1, 1)
        grid_t6.addWidget(CurrLMIXPosEdit, 5, 2, 1, 1)
        grid_t6.addWidget(CurrLMIYPos, 5, 3, 1, 1)
        grid_t6.addWidget(CurrLMIYPosEdit, 5, 4, 1, 1)
       

        MoveLMIButton = QPushButton("MOVE TARGET ON LMI")
        MoveLMIButton.clicked.connect(self.run_NIHTS_LMI_Mapping) ###FIX
        grid_t6.addWidget(MoveLMIButton, 6, 2, 1, 2)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t6.addWidget(CheckBox_Comm, 7, 1, 1, 1)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(run_Exit)
        #grid_t6.addWidget(ExitButton, 7, 4, 1, 1)
        
        self.tab6.setLayout(grid_t6)
        
        ##
        # NIHTS SHUTDOWN TAB
        ##
        grid_t7 = QGridLayout()
        grid_t7.setSpacing(10)

        ShutdownLabel = QLabel('Shutdown the NIHTS Camera')
        ShutdownLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        ShutdownButton = QPushButton("NIHTS Shutdown")
        ShutdownButton.clicked.connect(run_NIHTS_Shutdown)
        ExitLabel = QLabel('EXIT to Close the NIHTS GUI')
        ExitLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(run_Exit)
        grid_t7.addWidget(ExitButton, 4, 3, 1, 1)
        
        grid_t7.addWidget(ShutdownLabel, 1, 1, 1, 5)
        grid_t7.addWidget(ShutdownButton, 2, 3, 1, 1)
        grid_t7.addWidget(ExitLabel, 3, 1, 1, 5)
        grid_t7.addWidget(CheckBox_Comm, 5, 1, 1, 1)
        
        self.tab7.setLayout(grid_t7)
        
        
        ##
        # ADD TABS TO WIDGET
        ##
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    ## TERMINAL COMMAND LINE
    
    def run_NIHTS_Terminal1(self):
        
        ##
        # NIHTS_Terminal.py
        ##
        """ GUI Terminal Line - Enter Commands on Terminal Line
            v1.2: 2018-06-26, ag765@nau.edu, A Gustafsson
            
            ** GUI Version - Needs Testing
            
            updates:
            -
            
            """
        print('Starting Terminal')
        print('Command', str(CommandCurrent[-1]))
        
        #if str(CommandCurrent[-1]) == 0:
        #current_text = str(CommandEdit1.currentText())
        #print(current_text)
        print(curr_text)
    
    ##
    #
    ##


    def run_NIHTS_Terminal2(self):
        
        ##
        # NIHTS_Terminal.py
        ##
        """ GUI Terminal Line - Enter Commands on Terminal Line
            v1.2: 2018-06-26, ag765@nau.edu, A Gustafsson
            
            ** GUI Version - Needs Testing
            
            updates:
            -
            
            """
        print('Starting Terminal 2')
        print('Command', str(CommandCurrent[-1]))
            
        #if str(CommandCurrent[-1]) == 0:


    def run_NIHTS_Terminal3(self):
        
        ##
        # NIHTS_Terminal.py
        ##
        """ GUI Terminal Line - Enter Commands on Terminal Line
            v1.2: 2018-06-26, ag765@nau.edu, A Gustafsson
            
            ** GUI Version - Needs Testing
            
            updates:
            -
            
            """
        print('Starting Terminal 3')
        print('Command', str(CommandCurrent[-1]))
            
        #if str(CommandCurrent[-1]) == 0:



    def run_NIHTS_Terminal4(self):
        
        ##
        # NIHTS_Terminal.py
        ##
        """ GUI Terminal Line - Enter Commands on Terminal Line
            v1.2: 2018-06-26, ag765@nau.edu, A Gustafsson
            
            ** GUI Version - Needs Testing
            
            updates:
            -
            
            """
        print('Starting Terminal 4')
        print('Command', str(CommandCurrent[-1]))
            
        #if str(CommandCurrent[-1]) == 0:


    def run_NIHTS_Terminal5(self):
        
        ##
        # NIHTS_Terminal.py
        ##
        """ GUI Terminal Line - Enter Commands on Terminal Line
            v1.2: 2018-06-26, ag765@nau.edu, A Gustafsson
            
            ** GUI Version - Needs Testing
            
            updates:
            -
            
            """
        print('Starting Terminal 5')
        print('Command', str(CommandCurrent[-1]))
            
        #if str(CommandCurrent[-1]) == 0:


    global Terminal1
    def Terminal1(self):
    
        groupBox_term1 = QGroupBox("")
        #groupBox_term1.setEnabled(False)
        vbox_term1 = QGridLayout()
    
        Command1 = QLabel("Command:")
        Command1.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        CommandEdit1 = QComboBox()
        CommandEdit1.addItem("")
        CommandEdit1.addItem("x.go(coadds=1, exptime=1, nexp=1, return_images=False)")
        CommandEdit1.addItem("nihts.go(nexp=1, exptime=1, target='test', frame_type='object', comment1='Slit: None, Position: None', aborterror=False)")
        CommandEdit1.addItem("NIHTS_arcs.py")
        CommandEdit1.addItem("NIHTS_flats.py")
        CommandEdit1.addItem("NIHTS_focus.py xpos ypos")
        CommandEdit1.addItem("tcs.current_target_pt = tcs.home_pt")
        CommandEdit1.addItem("tcs.move_to_slit_position(tcs.slit['slit_width']['A/B/Cen']) = tcs.home_pt")
        CommandEdit1.addItem("NIHTS_AB.py target slit n_exptime")
        CommandEdit1.addItem("NIHTS_ABBA.py target slit n_exptime")
        CommandEdit1.addItem("NIHTS_CenSky.py target slit n_exptime")
        CommandEdit1.setEditable(True)
        CommandEdit1.currentIndexChanged.connect(self.CurrentComm)
        
        ## I AM HERE
        # NEED TO PRINT FOR THE Current Tab, Not for everything going to the same CurrentComm function
        ##
        
        vbox_term1.addWidget(Command1, 1, 1, 1, 1)
        vbox_term1.addWidget(CommandEdit1, 1, 2, 1, 1)
        
        curr_text.append(str(CommandEdit1.currentText()))
        print('TEXT', curr_text)

        SendButton1 = QPushButton("Send")
        SendButton1.clicked.connect(self.run_NIHTS_Terminal1)
        
        vbox_term1.addWidget(SendButton1, 1, 3, 1, 1)
        
        groupBox_term1.setLayout(vbox_term1)
    
        return groupBox_term1

    global Terminal2
    def Terminal2(self):

        groupBox_term2 = QGroupBox("")
        vbox_term2 = QGridLayout()

        Command2 = QLabel("Command:")
        Command2.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        CommandEdit2 = QComboBox()
        CommandEdit2.addItem("")
        CommandEdit2.addItem("x.go(coadds=1, exptime=1, nexp=1, return_images=False)")
        CommandEdit2.addItem("nihts.go(nexp=1, exptime=1, target='test', frame_type='object', comment1='Slit: None, Position: None', aborterror=False)")
        CommandEdit2.addItem("NIHTS_arcs.py")
        CommandEdit2.addItem("NIHTS_flats.py")
        CommandEdit2.addItem("NIHTS_focus.py xpos ypos")
        CommandEdit2.addItem("tcs.current_target_pt = tcs.home_pt")
        CommandEdit2.addItem("tcs.move_to_slit_position(tcs.slit['slit_width']['A/B/Cen']) = tcs.home_pt")
        CommandEdit2.addItem("NIHTS_AB.py target slit n_exptime")
        CommandEdit2.addItem("NIHTS_ABBA.py target slit n_exptime")
        CommandEdit2.addItem("NIHTS_CenSky.py target slit n_exptime")
        CommandEdit2.setEditable(True)
        CommandEdit2.currentIndexChanged.connect(self.CurrentComm)
        
        vbox_term2.addWidget(Command2, 1, 1, 1, 1)
        vbox_term2.addWidget(CommandEdit2, 1, 2, 1, 1)
        
        SendButton2 = QPushButton("Send")
        SendButton2.clicked.connect(self.run_NIHTS_Terminal2)
        vbox_term2.addWidget(SendButton2, 1, 3, 1, 1)
    
        groupBox_term2.setLayout(vbox_term2)

        return groupBox_term2

    global Terminal3
    def Terminal3(self):
    
        groupBox_term3 = QGroupBox("")
        vbox_term3 = QGridLayout()
    
        Command3 = QLabel("Command:")
        Command3.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        CommandEdit3 = QComboBox()
        CommandEdit3.addItem("")
        CommandEdit3.addItem("x.go(coadds=1, exptime=1, nexp=1, return_images=False)")
        CommandEdit3.addItem("nihts.go(nexp=1, exptime=1, target='test', frame_type='object', comment1='Slit: None, Position: None', aborterror=False)")
        CommandEdit3.addItem("NIHTS_arcs.py")
        CommandEdit3.addItem("NIHTS_flats.py")
        CommandEdit3.addItem("NIHTS_focus.py xpos ypos")
        CommandEdit3.addItem("tcs.current_target_pt = tcs.home_pt")
        CommandEdit3.addItem("tcs.move_to_slit_position(tcs.slit['slit_width']['A/B/Cen']) = tcs.home_pt")
        CommandEdit3.addItem("NIHTS_AB.py target slit n_exptime")
        CommandEdit3.addItem("NIHTS_ABBA.py target slit n_exptime")
        CommandEdit3.addItem("NIHTS_CenSky.py target slit n_exptime")
        CommandEdit3.setEditable(True)
        CommandEdit3.currentIndexChanged.connect(self.CurrentComm)
        
        vbox_term3.addWidget(Command3, 1, 1, 1, 1)
        vbox_term3.addWidget(CommandEdit3, 1, 2, 1, 1)
        
        SendButton3 = QPushButton("Send")
        SendButton3.clicked.connect(self.run_NIHTS_Terminal3)
        vbox_term3.addWidget(SendButton3, 1, 3, 1, 1)

        groupBox_term3.setLayout(vbox_term3)

        return groupBox_term3

    global Terminal4
    def Terminal4(self):
    
        groupBox_term4 = QGroupBox("")
        vbox_term4 = QGridLayout()
    
        Command4 = QLabel("Command:")
        Command4.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        CommandEdit4 = QComboBox()
        CommandEdit4.addItem("")
        CommandEdit4.addItem("x.go(coadds=1, exptime=1, nexp=1, return_images=False)")
        CommandEdit4.addItem("nihts.go(nexp=1, exptime=1, target='test', frame_type='object', comment1='Slit: None, Position: None', aborterror=False)")
        CommandEdit4.addItem("NIHTS_arcs.py")
        CommandEdit4.addItem("NIHTS_flats.py")
        CommandEdit4.addItem("NIHTS_focus.py xpos ypos")
        CommandEdit4.addItem("tcs.current_target_pt = tcs.home_pt")
        CommandEdit4.addItem("tcs.move_to_slit_position(tcs.slit['slit_width']['A/B/Cen']) = tcs.home_pt")
        CommandEdit4.addItem("NIHTS_AB.py target slit n_exptime")
        CommandEdit4.addItem("NIHTS_ABBA.py target slit n_exptime")
        CommandEdit4.addItem("NIHTS_CenSky.py target slit n_exptime")
        CommandEdit4.setEditable(True)
        CommandEdit4.currentIndexChanged.connect(self.CurrentComm)
        
        vbox_term4.addWidget(Command4, 1, 1, 1, 1)
        vbox_term4.addWidget(CommandEdit4, 1, 2, 1, 1)
        
        SendButton4 = QPushButton("Send")
        SendButton4.clicked.connect(self.run_NIHTS_Terminal4)
        vbox_term4.addWidget(SendButton4, 1, 3, 1, 1)
    
        groupBox_term4.setLayout(vbox_term4)

        return groupBox_term4

    global Terminal5
    def Terminal5(self):
    
        groupBox_term5 = QGroupBox("")
        vbox_term5 = QGridLayout()
    
        Command5 = QLabel("Command:")
        Command5.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        CommandEdit5 = QComboBox()
        CommandEdit5.addItem("")
        CommandEdit5.addItem("x.go(coadds=1, exptime=1, nexp=1, return_images=False)")
        CommandEdit5.addItem("nihts.go(nexp=1, exptime=1, target='test', frame_type='object', comment1='Slit: None, Position: None', aborterror=False)")
        CommandEdit5.addItem("NIHTS_arcs.py")
        CommandEdit5.addItem("NIHTS_flats.py")
        CommandEdit5.addItem("NIHTS_focus.py xpos ypos")
        CommandEdit5.addItem("tcs.current_target_pt = tcs.home_pt")
        CommandEdit5.addItem("tcs.move_to_slit_position(tcs.slit['slit_width']['A/B/Cen']) = tcs.home_pt")
        CommandEdit5.addItem("NIHTS_AB.py target slit n_exptime")
        CommandEdit5.addItem("NIHTS_ABBA.py target slit n_exptime")
        CommandEdit5.addItem("NIHTS_CenSky.py target slit n_exptime")
        CommandEdit5.setEditable(True)
        CommandEdit5.currentIndexChanged.connect(self.CurrentComm)
        
        vbox_term5.addWidget(Command5, 1, 1, 1, 1)
        vbox_term5.addWidget(CommandEdit5, 1, 2, 1, 1)
        
        SendButton5 = QPushButton("Send")
        SendButton5.clicked.connect(self.run_NIHTS_Terminal5)
        vbox_term5.addWidget(SendButton5, 1, 3, 1, 1)

        groupBox_term5.setLayout(vbox_term5)
        return groupBox_term5

    
    global DarksStatus
    def DarksStatus(self):
        infoBox = QMessageBox()
        infoBox.setText("Confirm the Dome Flat Lamps are OFF?")
        infoBox.setWindowTitle("Dome Darks Status")
        infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
        infoBox.button(QMessageBox.Yes).setText('Lamps OFF')
        infoBox.button(QMessageBox.No).setText('Lamps ON')
        infoBox.setEscapeButton(QMessageBox.Close)
        result = infoBox.exec_()
        if result == QMessageBox.Yes:
            print('-----Initialize Dome Darks Sequence-----')
            slit_state = [state_0[-1], state_1[-1], state_2[-1], state_3[-1], state_4[-1], state_5[-1], state_6[-1], state_7[-1], state_8[-1]]
            slitnames = ['All', 'SED1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'SED2']
            slits = []
            for i in range(9):
                status = bool(slit_state[i])
                print(slitnames[i], status)
                if i == 0 and status == True:
                    slits.append(slitnames[i])
                elif i != 0 and bool(slit_state[0]) == False:
                    status = bool(slit_state[i])
                    if status == True:
                        slits.append(slitnames[i])
                else:
                    pass
        
            slit0 = slit_state[0]
            slit1 = slit_state[1]
            slit2 = slit_state[2]
            slit3 = slit_state[3]
            slit4 = slit_state[4]
            slit5 = slit_state[5]
            slit6 = slit_state[6]
            slit7 = slit_state[7]
            slit8 = slit_state[8]
            
            ##
            # NIHTS_flats_darks_v7.py
            ##
            """ NIHTS DARKS - Take Dome Darks.
                v1.7: 2018-06-04, ag765@nau.edu, A Gustafsson
                
                Take 10 exposures at each exposure time from 1 - 20 seconds. Records frame type and slit information into headers. 4.03 slit is called sed1 and sed2.
                
                
                ** GUI Version - Needs testing
                
                To use, enter on the command line:
                run -i NIHTS_flats_darks.py
                
                updates:
                -
                """
    
            # make sure arc lamp is turned off
            print('Confirming ARC lamp is turned off')
            subprocess.call("pwrusb setone 3 0", shell=True)
    
            print('-----Starting Dome Darks Sequence-----')
            
            slit_state = [slit0, slit1, slit2, slit3, slit4, slit5, slit6, slit7, slit8]
            print(slit_state)
            
            slitnames = ['All', 'sed1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'sed2']
            slits = []
            for i in range(9):
                status = bool(int(slit_state[i]))
                if i == 0 and status == True:
                    slits.append(slitnames[i])
                elif i != 0 and bool(int(slit_state[0])) == False:
                    status = bool(int(slit_state[i]))
                    if status == True:
                        slits.append(slitnames[i])

            logging.info('Dome Darks Sequence Begin for slits: %s' %slits)
            
            nexp=1
    
            if slits == ['All']:
                slit = ['sed1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'sed2']
                print(slit)
            else:
                slit = slits
                print(slit)

            exposure_time = []
            for i in range(len(slit)):
                print(slit[i])
                if str(slit[i]) == 'sed1':
                    exposure_time.append(1)
                elif str(slit[i]) == '1.34':
                    exposure_time.append(3)
                elif str(slit[i]) == '0.81':
                    exposure_time.append(6)
                elif str(slit[i]) == '0.27':
                    exposure_time.append(15)
                elif str(slit[i]) == '0.54':
                    exposure_time.append(7)
                elif str(slit[i]) == '1.07':
                    exposure_time.append(4)
                elif str(slit[i]) == '1.61':
                    exposure_time.append(2)
                elif str(slit[i]) == 'sed2':
                    exposure_time.append(1)
        
            print('exp time', exposure_time)
            #Progress_t2.setValue(0)

            for i in range(len(slit)):
                nihts.go(nexp=nexp, exptime=exposure_time[i], target='Dome Flats - No Lamps', frame_type='dome flat', comment1 = 'Slit: '+str(slit[i])+', Position: None', aborterror=False)
                # wait for exposures to complete
                nihts.wait4nihts()
                completed = np.divide(100,len(slit))*(i+1)
                #Progress_t2.setValue(completed)

            print('-----Dome Darks Sequence Complete-----')

            ##
            #
            ##
            
            logging.info('Dome Darks Sequence End for Slits: %s' %slits)
        else:
            print('Turn the Deveny 6V Lamps OFF and try again.')
    
    global FlatsStatus
    def FlatsStatus(self):
        infoBox = QMessageBox()
        infoBox.setText("Confirm the Deveny 6V Dome Flat Lamps are ON?")
        infoBox.setWindowTitle("Dome Flats Status")
        infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
        infoBox.button(QMessageBox.Yes).setText('Lamps ON')
        infoBox.button(QMessageBox.No).setText('Lamps OFF')
        infoBox.setEscapeButton(QMessageBox.Close)
        result = infoBox.exec_()
        if result == QMessageBox.Yes:
            print('-----Initialize Dome Flats Sequence-----')
            slit_state = [state_0[-1], state_1[-1], state_2[-1], state_3[-1], state_4[-1], state_5[-1], state_6[-1], state_7[-1], state_8[-1]]
            slitnames = ['All', 'SED1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'SED2']
            slits = []
            for i in range(9):
                status = bool(slit_state[i])
                print(slitnames[i], status)
                if i == 0 and status == True:
                    slits.append(slitnames[i])
                elif i != 0 and bool(slit_state[0]) == False:
                    status = bool(slit_state[i])
                    if status == True:
                        slits.append(slitnames[i])
                else:
                    pass
            slit0 = slit_state[0]
            slit1 = slit_state[1]
            slit2 = slit_state[2]
            slit3 = slit_state[3]
            slit4 = slit_state[4]
            slit5 = slit_state[5]
            slit6 = slit_state[6]
            slit7 = slit_state[7]
            slit8 = slit_state[8]
            
            ##
            # NIHTS_flats_lamps_v7.py
            ##
            """ NIHTS FLATS - Take Dome Flats.
                v1.7: 2018-06-04, ag765@nau.edu, A Gustafsson
                
                Take 10 exposures at each exposure time from 1 - 20 seconds. Records frame type and slit information into headers. 4.03 slit is called sed1 and sed2.
                
                
                ** GUI Version - Needs testing
                
                To use, enter on the command line:
                run -i NIHTS_flats.py
                
                updates:
                -
                """
    
            # make sure arc lamp is turned off
            print('Confirming ARC lamp is turned off')
            subprocess.call("pwrusb setone 3 0", shell=True)
    
            print('-----Starting Dome Flats Sequence-----')
            logging.info('Dome Flats Sequence Begin for slits: %s' %slits)
    
            slit_state = [slit0, slit1, slit2, slit3, slit4, slit5, slit6, slit7, slit8]
            slitnames = ['All', 'sed1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'sed2']
            slits = []
            for i in range(9):
                status = bool(int(slit_state[i]))
                if i == 0 and status == True:
                    slits.append(slitnames[i])
                elif i != 0 and bool(int(slit_state[0])) == False:
                    status = bool(int(slit_state[i]))
                    if status == True:
                        slits.append(slitnames[i])

            nexp=10
    
            if slits == ['All']:
                slit = ['sed1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'sed2']
                print(slit)
            else:
                slit = slits
                print(slit)

            exposure_time = []
            for i in range(len(slit)):
                if slit[i] == 'sed1':
                    exposure_time.append(1)
                elif slit[i] == '1.34':
                    exposure_time.append(3)
                elif slit[i] == '0.81':
                    exposure_time.append(6)
                elif slit[i] == '0.27':
                    exposure_time.append(15)
                elif slit[i] == '0.54':
                    exposure_time.append(7)
                elif slit[i] == '1.07':
                    exposure_time.append(4)
                elif slit[i] == '1.61':
                    exposure_time.append(2)
                elif slit[i] == 'sed2':
                    exposure_time.append(1)
            
            #completed = 0
            #Progress_t2.setValue(completed)
            
            for i in range(len(slit)):
                nihts.go(nexp=nexp, exptime=exposure_time[i], target='Dome Flats', frame_type='dome flat', comment1 = 'Slit: '+str(slit[i])+', Position: None', aborterror=False)
                # wait for exposures to complete
                nihts.wait4nihts()
                #completed = np.divide(100,len(slit))*(i+1)
                #Progress_t2.setValue(completed)
    
            print('-----Dome Flats Sequence Complete-----')
            logging.info('Dome Flats Sequence End for Slits: %s' %slits)

            ##
            #
            ##
            
        else:
            print('Turn the Deveny 6V Lamps ON and try again.')

    ## SLIT BOX
    def createSlitOptions(self):
        
        groupBox = QGroupBox("", self)
        
        slit0 = QCheckBox("ALL", self)
        slit0.stateChanged.connect(self.run_clickBox0)
        #slit0.setCheckState(True)
        
        slit1 = QCheckBox("SED1", self)
        slit1.stateChanged.connect(self.run_clickBox1)
        
        slit2 = QCheckBox("1.34", self)
        slit2.stateChanged.connect(self.run_clickBox2)
        
        slit3 = QCheckBox("0.81", self)
        slit3.stateChanged.connect(self.run_clickBox3)
        
        slit4 = QCheckBox("0.27", self)
        slit4.stateChanged.connect(self.run_clickBox4)
        
        slit5 = QCheckBox("0.54", self)
        slit5.stateChanged.connect(self.run_clickBox5)
        
        slit6 = QCheckBox("1.07", self)
        slit6.stateChanged.connect(self.run_clickBox6)
        
        slit7 = QCheckBox("1.61", self)
        slit7.stateChanged.connect(self.run_clickBox7)
        
        slit8 = QCheckBox("SED2", self)
        slit8.stateChanged.connect(self.run_clickBox8)
        
        
        slit0.toggled.connect(slit1.setDisabled)
        slit0.toggled.connect(slit2.setDisabled)
        slit0.toggled.connect(slit3.setDisabled)
        slit0.toggled.connect(slit4.setDisabled)
        slit0.toggled.connect(slit5.setDisabled)
        slit0.toggled.connect(slit6.setDisabled)
        slit0.toggled.connect(slit7.setDisabled)
        slit0.toggled.connect(slit8.setDisabled)
        
        slit1.toggled.connect(slit0.setDisabled)
        slit2.toggled.connect(slit0.setDisabled)
        slit3.toggled.connect(slit0.setDisabled)
        slit4.toggled.connect(slit0.setDisabled)
        slit5.toggled.connect(slit0.setDisabled)
        slit6.toggled.connect(slit0.setDisabled)
        slit7.toggled.connect(slit0.setDisabled)
        slit8.toggled.connect(slit0.setDisabled)
        
        
        SlitsLabel = QLabel('Select slitlets you will use during observations:')
        SlitsLabel.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        
        vbox = QGridLayout()
        vbox.addWidget(SlitsLabel, 1, 1, 1, 4)
        vbox.addWidget(slit0, 2, 1, 1, 1)
        vbox.addWidget(slit1, 3, 1, 1, 1)
        vbox.addWidget(slit2, 4, 1, 1, 1)
        vbox.addWidget(slit3, 3, 2, 1, 1)
        vbox.addWidget(slit4, 4, 2, 1, 1)
        vbox.addWidget(slit5, 3, 3, 1, 1)
        vbox.addWidget(slit6, 4, 3, 1, 1)
        vbox.addWidget(slit7, 3, 4, 1, 1)
        vbox.addWidget(slit8, 4, 4, 1, 1)
        groupBox.setLayout(vbox)
        
        slit0.setChecked(True)
        
        return groupBox
    
    def run_clickBox0(self, state0):
        if state0 == Qt.Checked:
            print('All Slits Selected')
            state_0.append(1)
        else:
            state_0.append(0)
    
    def run_clickBox1(self, state1):
        if state1 == Qt.Checked:
            print('SED1 Selected')
            state_1.append(1)
        else:
            state_1.append(0)

    def run_clickBox2(self, state2):
        if state2 == Qt.Checked:
            print('1.34" Selected')
            state_2.append(1)
        else:
            state_2.append(0)

    def run_clickBox3(self, state3):
        if state3 == Qt.Checked:
            print('0.81" Selected')
            state_3.append(1)
        else:
            state_3.append(0)

    def run_clickBox4(self, state4):
        if state4 == Qt.Checked:
            print('0.27" Selected')
            state_4.append(1)
        else:
            state_4.append(0)

    def run_clickBox5(self, state5):
        if state5 == Qt.Checked:
            print('0.54" Selected')
            state_5.append(1)
        else:
            state_5.append(0)

    def run_clickBox6(self, state6):
        if state6 == Qt.Checked:
            print('1.07" Selected')
            state_6.append(1)
        else:
            state_6.append(0)

    def run_clickBox7(self, state7):
        if state7 == Qt.Checked:
            print('1.61" Selected')
            state_7.append(1)
        else:
            state_7.append(0)

    def run_clickBox8(self, state8):
        if state8 == Qt.Checked:
            print('SED2 Selected')
            state_8.append(1)
        else:
            state_8.append(0)


    ## Focus Setup Box
    def createFocusSetup1(self):
    
        groupBox1_t3 = QGroupBox("")
        vbox1_t3 = QGridLayout()
        
        Title = QLabel('Set X and Y Position of the Focus Star')
        Title.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
    
        XPos = QLabel('X Pos')
        XPos.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        YPos = QLabel('Y Pos')
        YPos.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        
        XPosEdit = QSpinBox() #(self)
        XPosEdit.setMaximum(1025)
        XPosEdit.setValue(100)
        XPosEdit.valueChanged.connect(self.textchangedX)
        YPosEdit = QSpinBox()
        YPosEdit.setMaximum(1025)
        YPosEdit.setValue(100)
        YPosEdit.valueChanged.connect(self.textchangedY)

        vbox1_t3.setSpacing(10)
        
        vbox1_t3.addWidget(Title, 1, 2, 1, 2)
        vbox1_t3.addWidget(XPos, 2, 1, 1, 1)
        vbox1_t3.addWidget(XPosEdit, 2, 2, 1, 1)
        
        vbox1_t3.addWidget(YPos, 2, 3, 1, 1)
        vbox1_t3.addWidget(YPosEdit, 2, 4, 1, 1)
        
        groupBox1_t3.setLayout(vbox1_t3)
        
        return groupBox1_t3
        
    def createFocusSetup2(self):
        
        groupBox2_t3 = QGroupBox("")
        vbox2_t3 = QGridLayout()
        
        Filter = QLabel('LMI Filter')
        Filter.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        #Add Box for Center value - should be able to adjust off of 1000+offset
        Step = QLabel('Step Size')
        Step.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        vbox2_t3.setSpacing(10)
        
        FilterBox = QComboBox(self)
        FilterBox.addItem("OPEN")
        FilterBox.addItem("B")
        FilterBox.addItem("V")
        FilterBox.addItem("R")
        FilterBox.addItem("VR")
        FilterBox.addItem("SDSS g")
        FilterBox.addItem("SDSS r")
        FilterBox.addItem("SDSS i")
        FilterBox.addItem("[OIII]")
        FilterBox.addItem("H-alpha ON")
        FilterBox.addItem("H-alpha OFF")
        FilterBox.addItem("WC")
        FilterBox.addItem("WN")
        FilterBox.addItem("CT")
        FilterBox.addItem("BC")
        FilterBox.addItem("GC")
        FilterBox.addItem("RC")
        vbox2_t3.addWidget(Filter, 2, 1, 1, 1)
        vbox2_t3.addWidget(FilterBox, 2, 2, 1, 1)
        
        FilterBox.setCurrentIndex(5)
        FilterBox.currentIndexChanged.connect(self.CurrentFilter)
        
        vbox2_t3.addWidget(Step, 2, 3, 1, 1)
        StepBox = QSpinBox(self)
        vbox2_t3.addWidget(StepBox, 2, 4, 1, 1)
        
        StepBox.setValue(50)
        StepBox.valueChanged.connect(self.CurrentStep)
        
        groupBox2_t3.setLayout(vbox2_t3)
        
        return groupBox2_t3
    
    def textchangedExpTime(self, xfexptime):
        ExpFTime.append(xfexptime)
    
    def textchangedFOffset(self, focus_offset):
        FOffset.append(focus_offset)
    
    def textchangedX(self, xposition):
        XPosCurrent.append(xposition)
    
    def textchangedY(self, yposition):
        YPosCurrent.append(yposition)
    
    def CurrentFilter(self, curr_filter):
        FilterCurrent.append(curr_filter)
    
    def CurrentComm(self, curr_command):
        CommandCurrent.append(curr_command)
    
    def CurrentStep(self, curr_step):
        StepCurrent.append(curr_step)

    def run_NIHTS_Focus(self):
        print('X ExpTime', str(ExpFTime[-1]))
        print('X Pos', str(XPosCurrent[-1]))
        print('Y Pos', str(YPosCurrent[-1]))
        print('Filter', str(FilterCurrent[-1]))
        print('Step Size', str(StepCurrent[-1]))
        f_offset = float(FOffset[-1])
        xtime = str(ExpFTime[-1])
        x_starpos = str(XPosCurrent[-1])
        y_starpos = str(YPosCurrent[-1])
        focus_filter = str(FilterCurrent[-1])
        focus_step = str(StepCurrent[-1])
        filter_list = ['OPEN','B','V','R','VR','SDSSg','SDSSr','SDSSi','OIII','Ha_on','Ha_off','WC','WN','CT','BC','GC','RC']
        filter = filter_list[int(focus_filter)]
        
        if filter=='OPEN':
            dichroic = 239.95
            offset = 0
        elif filter=='B':
            dichroic = 238.76
            offset = 105
        elif filter=='V':
            dichroic = 238.76
            offset = 105
        elif filter=='R':
            dichroic = 238.36
            offset = 140
        elif filter=='VR':
            dichroic = 237.84
            offset = 185
        elif filter=='SDSSg':
            dichroic = 237.90
            offset = 180
        elif filter=='SDSSr':
            dichroic = 237.90
            offset = 180
        elif filter=='SDSSi':
            dichroic = 237.90
            offset = 180
        elif filter=='OIII':
            dichroic = 237.62
            offset = 205
        elif filter=='Ha_on':
            dichroic = 238.19
            offset = 155
        elif filter=='Ha_off':
            dichroic = 238.19
            offset = 155
        elif filter=='WC':
            dichroic = 238.07
            offset = 165
        elif filter=='WN':
            dichroic =  238.13
            offset = 160
        elif filter=='CT':
            dichroic = 238.01
            offset = 170
        elif filter=='BC':
            dichroic = 237.96
            offset = 175
        elif filter=='GC':
            dichroic = 237.96
            offset = 175
        elif filter=='RC':
            dichroic = 237.96
            offset = 175
        
        logging.info('Focus Sequence Requested')
        infoBox = QMessageBox()
        infoBox.setText("Ask the TO to move the dichroic position to %smm ... Ready?" % dichroic)
        infoBox.setWindowTitle("Focus Sequence")
        infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
        infoBox.setEscapeButton(QMessageBox.Close)
        result = infoBox.exec_()
        if result == QMessageBox.Yes:
            print('Initialize Focus Sequence')
            logging.info('Focus Sequence Begin...')
            logging.info('Focus Parameters: xpos: %s, ypos: %s, exptime: %s, filter: %s, step: %s' %(x_starpos, y_starpos, xtime, filter, focus_step))
           
            ##
            # NIHTS_focus_v8.py
            ##
            """ NIHTS FOCUS - Runs a focus script.
                v1.9: 2018-07-17, ag765@nau.edu, A Gustafsson
                
                Focus NIHTS for LMI filter. Standalone.
                
                set LMI filter and step size. script changes focus 11 times stepping through the nominal value (determined from filter). script throws these x.go images into a focus folder. Here it takes a 30" box around the star and calculates FWHM in both x and y for each image. It then plots the FWHM ('') vs Focus and fits a polynomial to determine best fit.
                
                - set exposure time -- right now hard coded at 3sec
                - nominal focus set to 810
                - create new focus directory each time you run focus script with time stamp
                - x and y gaussian fits
                - fix so that it doesnt redo your difference image
                
                ** GUI Version -- Needs Testing
                
                
                To use, enter on the command line in the ipython environment:
                run -i NIHTS_focus.py xpos ypos opt(-filter) opt(-seeing) opt(-x_exptime) opt(-step) opt(-gdr_string)
                
                updates:
                - update best focus center
                
                """
            import argparse
            import subprocess, sys
            from astropy.io import fits
            import os
            import os.path
            import shutil
            import glob
            import time
            import math
            import random
            import matplotlib.pyplot as plt
            import numpy as np
            from scipy.optimize import curve_fit
            
            
            completed = 0
            
            xpos = float(x_starpos)
            ypos = float(y_starpos)
            x_exptime = float(xtime)
            step = float(focus_step)
            seeing = 2
    
            ###
            ## SET UP FOCUS FILES DIRECTORY FOR ANALYSIS ##
            
            xcam_dir = '/Users/xcam/xenics-data/'
            date_dir = os.listdir(xcam_dir)
                    
            dates = []
            for date in date_dir:
                dates.append(date)
            today = dates[-1]
            print('Date: %s' % today)
                
            file_dir = os.listdir(xcam_dir + today + '/')
            files = []
            for file in file_dir:
                if file.endswith('.fits'):
                    files.append(file)
            last_file = files[-1]
            
            print('last file',last_file)

            if last_file == 'current.fits':
                last_file = files[-2]
            else:
                pass

            prefix, num = last_file.split('_')
            number, suffix = num.split('.')

            ####
            
            # take background image
            nihts.wait4nihts()
            print(' --- Creating Background Image ---')
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(-50,0))
                    
            nihts.wait4nihts()
            
            x.go(x_exptime,1,1,return_images=False)

            #completed = 6.7
            #Progress_t3.setValue(completed)
            
            nihts.wait4nihts()
            
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(+50,0))
                
            nihts.wait4nihts()
            
            # take focus images
            print('----------------------- \n Beginning Focus Sequence \n ------------------------')
            
            #nom_focus = f_offset-180 #Nominal is 650 (1650) AG 08/12/18
            #tcs.send_focus_microns(nom_focus)
            #print('--- Nominal Focus Value ---', nom_focus)
            
            focus_list = []
            for j in range(7):
                focus = f_offset+(j-3)*step
                print('---------------- \n Focus value: %f \n -----------------' % focus)
                tcs.send_focus_microns(focus)
                focus_list.append(focus)
                    
                nihts.wait4nihts()
                
                for k in range(2):
                    #take image
                    x.go(x_exptime,1,1,return_images=False)
                    nihts.wait4nihts()

                #completed = 20+13.333*j
                #Progress_t3.setValue(completed)

            #####
                    
            d=0
            while os.path.exists(xcam_dir + today + '/focus_%s' %d):
                d+=1
            os.makedirs(xcam_dir + today + '/focus_%s' %d)
            current_focus_dir = xcam_dir + today + '/focus_%s'%d
            print('current focus dir', current_focus_dir)
                    
            i = int(float(number)+1)
            file_list = []
            for i in range(15):
                focus_file = prefix + '_' + '{0:04}'.format(int(float(number)+i+1)) + '.fits'
                file_list.append(focus_file)

            for filename in os.listdir(xcam_dir + today + '/'):
                for filename in file_list:
                    shutil.copy(xcam_dir + today + '/' + filename, current_focus_dir)

            ######### NOW ANALYZE IMAGES IN FOCUS DIRECTORY ########
                    
            focus_files = os.listdir(current_focus_dir)
            print('Background image',focus_files[0])
            bkg = focus_files[0]
                    
            star_files = focus_files[1:]
                    
            # loop through all images of star
            FWHM_x = []
            FWHM_y = []
            for focus_file in star_files:
                image_dir = current_focus_dir + '/' + focus_file
                    
                image_data = fits.getdata(image_dir)[0]
                
                x_pos= int(xpos)
                y_pos= int(ypos)
                        
                image_data_star = image_data[y_pos-30:y_pos+30, x_pos-30:x_pos+30] - fits.getdata(current_focus_dir + '/' + bkg)[0][y_pos-30:y_pos+30, x_pos-30:x_pos+30]
                        
                plt.ion()
                plt.figure(1)
                plt.imshow(image_data_star, cmap='Blues')
                plt.pause(0.0001)
                plt.scatter([30], [30], c='r', marker ='x', s=100)
                plt.pause(0.0001)
                time.sleep(1)
                print('-----')
                plt.close()
                    
                star_flat_x = np.array(np.sum(image_data_star, axis=0))
                star_flat_y = np.array(np.sum(image_data_star, axis=1))
                    
                xrange = np.arange(0,60,1)
                mean_x = np.divide(np.sum(xrange*np.array(star_flat_x)),np.sum(np.array(star_flat_x)))
                sigma_x = np.sqrt(np.abs([np.divide(np.sum(star_flat_x*((xrange-mean_x)**2)),(np.sum(star_flat_x)))]))
                line_fit_coeff_x = np.polyfit(xrange, star_flat_x, 1, full=True)
                line_fit_x = line_fit_coeff_x[0][0]*np.power(xrange,1) + line_fit_coeff_x[0][1]
                zero_star_x = star_flat_x
                        
                yrange = np.arange(0,60,1)
                mean_y = np.divide(np.sum(yrange*np.array(star_flat_y)),np.sum(np.array(star_flat_y)))
                sigma_y = np.sqrt(np.abs([np.divide(np.sum(star_flat_y*((yrange-mean_y)**2)),(np.sum(star_flat_y)))]))
                line_fit_coeff_y = np.polyfit(yrange, star_flat_y, 1, full=True)
                line_fit_y = line_fit_coeff_y[0][0]*np.power(yrange,1) + line_fit_coeff_y[0][1]
                zero_star_y = star_flat_y
                        
                X = np.arange(0,60,1)
                Y = np.arange(0,60,1)
                        
                init_guess = np.divide(np.divide(seeing,0.326), 2*np.sqrt(2*np.log(2)))
                init_vals_x = [80000,30,init_guess,0]  # for [amp, cen, sigma,c]
                init_vals_y = [40000,30,init_guess,0]  # for [amp, cen, sigma,c]
                        
                def Gauss_x(X,amp,cen,sigma_x,c_x):
                    return amp*np.exp(-(X-cen)**2/(2*sigma_x**2))+c_x
                popt_x, pcov_x = curve_fit(Gauss_x,X,zero_star_x,p0=init_vals_x)
                        
                def Gauss_y(Y,amp,cen,sigma_y,c_y):
                    return amp*np.exp(-(Y-cen)**2/(2*sigma_y**2))+c_y
                popt_y, pcov_y = curve_fit(Gauss_y,Y,zero_star_y,p0=init_vals_y)
                    
                plt.ion()
                plt.figure(1)
                plt.plot(X, zero_star_x, 'b+:', label='data_x')
                plt.pause(0.0001)
                plt.plot(X, Gauss_x(X, *popt_x), 'b-', label='fit_x')
                plt.pause(0.0001)
                plt.plot(Y, zero_star_y, 'r+:', label='data_y')
                plt.pause(0.0001)
                plt.plot(Y, Gauss_y(Y, *popt_y), 'r-', label='fit_y')
                plt.pause(0.0001)
                plt.legend()
                plt.title('')
                plt.xlabel('Pixels')
                plt.ylabel('Intensity')
                time.sleep(1)
                print('-----')
                plt.close()
                    
                FWHMx_pix = 2*np.sqrt(2*np.log(2))*popt_x[2]
                FWHMx_arc = 0.326*FWHMx_pix
                FWHM_x.append(FWHMx_arc)
                print('FWHM x: %f arcsec' %FWHMx_arc)
                        
                FWHMy_pix = 2*np.sqrt(2*np.log(2))*popt_y[2]
                FWHMy_arc = 0.326*FWHMy_pix
                FWHM_y.append(FWHMy_arc)
                print('FWHM y: %f arcsec' %FWHMy_arc)
                        
                focus_values = [val for val in focus_list for _ in (0,1)]
                
            # Resample focus values
            focus_new = np.arange(f_offset+(-3)*step, f_offset+(3)*step, 0.001)
            
            ## polyfit -- short (2nd order)
            fit_coeff_x = np.polyfit(focus_values, FWHM_x, 2, full=True)
            fit_x_short = fit_coeff_x[0][0]*np.power(focus_values,2) + fit_coeff_x[0][1]*np.power(focus_values,1)+ fit_coeff_x[0][2]
            ## polyfit (2nd order)
            fit_x = fit_coeff_x[0][0]*np.power(focus_new,2) + fit_coeff_x[0][1]*np.power(focus_new,1)+ fit_coeff_x[0][2]
                
            fit_coeff_y = np.polyfit(focus_values, FWHM_y, 2, full=True)
            fit_y_short = fit_coeff_y[0][0]*np.power(focus_values,2) + fit_coeff_y[0][1]*np.power(focus_values,1)+ fit_coeff_y[0][2]
            fit_y = fit_coeff_y[0][0]*np.power(focus_new,2) + fit_coeff_y[0][1]*np.power(focus_new,1)+ fit_coeff_y[0][2]
            
            ## Check for intersection
            if len(np.where(np.round(fit_x,4) == np.round(fit_y,4))[0]) != 0:
                
                intersect = focus_new[np.where(np.round(fit_x,4) == np.round(fit_y,4))]
                    
                FWHM_bestx = fit_x[np.where(np.round(fit_x,4) == np.round(fit_y,4))]
                FWHM_besty = fit_y[np.where(np.round(fit_x,4) == np.round(fit_y,4))]
                
                diff_x = FWHM_x - fit_x_short
                var_x = np.std(diff_x)
                diff_y = FWHM_y - fit_y_short
                var_y = np.std(diff_y)
                
                print('----------------------- \n Best Focus: %1.0f \n ----------------------- \n Best Seeing: %1.1f \n ----------------------- \n Seeing Variability: %1.1f \n -----------------------' % (float(np.median(intersect)), float(np.median(FWHM_bestx)), var_x))
                
                plt.ioff()
                plt.plot(focus_values, FWHM_x, 'b+:', label='data_x')
                plt.plot(focus_values, FWHM_y, 'r+:', label='data_y')
                plt.plot(focus_new, fit_x, 'b-', label='fit_x')
                plt.plot(focus_new, fit_y, 'r-', label='fit_y')
                plt.legend()
                plt.title('Focus Script')
                plt.xlabel('Focus (microns)')
                plt.ylabel('FWHM (")')
                plt.savefig(current_focus_dir+'/focus_curve.png')
                plt.close()
                
                focus_plot = current_focus_dir+'/focus_curve.png'
                subprocess.call("open %s" %focus_plot, shell=True)
                
                print('----- FOCUS SEQUENCE COMPLETE -----')
                print('-------  BEST FOCUS = %1.1f  -------' % float(np.round(np.median(intersect),-1)))

                ##
                #
                ##
                infoBox = QMessageBox()
                infoBox.setText("Do you want to send focus offset: %1.0f microns?" % (float(np.round(np.median(intersect),-1))))
                infoBox.setWindowTitle("Best Focus")
                infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
                infoBox.setEscapeButton(QMessageBox.Close)
                result = infoBox.exec_()
                if result == QMessageBox.Yes:
                    print('Sending Best Focus')
                    tcs.send_focus_microns(float(np.round(np.median(intersect),-1)))
                    logging.info('Best Focus Sent')
                    logging.info('... Focus Sequence End')
                else:
                    pass
                    logging.info('Best Focus Declined')
                    tcs.send_focus_microns(float(f_offset))
                    logging.info('... Focus Sequence End')
            else:
                print('No Intersection')
                
                plt.ioff()
                plt.plot(focus_values, FWHM_x, 'b+:', label='data_x')
                plt.plot(focus_values, FWHM_y, 'r+:', label='data_y')
                plt.plot(focus_new, fit_x, 'b-', label='fit_x')
                plt.plot(focus_new, fit_y, 'r-', label='fit_y')
                plt.legend()
                plt.title('Focus Script')
                plt.xlabel('Focus (microns)')
                plt.ylabel('FWHM (")')
                plt.savefig(current_focus_dir+'/focus_curve.png')
                plt.close()

                focus_plot = current_focus_dir+'/focus_curve.png'
                subprocess.call("open %s" %focus_plot, shell=True)
                
                logging.info('No Best Focus Found')
                tcs.send_focus_microns(float(f_offset))
                logging.info('... Focus Sequence End')
                        
        else:
            logging.info('Dichroic Not in Place for Focus')
            print('clicked no')

    def BinningCurrent(self, curr_binning):
        CurrentBinning.append(curr_binning)
                        
    ## XCAM X.GO
    def SlitCurrent(self, curr_slit):
        CurrentSlit.append(curr_slit)
    
    def SlitPosCurrent(self, curr_slit_pos):
        CurrentSlitPos.append(curr_slit_pos)
        print(CurrentSlitPos)
    
    def run_NIHTS_Move(self):
        print('Current Slit', str(CurrentSlit[-1]))
        print('Current Slit Pos', str(CurrentSlitPos[-1]))
        current_slit = str(CurrentSlit[-1])
        current_slit_pos = str(CurrentSlitPos[-1])
        slit_list = ['sed1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'sed2']
        pos_list = ['A', 'B', 'cen']
        slit = slit_list[int(current_slit)]
        print('slit', slit)
        pos = pos_list[int(current_slit_pos)]
        print('pos', pos)
        logging.info('Move to slit %s at position %s' %(slit, pos))
        
        ##
        # NIHTS_Move.py
        ##
        """ NIHTS Move - Move target to slit.
            v1.1: 2018-05-14, ag765@nau.edu, A Gustafsson
            
            ** GUI Version - Needs Testing
            
            updates:
            -
            
            """
    
        tcs.move_to_slit_position(tcs.slits[str(slit)][pos])

        ##
        #
        ##
    
    
    
    def CurrXPosChanged(self, curr_xposLMI):
        XPosLMICurrent.append(curr_xposLMI)
    def CurrYPosChanged(self, curr_yposLMI):
        YPosLMICurrent.append(curr_yposLMI)
    
    def DesXPosChanged(self, des_xposLMI):
        XPosLMIDesired.append(des_xposLMI)
    def DesYPosChanged(self, des_yposLMI):
        YPosLMIDesired.append(des_yposLMI)
    
    def CurrentXExpTime(self, curr_xexptime):
        XExpTimeCurrent.append(curr_xexptime)
    
    def CurrentCoadds(self, curr_coadds):
        CoaddsCurrent.append(curr_coadds)
    
    def run_NIHTS_XExp(self):
        print('XCAM ExpTime', str(XExpTimeCurrent[-1]))
        print('Coadds', str(CoaddsCurrent[-1]))
        current_xexptime = str(XExpTimeCurrent[-1])
        current_coadds = str(CoaddsCurrent[-1])
        
        logging.info('XCAM Exposure: %s second(s), %s coadds' %(current_xexptime, current_coadds))
        
        ##
        # NIHTS_XExp.py
        ##
        """ XCAM Exposure - Take XCAM Exposure
            v1.1: 2018-04-12, ag765@nau.edu, A Gustafsson
            
            ** GUI Version - Needs Testing
            
            updates:
            -
            
            """
        
        xexptime = float(current_xexptime)
        coadds = int(current_coadds)
        
        nihts.wait4nihts()
        x.go(xexptime, coadds, 1, return_images=False)
    
        ##
        #
        ##

    ## NIHTS Setup Box
    def createNIHTSSetup1(self):
        
        groupBox1_t5 = QGroupBox("")
        vbox_t5 = QGridLayout()
        
        Target = QLabel('Target')
        Target.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        Guiding = QLabel('Guiding')
        Guiding.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        TargetEdit = QLineEdit()
        TargetEdit.textChanged.connect(self.textchangedTarget)
        
        vbox_t5.setSpacing(10)
        
        vbox_t5.addWidget(Target, 1, 1, 1, 1)
        vbox_t5.addWidget(TargetEdit, 1, 2, 1, 1)
        
        GuideBox = QComboBox(self)
        GuideBox.addItem("OFF")
        GuideBox.addItem("ON")
        
        GuideBox.setCurrentIndex(0)
        GuideBox.currentIndexChanged.connect(self.CurrentGuiding)

        vbox_t5.addWidget(Guiding, 1, 3, 1, 1)
        vbox_t5.addWidget(GuideBox, 1, 4, 1, 1)
        
        NExpTime = QLabel('ExpTime')
        NExpTime.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        NumSeq = QLabel('# Seq')
        NumSeq.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        vbox_t5.addWidget(NExpTime, 2, 1, 1, 1)
        NExpTimeBox = QDoubleSpinBox(self)
        vbox_t5.addWidget(NExpTimeBox, 2, 2, 1, 1)
        
        NExpTimeBox.setDecimals(2)
        NExpTimeBox.setMaximum(1000)
        NExpTimeBox.setValue(1)
        NExpTimeBox.valueChanged.connect(self.CurrentNExpTime)
        
        vbox_t5.addWidget(NumSeq, 2, 3, 1, 1)
        NumSeqBox = QSpinBox(self)
        vbox_t5.addWidget(NumSeqBox, 2, 4, 1, 2)
        
        NumSeqBox.setValue(1)
        NumSeqBox.valueChanged.connect(self.CurrentNnseq)
        
        groupBox1_t5.setLayout(vbox_t5)
        
        return groupBox1_t5
    
    
    def createNIHTSSetup2(self):
        
        groupBox2_t5 = QGroupBox("")
        vbox_t5 = QGridLayout()
        
        Offset = QLabel('Offset (")')
        Offset.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        Direction = QLabel('Direction')
        Direction.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        vbox_t5.addWidget(Offset, 3, 1, 1, 1)
        OffsetBox = QSpinBox(self)
        vbox_t5.addWidget(OffsetBox, 3, 2, 1, 1)
        
        OffsetBox.setMaximum(1000)
        OffsetBox.setValue(20)
        OffsetBox.valueChanged.connect(self.CurrentOffset)
        
        DirBox = QComboBox(self)
        DirBox.addItem("Up")
        DirBox.addItem("Down")
        DirBox.addItem("Left")
        DirBox.addItem("Right")
        DirBox.addItem("RA")
        DirBox.addItem("DEC")
        
        DirBox.setCurrentIndex(0)
        DirBox.currentIndexChanged.connect(self.CurrentDirection)
        
        vbox_t5.addWidget(Direction, 3, 3, 1, 1)
        vbox_t5.addWidget(DirBox, 3, 4, 1, 2)
        
        groupBox2_t5.setLayout(vbox_t5)
        
        return groupBox2_t5

    def textchangedTarget(self, curr_target):
        TargetCurrent.append(curr_target.replace(" ", "_"))
    
    def CurrentNExpTime(self, curr_nexptime):
        NExpTimeCurrent.append(curr_nexptime)

    def CurrentNnseq(self, curr_nnseq):
        NnseqCurrent.append(curr_nnseq)

    def CurrentOffset(self, curr_offset):
        OffsetCurrent.append(curr_offset)

    def CurrentGuiding(self, curr_guiding):
        GuidingCurrent.append(curr_guiding)

    def CurrentDirection(self, curr_direction):
        DirCurrent.append(curr_direction)

    def run_NIHTS_NTest(self):
        print('NIHTS ExpTime', str(NExpTimeCurrent[-1]))
        print('Guiding', str(GuidingCurrent[-1]))
    
        current_slit = str(CurrentSlit[-1])
        current_slit_pos = str(CurrentSlitPos[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])
        logging.info('NIHTS Test Exposure: %s second(s): GDR %s' %(current_nexptime, current_guiding))
        
        ##
        # NIHTS_NTest.py
        ##
        """ NIHTS Test - Take NIHTS Test Exposure
            v1.1: 2018-05-14, ag765@nau.edu, A Gustafsson
            
            ** GUI Version - Needs Testing
            
            updates:
            -
            
            """
    
        # Define argument names
        curr_slit = int(current_slit)
        curr_slitpos = int(current_slit_pos)
        n_exptime = float(current_nexptime)
        gdr_str = current_guiding
    
        slitnames = ['sed1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'sed2']
        slit = slitnames[curr_slit]
        slitposition = ['A', 'B', 'cen']
        slit_pos = slitposition[curr_slitpos]
    
        if int(gdr_str) == 1:
            tcs.wait4(True)
        elif int(gdr_str) == 0:
            pass
        
        print('NIHTS Test Exposure:')
        nihts.go(nexp=1, exptime=n_exptime, target='TEST', frame_type='object',  comment1 = 'Slit:'+slit+', Position:'+slit_pos, aborterror=False)
        nihts.wait4nihts()
    
        ##
        #
        ##

    def run_NIHTS_NExp(self):
        print('Target', str(TargetCurrent[-1]))
        print('NIHTS ExpTime', str(NExpTimeCurrent[-1]))
        print('Guiding', str(GuidingCurrent[-1]))
    
        current_target = str(TargetCurrent[-1])
        current_slit = str(CurrentSlit[-1])
        current_slit_pos = str(CurrentSlitPos[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_nnseq = str(NnseqCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])
        current_xexptime = str(XExpTimeCurrent[-1])
        current_coadds = str(CoaddsCurrent[-1])
        logging.info('NIHTS Exposure: %s: %s second(s): GDR %s' %(current_target, current_nexptime, current_guiding))
        
        ##
        # NIHTS_NExp.py
        ##
        """ NIHTS Exposure - Take NIHTS Exposure
            v1.1: 2018-04-12, ag765@nau.edu, A Gustafsson
            
            ** GUI Version - Needs Testing
            
            updates:
            - guiding -- TEST
            
            """
                
        # define arguments
        targetname = current_target
        curr_slit = int(current_slit)
        n_exptime = float(current_nexptime)
        curr_slitpos = int(current_slit_pos)
        gdr_str = current_guiding
        nseq = int(current_nnseq)
        x_exptime = float(current_xexptime)
        x_coadds = int(current_coadds)
        save_n=1
    
        slitnames = ['sed1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'sed2']
        slit = slitnames[curr_slit]
        slitposition = ['A', 'B', 'cen']
        slit_pos = slitposition[curr_slitpos]
         
        print('NIHTS Exposure Sequence Begin:')
        
        for i in range(nseq):
            seq = i+1
            print('STARTING NIHTS SEQUENCE %d/%d' %(seq,nseq))
            
            if int(gdr_str) == 1:
                tcs.wait4(True)
            elif int(gdr_str) == 0:
                pass
        
            nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object', comment1='Slit:'+slit+', Position:'+slit_pos, aborterror=False)
            # take ZTV images while waiting for nihts
            while nihts.isNIHTSready() == False:
                x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)

            nihts.wait4nihts()

            #x.go(x_exptime,x_coadds,1,return_images=False)

            ##
            #
            ##
    
    def run_NIHTS_AB(self):
        print('Target', str(TargetCurrent[-1]))
        print('NIHTS ExpTime', str(NExpTimeCurrent[-1]))
        print('Guiding', str(GuidingCurrent[-1]))

        current_target = str(TargetCurrent[-1])
        current_slit = str(CurrentSlit[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_xexptime = str(XExpTimeCurrent[-1])
        current_coadds = str(CoaddsCurrent[-1])
        current_nnseq = str(NnseqCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])
        
        logging.info('AB Nod Sequence Requested')
        infoBox = QMessageBox()
        infoBox.setText("Have you acquired the target on the A beam position?")
        infoBox.setWindowTitle("AB Nod")
        infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
        infoBox.setEscapeButton(QMessageBox.Close)
        result = infoBox.exec_()
        if result == QMessageBox.Yes:
            print('Yes - Target is acquired on A')
            logging.info('NIHTS AB Sequence Begin...')
            logging.info('AB Parameters: %s: %s second(s): %s sequence(s): GDR %s' %(current_target, current_nexptime, current_nnseq, current_guiding))
            
            ##
            # NIHTS_AB_v4
            ##
            """ NIHTS AB - Performs 1 AB sequence of images.
                v1.5: 2019-03-28, ag765@nau.edu, A Gustafsson
                
                AB Nod Script from position A on slit and returning to A. Adds ZTV looped images. Inputs frame type and slit position into headers. Added guider status. Added for guiding on/off.
                
                ** GUI Version
                
                To use, enter on the command line in the ipython environment:
                run -i NIHTS_AB.py target slit n_exptime x_exptime nseq gdr
                
                uses the editted version of nihts.go
                
                updates:
                - GUIDING on target needs 45 sec wait statement
                """
            
            import time 
            
            # Define argument names
            targetname = current_target
            curr_slit = int(current_slit)
            n_exptime = float(current_nexptime)
            x_exptime = float(current_xexptime)
            x_coadds = int(current_coadds)
            gdr_str = current_guiding
            nseq = int(current_nnseq)
    
            slitnames = ['sed1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'sed2']
            slit = slitnames[curr_slit]
            
            #completed = 0
            #Progress_t5.setValue(completed)

            for i in range(nseq):
                seq = i+1
                print('STARTING AB SEQUENCE %d/%d' %(seq,nseq))
                
                print(gdr_str)
                if int(gdr_str) == 1:
                    print('True')
              
                nihts.wait4nihts()
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
    
                #x.go(x_exptime,x_coadds,1,return_images=False)
        
                # take 1 exposure
                nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit:'+slit+', Position:A', aborterror=False)
                # wait for exposure
                while nihts.isNIHTSready() == False:
                    x.go(x_exptime,x_coadds,1,return_images=False)
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                elif int(gdr_str) == 0:
                    pass
        
                #
                # move target to slit position B
                #
                tcs.move_to_slit_position(tcs.slits[slit]['B'])
                
                nihts.wait4nihts()
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
                
                time.sleep(5) #wait for TCS to get accurate timestamps
    
                # take 1 exposure
                nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit:'+slit+', Position:B', aborterror=False)
                # wait for both exposures to complete plus readout in between
                while nihts.isNIHTSready() == False:
                    x.go(x_exptime,x_coadds,1,return_images=False)
                
                nihts.wait4nihts()
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
    
                #
                # move target to slit position A
                #
                tcs.move_to_slit_position(tcs.slits[slit]['A'])
                
                nihts.wait4nihts()
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass

                time.sleep(5) #wait for TCS to get accurate timestamps
                
                x.go(x_exptime,x_coadds,1,return_images=False)
        
                #completed = np.divide(100,nseq)*(i+1)
                #Progress_t5.setValue(completed)
        
            print('-----AB Exposure Sequence Complete-----')

            ##
            #
            ##
            
            logging.info('... NIHTS AB Sequence End')
        else:
            logging.info('AB Nod Waiting to Acquire Target')
            print('Need to acquire target on A position')
        
        
    def run_NIHTS_ABBA(self):
        print('Target', str(TargetCurrent[-1]))
        print('NIHTS ExpTime', str(NExpTimeCurrent[-1]))
        print('Num Seq', str(NnseqCurrent[-1]))
        print('Guiding', str(GuidingCurrent[-1]))

        current_target = str(TargetCurrent[-1])
        current_slit = str(CurrentSlit[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_xexptime = str(XExpTimeCurrent[-1])
        current_coadds = str(CoaddsCurrent[-1])
        current_nnseq = str(NnseqCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])


        logging.info('ABBA Nod Sequence Requested')
        infoBox = QMessageBox()
        infoBox.setText("Have you acquired the target on the A beam position?")
        infoBox.setWindowTitle("ABBA Nod")
        infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
        infoBox.setEscapeButton(QMessageBox.Close)
        result = infoBox.exec_()
        if result == QMessageBox.Yes:
            print('Yes - Target acquired on A position')
            logging.info('NIHTS ABBA Sequence Begin...')
            logging.info('AB Parameters: %s: %s second(s): %s sequence(s): GDR %s' %(current_target, current_nexptime, current_nnseq, current_guiding))
           
            ##
            # NIHTS_ABBA_v11.py
            ##
            """ NIHTS ABBA - Performs ABBA sequence of images.
                v1.11: 2019-03-28, ag765@nau.edu, A Gustafsson
                
                ABBA Nod Script from position A on slit and returning to A. Adds ZTV looped images. Inputs frame type and slit position into headers. Added guider status. Added for guiding on/off. Save every Nth image enabled for xcam.
                
                To use, enter on the command line in the ipython environment:
                run -i NIHTS_ABBA.py target slit n_exptime opt(-nseq) opt(-x_exptime) opt(-save_n) opt(-gdr_str)
                
                uses the editted version of nihts.go
                
                updates:
                - add save_n
                - Guiding on target needs 45 second wait statement
                """
            import time
            
            # Define argument names
            targetname = current_target
            curr_slit = int(current_slit)
            n_exptime = float(current_nexptime)
            x_exptime = float(current_xexptime)
            x_coadds = int(current_coadds)
            #save_n = int(args.save_n)
            save_n = 1
            gdr_str = current_guiding
            nseq = int(current_nnseq)
    
            slitnames = ['sed1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'sed2']
            slit = slitnames[curr_slit]
    
    
            #completed = 0
            #Progress_t5.setValue(completed)
            
            for i in range(nseq):
                seq = i+1
                print('STARTING ABBA SEQUENCE %d/%d' %(seq,nseq))
        
                tcs.wait4(True) #Added by AG 01/14/21
                #aos.wait4(True) #Added by AG 01/14/21
                nihts.wait4nihts()
                
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
            
                tcs.wait4(True) #Added by AG 01/14/21
                #aos.wait4(True) #Added by AG 01/14/21
                
                # take 1 exposure
                nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit:'+slit+', Position:A', aborterror=False)
                # take ZTV images while waiting for nihts
                while nihts.isNIHTSready() == False:
                    x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)
                
                nihts.wait4nihts()
                tcs.wait4(True) #Added by AG 01/14/21
                #aos.wait4(True) #Added by AG 01/14/21
                
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
                
                tcs.wait4(True) #Added by AG 01/14/21
                #aos.wait4(True) #Added by AG 01/14/21

                #
                # move target to slit position B
                #
                tcs.move_to_slit_position(tcs.slits[slit]['B'])
                
                nihts.wait4nihts()
                tcs.wait4(True) #Added by AG 01/14/21
                #aos.wait4(True) #Added by AG 01/14/21
                
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
                
                tcs.wait4(True) #Added by AG 01/14/21
                #aos.wait4(True) #Added by AG 01/14/21
                time.sleep(5) #NM added 01/13/21 wait for TCS to get accurate timestamps
                        
                # take 2 exposures
                nihts.go(nexp=2, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit:'+slit+', Position:B', aborterror=False)
                # take ZTV images while waiting for nihts
                while nihts.isNIHTSready() == False:
                    x.go(x_exptime,x_coadds,1, return_images=False, save_every_Nth_to_currentfits=save_n)
                
                nihts.wait4nihts()
                tcs.wait4(True) #Added by AG 01/14/21
                #aos.wait4(True) #Added by AG 01/14/21
                
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
                
                tcs.wait4(True) #Added by AG 01/14/21
                #aos.wait4(True) #Added by AG 01/14/21
        
                #
                # move back to position A
                #
                tcs.move_to_slit_position(tcs.slits[slit]['A'])
                # wait for telescope to move
                
                nihts.wait4nihts()
                tcs.wait4(True) #Added by AG 01/14/21
                #aos.wait4(True) #Added by AG 01/14/21
                
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
                
                tcs.wait4(True) #Added by AG 01/14/21
                #aos.wait4(True) #Added by AG 01/14/21
                time.sleep(5) #wait for TCS to get accurate timestamps
        
                # take 1 exposure
                nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit:'+slit+', Position:A', aborterror=False)
                # take ZTV images while waiting for nihts
                while nihts.isNIHTSready() == False:
                    x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                elif int(gdr_str) == 0:
                    pass
                
                tcs.wait4(True) #Added by AG 01/14/21
                #aos.wait4(True) #Added by AG 01/14/21
        
                #completed = np.divide(100,nseq)*(i+1)
                #Progress_t5.setValue(completed)
                        
            print('-----ABBA Exposure Sequence Complete-----')

            ##
            #
            ##

            logging.info('... NIHTS ABBA Sequence End')
        else:
            logging.info('ABBA Nod Waiting to Acquire Target')
            print('Need to acquire target on A position')
    
    
    def run_NIHTS_Offset(self):
        current_offset = str(OffsetCurrent[-1])
        current_direction = str(DirCurrent[-1])
        
        direction = ['UP','DOWN','LEFT','RIGHT','RA','DEC']
        current_dir = direction[int(current_direction)]
        
        print('Offset', current_offset)
        print('Direction', current_dir)

        logging.info('Offset Requested')
        infoBox = QMessageBox()
        infoBox.setText("Would you like to offset the telescope %s arcseconds %s?" %(current_offset, current_dir))
        infoBox.setWindowTitle("Target Offset")
        infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
        infoBox.setEscapeButton(QMessageBox.Close)
        result = infoBox.exec_()
        if result == QMessageBox.Yes:
            print('Yes- Move Telescope')
            logging.info('NIHTS Offset Begin...')
            logging.info('Offset Parameters: %s arcseconds: %s' %(current_offset, current_dir))
            
            ##
            # NIHTS_Offset
            ##
            """ NIHTS Offset
                v1.1: 2018-09-16, ag765@nau.edu, A Gustafsson
                
                ** GUI Version - Needs testing
                
                uses the editted version of nihts.go
                
                updates:
                - Need to switch direction so that it is direction of telescope, not object which is requested
                """
                
            # define arguments
            offset = float(current_offset)
            direction = int(current_direction)
                
            if direction != 4 and direction != 5: # RA and DEC
                offset = np.divide(offset,0.326)
            else:
                pass
                
            #
            # move target to off slit position
            #
            if direction==4: #RA
                ra = offset
                dec = 0
                tcs.send_target_offset(ra, dec, handset=True, tplane=True)

            elif direction==5: #DEC
                ra = 0
                dec = offset
                tcs.send_target_offset(ra, dec, handset=True, tplane=True)
            
            elif direction==3: #RIGHT
                tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(+offset,0))

            elif direction==2: #LEFT
                tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(-offset,0))
            
            elif direction==0: #UP
                #y = +offset
                tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(0,+offset))

            elif direction==1: #DOWN
                tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(0,-offset))

            print('-----Offset Complete-----')

            ##
            #
            ##

            logging.info('... NIHTS Offset End')
        else:
            logging.info('No Offset Applied')
            print('No Offset Applied')

    def run_NIHTS_CenSky(self):
        print('Target', str(TargetCurrent[-1]))
        print('NIHTS ExpTime', str(NExpTimeCurrent[-1]))
        print('Num Seq', str(NnseqCurrent[-1]))
        print('Offset', str(OffsetCurrent[-1]))
        print('Direction', str(DirCurrent[-1]))
        print('Guiding', str(GuidingCurrent[-1]))
        
        current_target = str(TargetCurrent[-1])
        current_slit = str(CurrentSlit[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_xexptime = str(XExpTimeCurrent[-1])
        current_nnseq = str(NnseqCurrent[-1])
        current_coadds = str(CoaddsCurrent[-1])
        current_offset = str(OffsetCurrent[-1])
        current_direction = str(DirCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])
        
        logging.info('Cen-Sky Nod Sequence Requested')
        infoBox = QMessageBox()
        infoBox.setText("Have you acquired the target on the Center position?")
        infoBox.setWindowTitle("Cen-Sky Nod")
        infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
        infoBox.setEscapeButton(QMessageBox.Close)
        result = infoBox.exec_()
        if result == QMessageBox.Yes:
            print('Yes- Acquired target on Center position')
            logging.info('NIHTS Cen-Sky Sequence Begin...')
            logging.info('Cen-Sky Parameters: %s: %s second(s): %s arcseconds: %s: %s sequence(s): GDR %s' %(current_target, current_nexptime, current_offset, current_direction, current_nnseq, current_guiding))
            
            ##
            # NIHTS_CenSky_v3
            ##
            """ NIHTS CenSky - Performs Cen - Off slit sequence of images.
                v1.4: 2019-03-28, ag765@nau.edu, A Gustafsson
                
                Cen-Sky Slit Nod Script from position Cen on slit and returning to Cen. CS-CS-CS-etc... Adds ZTV looped images. Inputs frame type and slit position into headers. Added guiding status yes/no. Option for up/down/left/right or RA/DEC offsets
                
                ** GUI Version
                
                To use, enter on the command line in the ipython environment:
                run -i NIHTS_CenSky.py target slit n_exptime opt(-nseq) opt(-x_exptime) opt(-direction) opt(-offset) opt(-gdr)
                
                uses the editted version of nihts.go
                
                updates:
                - guiding on target needs 45 sec wait statement
                """
            
            import time
            
            # define arguments
            targetname = current_target
            curr_slit = int(current_slit)
            n_exptime = float(current_nexptime)
            nseq = int(current_nnseq)
            x_exptime = float(current_xexptime)
            x_coadds = int(current_coadds)
            offset = float(current_offset)
            direction = int(current_direction)
            gdr_str = current_guiding
                
            slitnames = ['sed1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'sed2']
            slit = slitnames[curr_slit]
            
            if direction != 4 and direction != 5: #RA and DEC
                offset = np.divide(offset,0.326)
            else:
                pass
        
            #completed = 0
            #Progress_t5.setValue(completed)
            
            for i in range(nseq):
                seq = i+1
                print('STARTING Cen-Off SEQUENCE %d/%d' %(seq,nseq))
                
                nihts.wait4nihts()
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
                                
                # take 1 exposure
                nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit:'+slit+', Position:Cen', aborterror=False)
                # take ZTV images while waiting for nihts
                while nihts.isNIHTSready() == False:
                    x.go(x_exptime,x_coadds,1,return_images=False)
                nihts.wait4nihts()
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
                
                #
                # move target to off slit position
                #
                if direction==4: #RA
                    ra = offset
                    dec = 0
                    tcs.send_target_offset(ra, dec, handset=True, tplane=True)
                
                elif direction==5: #DEC
                    ra = 0
                    dec = offset
                    tcs.send_target_offset(ra, dec, handset=True, tplane=True)
                
                elif direction==3: #RIGHT
                    tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(+offset,0))
                
                elif direction==2: #LEFT
                    tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(-offset,0))
                
                elif direction==0: #UP
                    #y = +offset
                    tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(0,+offset))
                
                elif direction==1: #DOWN
                    tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(0,-offset))
                
                nihts.wait4nihts()
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
                
                #time.sleep(5) #wait for TCS to get accurate timestamps
                                
                # take 1 exposure
                nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit: None, Position:Cen', aborterror=False)
                # take ZTV images while waiting for nihts
                while nihts.isNIHTSready() == False:
                    x.go(x_exptime,x_coadds,1,return_images=False)
                nihts.wait4nihts()
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
                
                #
                # move back to position Cen
                #
                #
                if direction==4:
                    ra = offset
                    dec = 0
                    tcs.send_target_offset(-ra, -dec, handset=True, tplane=True)
                
                elif direction==5:
                    ra = 0
                    dec = offset
                    tcs.send_target_offset(-ra, -dec, handset=True, tplane=True)
                
                elif direction==3:
                    tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(-offset,0))
                
                elif direction==2:
                    tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(+offset,0))
                
                elif direction==0:
                    #y = +offset
                    tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(0,-offset))
                
                elif direction==1:
                    tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(0,+offset))
                
                # wait for telescope to move
                nihts.wait4nihts()
                if int(gdr_str) == 1:
                    tcs.wait4(True)
                    time.sleep(5) #time.sleep(45)
                elif int(gdr_str) == 0:
                    pass
                
                #time.sleep(5) #wait for TCS to get accurate timestamps
            
                x.go(x_exptime,x_coadds,1,return_images=False)
            
                #completed = np.divide(100,nseq)*(i+1)
                #Progress_t5.setValue(completed)
                
                print('-----Cen-Off Exposure Sequence Complete-----')
                
                ##
                #
                ##
                
                logging.info('... NIHTS Cen-Sky Sequence End')
        else:
            logging.info('Cen-Sky Nod Waiting to Acquire Target')
            print('Need to acquire target on Center position')


    def run_NIHTS_LMI_Mapping(self):

        logging.info('LMI Move Requested')
        infoBox = QMessageBox()
        infoBox.setText("Would you like to apply an LMI offset to the target?")
        infoBox.setWindowTitle("LMI Acquisition")
        infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
        infoBox.setEscapeButton(QMessageBox.Close)
        result = infoBox.exec_()
        if result == QMessageBox.Yes:
            print('Yes- Move Target on LMI')
            logging.info('NIHTS LMI Move Begin...')
            
            ##
            # NIHTS_LMI_Mapping.py
            ##
            """ NIHTS Offset
                v1.1: 2018-04-12, ag765@nau.edu, A Gustafsson
                
                ** GUI Version - Needs testing
                
                updates:
                -
                """
            
            # define arguments
            xpos = float(XPosLMICurrent[-1])
            ypos = float(YPosLMICurrent[-1])
            home_x = float(XPosLMIDesired[-1])
            home_y = float(YPosLMIDesired[-1])
            if int(CurrentBinning[-1]) == 0:
                binning = 1
            elif int(CurrentBinning[-1]) == 1:
                binning = 2
            elif int(CurrentBinning[-1]) == 2:
                binning = 3
            elif int(CurrentBinning[-1]) == 3:
                binning = 4
            
            pixscale = binning*0.12 #LMI Pixel Scale
            print('LMI Pix Scale: %.2f' %pixscale)

            offset_x = (float(xpos)-float(home_x))*pixscale
            offset_y = (float(ypos)-float(home_y))*pixscale

            print(offset_x, 'Offset in Arcsec EAST')
            print(offset_y, 'Offset in Arcsec SOUTH')
            
            #print('Apply the offset %.2f arcsec East and %.2f arcsec South' %(offset_x, offset_y))
            #print('East is positive, South is positive')
            
            N_pixscale = 0.326 #XCAM Pixel Scale
            
            offset_y_pix = -np.divide(offset_x, 0.326) #East is UP on XCAM so x offset on LMI is y offset on XCAM
            offset_x_pix = np.divide(offset_y, 0.326) #North is RIGHT on XCAM so y offset on LMI is x offset on XCAM

            logging.info('Apply the LMI offset %.2f arcsec East and %.2f arcsec South' %(offset_x, offset_y))
            
            #
            # move target on LMI
            #
            
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(offset_x_pix,offset_y_pix))
        
            print('-----Move Complete-----')
    
            ##
            #
            ##
            
            logging.info('... NIHTS LMI Move End')
        else:
            logging.info('No Move Applied')
            print('No Move Applied')


from datetime import datetime, date, time
UT = str(datetime.utcnow())
UTdate, time = UT.split(" ")
UTday = UTdate.replace("-","")

if __name__ == '__main__':
    app = QApplication([])
    ex = NIHTS()
    
    # check a,b,c,d paths before placing logfile
    #if os.path.exists('/Volumes/dctobsdata/nihts/%sd' %UTday) == True:
    #    filename = '/Volumes/dctobsdata/nihts/%sd/NIHTS_%sd.log' %(UTday, UTday)
    #elif os.path.exists('/Volumes/dctobsdata/nihts/%sc' %UTday) == True:
    #    filename = '/Volumes/dctobsdata/nihts/%sc/NIHTS_%sc.log' %(UTday, UTday)
    #elif os.path.exists('/Volumes/dctobsdata/nihts/%sb' %UTday) == True:
    #    filename = '/Volumes/dctobsdata/nihts/%sb/NIHTS_%sb.log' %(UTday, UTday)
    #else:
    #    filename = '/Volumes/dctobsdata/nihts/%sa/NIHTS_%sa.log' %(UTday, UTday)
    
    filename = '/Users/xcam/Desktop/Log/NIHTS_%sa.log' % UTday

    logging.basicConfig(filename=filename, level=logging.DEBUG, format=FORMAT) # filemode='w' will overwrite instead of append
    logging.info('--- STARTED ---')
    sys.exit(app.exec_())

quit()
