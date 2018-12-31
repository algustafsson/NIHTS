""" NIHTS GUI - NIHTS Exposure Control
    v1.3: 2018-06-04, ag765@nau.edu, A Gustafsson
    
    Creating GUI to avoid scripting. Using PyQt5.
    
    ** OLD NIHTS VERSION
    Runs with NIHTS Scripts
    
    To use, enter on the command line in the ipython environment:
    run -i NIHTS_GUI.py
    
    updates:
    - add exposure time capability for focus
    - add ability to change center of focus script
    - Reconfigure NIHTS Panel -> add general Nod script
    - Terminal Line Toggles on but not off
    - write terminal line script
    - save_n to ABBA script
    - Add status bar
    - set up logging so that it goes in the correct data folder
    - create separate log of information from terminal window
    """

import sys
import os
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

###############################################

import logging
logger = logging.getLogger(__name__)

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

FilterCurrent = []
StepCurrent = []

CurrentSlit = []
CurrentSlitPos = []

XExpTimeCurrent = []
CoaddsCurrent = []

TargetCurrent = []
NExpTimeCurrent = []
GuidingCurrent = []
NnseqCurrent = []
OffsetCurrent = []
DirCurrent = []


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
        self.width = 650
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
    
        def run_NIHTS_Arcs(self):
            logging.info('Arcs Sequence Begin...')
            subprocess.call(['python','/Users/xcam/NIHTS_arcs_v3.py'])
            logging.info('... Arcs Sequence End')
        
        def run_NIHTS_NTestImage(self):
            logging.info('NIHTS Test Exposure: 1 second')
            subprocess.call(['python','/Users/xcam/NIHTS_NTestImage.py'])

        def run_NIHTS_Home(self):
            logging.info('Target is at Home')
            subprocess.call(['python','/Users/xcam/NIHTS_Home.py'])

        def run_NIHTS_XFExp(self):
            logging.info('XCAM Exposure')
            subprocess.call(['python','/Users/xcam/NIHTS_XFExp.py'])

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
        
        FilterCurrent.append(5)
        StepCurrent.append(50)
        
        CurrentSlit.append(1)
        CurrentSlitPos.append(1)
        
        XExpTimeCurrent.append(1)
        CoaddsCurrent.append(1)
        
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
                grid_t1.addWidget(Terminal1(self), 4, 1, 1, 3)
                grid_t2.addWidget(Terminal2(self), 7, 1, 1, 3)
                grid_t3.addWidget(Terminal3(self), 5, 1, 1, 4)
                grid_t4.addWidget(Terminal4(self), 7, 1, 1, 4)
                grid_t5.addWidget(Terminal5(self), 4, 1, 1, 4)
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
        self.tabs.resize(500,200)
        
        ##
        # CREATE TABS
        ##
        self.tabs.addTab(self.tab1,"1. TEST IMAGE")
        self.tabs.addTab(self.tab2,"2. CALIBRATIONS")
        self.tabs.addTab(self.tab3,"3. FOCUS")
        self.tabs.addTab(self.tab4,"4. XCAM")
        self.tabs.addTab(self.tab5,"5. NIHTS")

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
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(run_Exit)
        grid_t1.addWidget(ExitButton, 5, 5, 1, 1)
        
        grid_t1.addWidget(TestLabel1, 1, 1, 1, 5)
        grid_t1.addWidget(TestButton, 2, 3, 1, 1)
        grid_t1.addWidget(TestLabel2, 3, 1, 1, 5)
        grid_t1.addWidget(CheckBox_Comm, 4, 1, 1, 1)
        
        self.tab1.setLayout(grid_t1)

        ##
        # CALIBRATIONS TAB
        ##
        grid_t2 = QGridLayout()
        grid_t2.setSpacing(10)
    
        ArcsLabel = QLabel('Begin Arcs Calibration Sequence')
        ArcsLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        ArcsButton = QPushButton("ARCS")
        ArcsButton.clicked.connect(run_NIHTS_Arcs)
        grid_t2.addWidget(ArcsLabel, 1, 1, 1, 4)
        grid_t2.addWidget(ArcsButton, 2, 2, 1, 1)
        
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
        grid_t2.addWidget(ExitButton, 7, 4, 1, 1)
        
        grid_t2.addWidget(self.createSlitOptions(), 5, 1, 1, 4)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t2.addWidget(CheckBox_Comm, 6, 1, 1, 1)
    
        self.tab2.setLayout(grid_t2)
        
        ##
        # FOCUS TAB
        ##
        grid_t3 = QGridLayout()
        grid_t3.setSpacing(10)
        
        ExposureFButton = QPushButton("Take Exposure") #XCAM Exposure for Focus
        grid_t3.addWidget(ExposureFButton, 1, 2, 1, 2)
        ExposureFButton.clicked.connect(run_NIHTS_XFExp)
        #Add Exposure time button to allow flexibility. default=3s
        
        grid_t3.addWidget(self.createFocusSetup1(), 2, 1, 1, 4)
        grid_t3.addWidget(self.createFocusSetup2(), 3, 1, 1, 4)
        
        FocusButton = QPushButton("FOCUS")
        FocusButton.clicked.connect(self.run_NIHTS_Focus)
        grid_t3.addWidget(FocusButton, 4, 2, 1, 2)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t3.addWidget(CheckBox_Comm, 5, 1, 1, 1)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(run_Exit)
        grid_t3.addWidget(ExitButton, 6, 4, 1, 1)
        
        self.tab3.setLayout(grid_t3)
        
        
        ##
        # XCAM TAB
        ##
        
        grid_t4 = QGridLayout()
        grid_t4.setSpacing(10)
        
        HomeButton = QPushButton("Target is at HOME")
        HomeButton.clicked.connect(run_NIHTS_Home)
        grid_t4.addWidget(HomeButton, 1, 1, 1, 1)
        
        MoveSlit = QLabel('Move to Slit/Pos:')
        MoveSlit.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        grid_t4.addWidget(MoveSlit, 1, 2, 1, 1)
        
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
        
        grid_t4.addWidget(Slit2Box, 1, 3, 1, 1)
        grid_t4.addWidget(Pos2Box, 1, 4, 1, 1)
        
        MoveButton = QPushButton("MOVE")
        MoveButton.clicked.connect(self.run_NIHTS_Move)
        grid_t4.addWidget(MoveButton, 2, 3, 1, 2)
        
        XExpTime = QLabel('Exposure Time')
        XExpTime.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        Coadds = QLabel('# Coadds')
        Coadds.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        Guiding = QLabel('Guiding')
        Guiding.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        grid_t4.setSpacing(10)
    
        #Title2 = QLabel('Setup XCAM Exposure')
        #Title2.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        #grid_t4.addWidget(Title2, 3, 1, 1, 4)
        
        grid_t4.addWidget(XExpTime, 4, 1, 1, 1)
        XExpTimeBox = QSpinBox(self)
        
        grid_t4.addWidget(XExpTimeBox, 4, 2, 1, 1)
        
        XExpTimeBox.setValue(1)
        XExpTimeBox.valueChanged.connect(self.CurrentXExpTime)
        
        grid_t4.addWidget(Coadds, 4, 3, 1, 1)
        CoaddsBox = QSpinBox(self)
        
        grid_t4.addWidget(CoaddsBox, 4, 4, 1, 1)
        
        CoaddsBox.setValue(1)
        CoaddsBox.valueChanged.connect(self.CurrentCoadds)
        
        XExpButton = QPushButton("XCAM")
        XExpButton.clicked.connect(self.run_NIHTS_XExp)
        grid_t4.addWidget(XExpButton, 5, 2, 1, 2)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t4.addWidget(CheckBox_Comm, 6, 1, 1, 1)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(run_Exit)
        grid_t4.addWidget(ExitButton, 7, 4, 1, 1)
        
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
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t5.addWidget(CheckBox_Comm, 6, 1, 1, 1)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(run_Exit)
        grid_t5.addWidget(ExitButton, 7, 4, 1, 1)
        
        self.tab5.setLayout(grid_t5)
        
        ##
        # ADD TABS TO WIDGET
        ##
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    ## TERMINAL COMMAND LINE

    def run_NIHTS_Terminal(self):
        subprocess.call(['python','/Users/xcam/NIHTS_Terminal.py'])

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
        vbox_term1.addWidget(Command1, 1, 1, 1, 1)
        vbox_term1.addWidget(CommandEdit1, 1, 2, 1, 1)

        SendButton1 = QPushButton("Send")
        SendButton1.clicked.connect(self.run_NIHTS_Terminal)
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
        vbox_term2.addWidget(Command2, 1, 1, 1, 1)
        vbox_term2.addWidget(CommandEdit2, 1, 2, 1, 1)
        
        SendButton2 = QPushButton("Send")
        SendButton2.clicked.connect(self.run_NIHTS_Terminal)
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
        vbox_term3.addWidget(Command3, 1, 1, 1, 1)
        vbox_term3.addWidget(CommandEdit3, 1, 2, 1, 1)
        
        SendButton3 = QPushButton("Send")
        SendButton3.clicked.connect(self.run_NIHTS_Terminal)
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
        vbox_term4.addWidget(Command4, 1, 1, 1, 1)
        vbox_term4.addWidget(CommandEdit4, 1, 2, 1, 1)
        
        SendButton4 = QPushButton("Send")
        SendButton4.clicked.connect(self.run_NIHTS_Terminal)
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
        vbox_term5.addWidget(Command5, 1, 1, 1, 1)
        vbox_term5.addWidget(CommandEdit5, 1, 2, 1, 1)
        
        SendButton5 = QPushButton("Send")
        SendButton5.clicked.connect(self.run_NIHTS_Terminal)
        vbox_term5.addWidget(SendButton5, 1, 3, 1, 1)

        groupBox_term5.setLayout(vbox_term5)
        return groupBox_term5
    
    
    global DarksStatus
    def DarksStatus(self):
        infoBox = QMessageBox()
        infoBox.setText("Have you selected your desired slits? ... Are the Deveny 6V Dome Flat Lamps OFF?")
        infoBox.setWindowTitle("Dome Darks Status")
        infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
        infoBox.setEscapeButton(QMessageBox.Close)
        result = infoBox.exec_()
        if result == QMessageBox.Yes:
            print('-----Starting Dome Darks Sequence-----')
            slit_state = [state_0[-1], state_1[-1], state_2[-1], state_3[-1], state_4[-1], state_5[-1], state_6[-1], state_7[-1], state_8[-1]]
            slitnames = ['All', 'SED1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'SED2']
            slits = []
            for i in range(9):
                print(slit_state[i])
                status = bool(slit_state[i])
                print(status)
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
            logging.info('Dome Darks Sequence Begin for slits: %s' %slits)
            subprocess.call(['python','/Users/xcam/NIHTS_flats_darks_v7.py','slit0','slit1','slit2','slit3','slit4','slit5','slit6','slit7','slit8'])
            logging.info('Dome Darks Sequence End for Slits: %s' %slits)
        else:
            print('Turn the Deveny 6V Lamps OFF and try again.')
    
    global FlatsStatus
    def FlatsStatus(self):
        infoBox = QMessageBox()
        infoBox.setText("Have you selected your desired slits? ... Are the Deveny 6V Dome Flat Lamps ON?")
        infoBox.setWindowTitle("Dome Flats Status")
        infoBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
        infoBox.setEscapeButton(QMessageBox.Close)
        result = infoBox.exec_()
        if result == QMessageBox.Yes:
            print('-----Starting Dome Flats Sequence-----')
            slit_state = [state_0[-1], state_1[-1], state_2[-1], state_3[-1], state_4[-1], state_5[-1], state_6[-1], state_7[-1], state_8[-1]]
            slitnames = ['All', 'SED1', '1.34', '0.81', '0.27', '0.54', '1.07', '1.61', 'SED2']
            slits = []
            for i in range(9):
                print(slit_state[i])
                status = bool(slit_state[i])
                print(status)
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
            logging.info('Dome Flats Sequence End for Slits: %s' %slits)
            subprocess.call(['python','/Users/xcam/NIHTS_flats_lamps_v7.py','slit0','slit1','slit2','slit3','slit4','slit5','slit6','slit7','slit8'])
            logging.info('Dome Darks Sequence Begin for slits: %s' %slits)
        else:
            print('Turn the Deveny 6V Lamps ON and try again.')

    ## SLIT BOX
    def createSlitOptions(self):
        
        groupBox = QGroupBox("", self)
        
        slit0 = QCheckBox("ALL", self)
        slit0.stateChanged.connect(self.run_clickBox0)
        
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
    
    def textchangedX(self, xposition):
        XPosCurrent.append(xposition)
    
    def textchangedY(self, yposition):
        YPosCurrent.append(yposition)
    
    def CurrentFilter(self, curr_filter):
        FilterCurrent.append(curr_filter)
    
    def CurrentStep(self, curr_step):
        StepCurrent.append(curr_step)

    def run_NIHTS_Focus(self):
        print(str(XPosCurrent[-1]))
        print(str(YPosCurrent[-1]))
        print(str(FilterCurrent[-1]))
        print(str(StepCurrent[-1]))
        x_starpos = str(XPosCurrent[-1])
        y_starpos = str(YPosCurrent[-1])
        focus_filter = str(FilterCurrent[-1])
        focus_step = str(StepCurrent[-1])
        filter_list = ['OPEN','B','V','R','VR','SDSSg','SDSSr','SDSSi','OIII','Ha_on','Ha_off','WC','WN','CT','BC','GC','RC']
        filter = filter_list[int(focus_filter)]
        logging.info('Focus Sequence Begin...')
        logging.info('Focus Parameters: xpos: %s, ypos: %s, filter: %s, step: %s' %(x_starpos, y_starpos, filter, focus_step))
        subprocess.call(['python','/Users/xcam/NIHTS_Focus_v8.py','x_starpos','y_starpos','focus_filter','focus_step'])
        logging.info('... Focus Sequence End')

    ## XCAM X.GO
    def SlitCurrent(self, curr_slit):
        CurrentSlit.append(curr_slit)
    
    def SlitPosCurrent(self, curr_slit_pos):
        CurrentSlitPos.append(curr_slit_pos)
    
    def run_NIHTS_Move(self):
        print(str(CurrentSlit[-1]))
        print(str(CurrentSlitPos[-1]))
        current_slit = str(CurrentSlit[-1])
        current_slit_pos = str(CurrentSlitPos[-1])
        slit_list = ['SED1', 1.34, 0.81, 0.27, 0.54, 1.07, 1.61, 'SED2']
        pos_list = ['A', 'B', 'CEN']
        slit = slit_list[int(current_slit)]
        slit_pos = pos_list[int(current_slit_pos)]
        logging.info('Move to slit %s at position %s' %(slit, slit_pos))
        subprocess.call(['python','/Users/xcam/NIHTS_Move.py','current_slit','current_slit_pos'])

    def CurrentXExpTime(self, curr_xexptime):
        XExpTimeCurrent.append(curr_xexptime)
    
    def CurrentCoadds(self, curr_coadds):
        CoaddsCurrent.append(curr_coadds)
    
    def run_NIHTS_XExp(self):
        print(str(XExpTimeCurrent[-1]))
        print(str(CoaddsCurrent[-1]))
        current_xexptime = str(XExpTimeCurrent[-1])
        current_coadds = str(CoaddsCurrent[-1])
        logging.info('XCAM Exposure: %s second(s), %s coadds' %(current_xexptime, current_coadds))
        subprocess.call(['python','/Users/xcam/NIHTS_XExp.py','current_xexptime','current_coadds'])

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
        NExpTimeBox = QSpinBox(self)
        vbox_t5.addWidget(NExpTimeBox, 2, 2, 1, 1)
        
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
        
        OffsetBox.setValue(20)
        
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
        print(str(NExpTimeCurrent[-1]))
        print(str(GuidingCurrent[-1]))
    
        current_slit = str(CurrentSlit[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])
        logging.info('NIHTS Test Exposure: %s second(s): GDR %s' %(current_nexptime, current_guiding))
        subprocess.call(['python','/Users/xcam/NIHTS_NTest.py','current_slit','current_nexptime','current_guiding])

    def run_NIHTS_NExp(self):
        print(str(TargetCurrent[-1]))
        print(str(NExpTimeCurrent[-1]))
        print(str(GuidingCurrent[-1]))
    
        current_target = str(TargetCurrent[-1])
        current_slit = str(CurrentSlit[-1])
        current_slit_pos = str(CurrentSlitPos[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])
        logging.info('NIHTS Exposure: %s: %s second(s): : GDR %s' %(current_target, current_nexptime, current_guiding))
        subprocess.call(['python','/Users/xcam/NIHTS/NIHTS_NExp.py','current_target','current_slit','current_nexptime','current_guiding'])

    def run_NIHTS_AB(self):
        print(str(TargetCurrent[-1]))
        print(str(NExpTimeCurrent[-1]))
        print(str(GuidingCurrent[-1]))

        current_target = str(TargetCurrent[-1])
        current_slit = str(CurrentSlit[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_xexptime = str(XExpTimeCurrent[-1])
        current_coadds = str(CoaddsCurrent[-1])
        current_nnseq = str(NnseqCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])

        logging.info('NIHTS AB Sequence Begin...')
        logging.info('AB Parameters: %s: %s second(s): %s sequence(s): GDR %s' %(current_target, current_nexptime, current_nnseq, current_guiding))
        subprocess.call(['python','/Users/xcam/NIHTS_AB_v4.py','current_target','current_slit','current_nexptime','current_xexptime','current_nnseq','current_guiding'])
        logging.info('... NIHTS AB Sequence End')

    def run_NIHTS_ABBA(self):
        print(str(TargetCurrent[-1]))
        print(str(NExpTimeCurrent[-1]))
        print(str(NnseqCurrent[-1]))
        print(str(GuidingCurrent[-1]))

        current_target = str(TargetCurrent[-1])
        current_slit = str(CurrentSlit[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_xexptime = str(XExpTimeCurrent[-1])
        current_coadds = str(CoaddsCurrent[-1])
        current_nnseq = str(NnseqCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])
        
        logging.info('NIHTS ABBA Sequence Begin...')
        logging.info('ABBA Parameters: %s: %s second(s): %s sequence(s): GDR %s' %(current_target, current_nexptime, current_nnseq, current_guiding))
        subprocess.call(['python','/Users/xcam/NIHTS_ABBA_v10.py','current_target','current_slit','current_nexptime','current_xexptime','current_nnseq','current_guiding'])
        logging.info('... NIHTS ABBA Sequence End')
    
    def run_NIHTS_CenSky(self):
        print(str(TargetCurrent[-1]))
        print(str(NExpTimeCurrent[-1]))
        print(str(NnseqCurrent[-1]))
        print(str(OffsetCurrent[-1]))
        print(str(GuidingCurrent[-1]))
        print(str(DirCurrent[-1]))
        
        current_target = str(TargetCurrent[-1])
        current_slit = str(CurrentSlit[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_xexptime = str(XExpTimeCurrent[-1])
        current_nnseq = str(NnseqCurrent[-1])
        current_coadds = str(CoaddsCurrent[-1])
        current_offset = str(OffsetCurrent[-1])
        current_direction = str(DirCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])

        logging.info('NIHTS Cen-Sky Sequence Begin...')
        logging.info('Cen-Sky Parameters: %s: %s second(s): %s arcseconds: %s: %s sequence(s): GDR %s' %(current_target, current_nexptime, current_offset, current_direction, current_nnseq, current_guiding))
        subprocess.call(['python','/Users/xcam/NIHTS_CenSky_v3.py','current_target','current_slit','current_nexptime','current_xexptime','current_nnseq','current_offset','current_direction','current_guiding'])
        logging.info('... NIHTS Cen-Sky Sequence End')


from datetime import datetime, date, time
UT = str(datetime.utcnow())
UTdate, time = UT.split(" ")
UTday = UTdate.replace("-","")

if __name__ == '__main__':
    app = QApplication([])
    ex = NIHTS()
    
    # check a,b,c,d paths before placing logfile
    if os.path.exists('/Volumes/dctobsdata/nihts/%sd' %UTday) == True:
        filename = '/Volumes/dctobsdata/nihts/%sd/NIHTS_%sd.log' %(UTday, UTday)
    elif os.path.exists('/Volumes/dctobsdata/nihts/%sc' %UTday) == True:
        filename = '/Volumes/dctobsdata/nihts/%sc/NIHTS_%sc.log' %(UTday, UTday)
    elif os.path.exists('/Volumes/dctobsdata/nihts/%sb' %UTday) == True:
        filename = '/Volumes/dctobsdata/nihts/%sb/NIHTS_%sb.log' %(UTday, UTday)
    else:
        filename = '/Volumes/dctobsdata/nihts/%sa/NIHTS_%sa.log' %(UTday, UTday)

    logging.basicConfig(filename=filename, level=logging.DEBUG, format=FORMAT) # filemode='w' will overwrite instead of append
    logging.info('--- STARTED ---')
    sys.exit(app.exec_())


quit()
    
    







