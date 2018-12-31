""" NIHTS GUI - NIHTS Exposure Control
    v1.0: 2018-04-12, ag765@nau.edu, A Gustafsson
    
    Creating GUI to avoid scripting. Using PyQt5.
    
    First Version for NIHTS GUI
    Runs with NIHTS Scripts
    Terminal Line Toggles on and Off
    
    To use, enter on the command line in the ipython environment:
    run -i NIHTS_GUI.py
    
    updates:
    
    - save_n to ABBA script
    - add logging
    
    """

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

#import logging
#log = logging.getLogger(__name__)

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
        def run_NIHTS_Arcs(self):
            os.system('python /Users/user/xcam/NIHTS_arcs_v3.py')
        
        def run_NIHTS_NTest(self):
            os.system('python /Users/user/pycode/NIHTS/NIHTS_NTest.py')
        
        def run_NIHTS_XExp(self):
            os.system('python /Users/user/xcam/NIHTS_XExp.py')
        
        def run_NIHTS_Home(self):
            os.system('python /Users/user/xcam/NIHTS_Home.py')
        
        state_0.append(0)
        state_1.append(0)
        state_2.append(0)
        state_3.append(0)
        state_4.append(0)
        state_5.append(0)
        state_6.append(0)
        state_7.append(0)
        state_8.append(0)
        
        XPosCurrent.append(0)
        YPosCurrent.append(0)
        
        FilterCurrent.append(5)
        StepCurrent.append(50)
        
        CurrentSlit.append(1)
        CurrentSlitPos.append(0)
        
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
    
        def run_NIHTS_Flats():
            slit_state = [state_0[-1], state_1[-1], state_2[-1], state_3[-1], state_4[-1], state_5[-1], state_6[-1], state_7[-1], state_8[-1]]
            os.system('python /Users/user/xcam/NIHTS_flats_v6.py %s' % ', '.join(map(str, slit_state)))
        
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

        TestLabel = QLabel('Take NIHTS test image at the start of each LOUI initialization')
        TestLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        TestButton = QPushButton("NIHTS Test Image")
        TestButton.clicked.connect(run_NIHTS_NTest)
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t1.addWidget(CheckBox_Comm, 3, 1, 1, 1)
        
        grid_t1.addWidget(TestLabel, 1, 1, 1, 3)
        grid_t1.addWidget(TestButton, 2, 2, 1, 1)
        
        #grid_t1.addWidget(Terminal1(self), 4, 1, 1, 3)

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
        grid_t2.addWidget(ArcsLabel, 1, 1, 1, 3)
        grid_t2.addWidget(ArcsButton, 2, 2, 1, 1)
        
        FlatsLabel = QLabel('Begin Dome Flats Calibration Sequence')
        FlatsLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        FlatsButton = QPushButton("FLATS")
        grid_t2.addWidget(FlatsLabel, 3, 1, 1, 3)
        grid_t2.addWidget(FlatsButton, 4, 2, 1, 1)
        
        FlatsButton.clicked.connect(run_NIHTS_Flats)
        
        grid_t2.addWidget(self.createSlitOptions(), 5, 1, 1, 3)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t2.addWidget(CheckBox_Comm, 6, 1, 1, 1)
        #grid_t2.addWidget(self.Terminal2(), 7,1,1,3)
    
        self.tab2.setLayout(grid_t2)
        
        ##
        # FOCUS TAB
        ##
        grid_t3 = QGridLayout()
        grid_t3.setSpacing(10)
        
        ExposureButton = QPushButton("Take Exposure")
        grid_t3.addWidget(ExposureButton, 1, 2, 1, 2)
        ExposureButton.clicked.connect(run_NIHTS_XExp)
        
        grid_t3.addWidget(self.createFocusSetup(), 2, 1, 1, 4)
        
        FocusButton = QPushButton("FOCUS")
        FocusButton.clicked.connect(self.run_NIHTS_Focus)
        grid_t3.addWidget(FocusButton, 3, 2, 1, 2)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t3.addWidget(CheckBox_Comm, 4, 1, 1, 1)
        #grid_t3.addWidget(self.Terminal3(), 5,1,1,4)
        
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
        MoveButton.clicked.connect(self.run_TestMove)
        grid_t4.addWidget(MoveButton, 2, 3, 1, 2)
        
        XExpTime = QLabel('Exposure Time')
        Coadds = QLabel('# Coadds')
        Guiding = QLabel('Guiding')
        
        grid_t4.setSpacing(10)
        
        grid_t4.addWidget(XExpTime, 3, 1, 1, 1)
        XExpTimeBox = QSpinBox(self)
        
        grid_t4.addWidget(XExpTimeBox, 3, 2, 1, 2)
        
        XExpTimeBox.setValue(1)
        XExpTimeBox.valueChanged.connect(self.CurrentXExpTime)
        
        grid_t4.addWidget(Coadds, 4, 1, 1, 1)
        CoaddsBox = QSpinBox(self)
        
        grid_t4.addWidget(CoaddsBox, 4, 2, 1, 2)
        
        CoaddsBox.setValue(1)
        CoaddsBox.valueChanged.connect(self.CurrentCoadds)
        
        XGoButton = QPushButton("GO")
        XGoButton.clicked.connect(self.run_NIHTS_XExp)
        grid_t4.addWidget(XGoButton, 5, 2, 1, 1)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t4.addWidget(CheckBox_Comm, 6, 1, 1, 1)
        #grid_t4.addWidget(self.Terminal4(), 7,1,1,4)
        
        self.tab4.setLayout(grid_t4)
        
        ##
        # NIHTS TAB
        ##
        grid_t5 = QGridLayout()
        grid_t5.setSpacing(10)
        
        grid_t5.addWidget(self.createNIHTSSetup1(), 1, 1, 1, 4)
        
        NIHTSTestButton = QPushButton("NIHTS Test")
        grid_t5.addWidget(NIHTSTestButton, 2, 1, 1, 2)
        
        NIHTSButton = QPushButton("NIHTS")
        grid_t5.addWidget(NIHTSButton, 2, 3, 1, 2)
        
        ABButton = QPushButton("AB")
        ABButton.clicked.connect(self.run_TestAB)
        grid_t5.addWidget(ABButton, 3, 1, 1, 2)
        
        ABBAButton = QPushButton("ABBA")
        ABBAButton.clicked.connect(self.run_TestABBA)
        grid_t5.addWidget(ABBAButton, 3, 3, 1, 2)
        
        grid_t5.addWidget(self.createNIHTSSetup2(), 4, 1, 1, 4)
        
        CenOffButton = QPushButton("CEN-OFF")
        CenOffButton.clicked.connect(self.run_TestCenOff)
        grid_t5.addWidget(CenOffButton, 5, 3, 1, 2)
        
        CheckBox_Comm = QCheckBox("Command Line")
        CheckBox_Comm.stateChanged.connect(run_toggleCommandLine)
        grid_t5.addWidget(CheckBox_Comm, 6, 1, 1, 1)
        
        self.tab5.setLayout(grid_t5)
        
        
        ##
        # ADD TABS TO WIDGET
        ##
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    ## TERMINAL COMMAND LINE

    def run_Terminal(self):
        os.system('python /Users/user/pycode/NIHTS/TestTerminal.py')

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
        CommandEdit1.addItem("NIHTS_CenOff.py target slit n_exptime")
        CommandEdit1.setEditable(True)
        vbox_term1.addWidget(Command1, 1, 1, 1, 1)
        vbox_term1.addWidget(CommandEdit1, 1, 2, 1, 1)

        SendButton1 = QPushButton("Send")
        SendButton1.clicked.connect(self.run_Terminal)
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
        CommandEdit2.addItem("NIHTS_CenOff.py target slit n_exptime")
        CommandEdit2.setEditable(True)
        vbox_term2.addWidget(Command2, 1, 1, 1, 1)
        vbox_term2.addWidget(CommandEdit2, 1, 2, 1, 1)
        
        SendButton2 = QPushButton("Send")
        SendButton2.clicked.connect(self.run_Terminal)
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
        CommandEdit3.addItem("NIHTS_CenOff.py target slit n_exptime")
        CommandEdit3.setEditable(True)
        vbox_term3.addWidget(Command3, 1, 1, 1, 1)
        vbox_term3.addWidget(CommandEdit3, 1, 2, 1, 1)
        
        SendButton3 = QPushButton("Send")
        SendButton3.clicked.connect(self.run_Terminal)
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
        CommandEdit4.addItem("NIHTS_CenOff.py target slit n_exptime")
        CommandEdit4.setEditable(True)
        vbox_term4.addWidget(Command4, 1, 1, 1, 1)
        vbox_term4.addWidget(CommandEdit4, 1, 2, 1, 1)
        
        SendButton4 = QPushButton("Send")
        SendButton4.clicked.connect(self.run_Terminal)
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
        CommandEdit5.addItem("NIHTS_CenOff.py target slit n_exptime")
        CommandEdit5.setEditable(True)
        vbox_term5.addWidget(Command5, 1, 1, 1, 1)
        vbox_term5.addWidget(CommandEdit5, 1, 2, 1, 1)
        
        SendButton5 = QPushButton("Send")
        SendButton5.clicked.connect(self.run_Terminal)
        vbox_term5.addWidget(SendButton5, 1, 3, 1, 1)

        groupBox_term5.setLayout(vbox_term5)
        return groupBox_term5
    
    
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
    def createFocusSetup(self):
    
        groupBox_t3 = QGroupBox("")
        vbox_t3 = QGridLayout()
    
        XPos = QLabel('X Pos')
        XPos.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        YPos = QLabel('Y Pos')
        YPos.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        Filter = QLabel('LMI Filter')
        Step = QLabel('Step Size')
        
        #global XPosCurrent
        #global YPosCurrent
        #global XPosEdit
        #global YPosEdit
        #global FilterBox
        
        XPosEdit = QLineEdit()
        XPosEdit.textChanged.connect(self.textchangedX)
        YPosEdit = QLineEdit()
        YPosEdit.textChanged.connect(self.textchangedY)
        
        vbox_t3.setSpacing(10)
        
        vbox_t3.addWidget(XPos, 1, 1, 1, 1)
        vbox_t3.addWidget(XPosEdit, 1, 2, 1, 1)
        
        vbox_t3.addWidget(YPos, 1, 3, 1, 1)
        vbox_t3.addWidget(YPosEdit, 1, 4, 1, 1)
        
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
        vbox_t3.addWidget(Filter, 2, 1, 1, 2)
        vbox_t3.addWidget(FilterBox, 2, 2, 1, 2)
        
        FilterBox.setCurrentIndex(5)
        FilterBox.currentIndexChanged.connect(self.CurrentFilter)
        
        vbox_t3.addWidget(Step, 3, 1, 1, 1)
        StepBox = QSpinBox(self)
        vbox_t3.addWidget(StepBox, 3, 2, 1, 2)
        
        StepBox.setValue(50)
        StepBox.valueChanged.connect(self.CurrentStep)
        
        groupBox_t3.setLayout(vbox_t3)
        
        return groupBox_t3
    
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
        current_xexptime = str(XExpTimeCurrent[-1])
        focus_filter = str(FilterCurrent[-1])
        focus_step = str(StepCurrent[-1])
        os.system('python /Users/user/xcam/NIHTS/NIHTS_Focus.py %s %s %s %s' % (x_starpos, y_starpos, current_xexptime, focus_filter, focus_step))
    
    
    ## XCAM X.GO
    def SlitCurrent(self, curr_slit):
        CurrentSlit.append(curr_slit)
    
    def SlitPosCurrent(self, curr_slit_pos):
        CurrentSlitPos.append(curr_slit_pos)
    
    def run_TestMove(self):
        print(str(CurrentSlit[-1]))
        print(str(CurrentSlitPos[-1]))
        current_slit = str(CurrentSlit[-1])
        current_slit_pos = str(CurrentSlitPos[-1])
        os.system('python /Users/user/pycode/NIHTS/TestMove.py %s %s' % (current_slit, current_slit_pos))
    
    def CurrentXExpTime(self, curr_xexptime):
        XExpTimeCurrent.append(curr_xexptime)
    
    def CurrentCoadds(self, curr_coadds):
        CoaddsCurrent.append(curr_coadds)
    
    def run_NIHTS_XExp(self):
        print(str(XExpTimeCurrent[-1]))
        print(str(CoaddsCurrent[-1]))
        current_xexptime = str(XExpTimeCurrent[-1])
        current_coadds = str(CoaddsCurrent[-1])
        os.system('python /Users/user/xcam/NIHTS_XExp.py %s %s' % (current_xexptime, current_coadds))
    
    def run_NIHTS_NExp(self):
        current_target = str(TargetCurrent[-1])
        current_slit = str(CurrentSlit[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_slit_pos = str(CurrentSlitPos[-1])
        os.system('python /Users/user/xcam/NIHTS_NExp.py %s %s' % (current_target, current_nexptime, current_slit, current_slit_pos))
    
    ## NIHTS Setup Box
    def createNIHTSSetup1(self):
        
        groupBox1_t5 = QGroupBox("")
        vbox_t5 = QGridLayout()
        
        Target = QLabel('Target')
        Target.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        Guiding = QLabel('Guiding')
        
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
        NumSeq = QLabel('# Seq')
        
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
        
        Offset = QLabel('Offset')
        Direction = QLabel('Direction')
        
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
        TargetCurrent.append(curr_target)

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




    def run_NIHTS_AB(self):
        print(str(TargetCurrent[-1]))
        print(str(NExpTimeCurrent[-1]))
        print(str(GuidingCurrent[-1]))

        current_target = str(TargetCurrent[-1])
        current_slit = str(CurrentSlit[-1])
        current_nexptime = str(NExpTimeCurrent[-1])
        current_xexptime = str(XExpTimeCurrent[-1])
        current_nnseq = str(NnseqCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])

        os.system('python /Users/user/xcam/NIHTS_AB_v4.py %s %s %s %s %s %s' % (current_target, current_slit, current_nexptime, current_xexptime, current_nnseq, current_guiding))

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

        os.system('python /Users/user/xcam/NIHTS_ABBA_v10.py %s %s %s %s %s %s' % (current_target, current_slit, current_nexptime, current_xexptime, current_coadds, current_nnseq, current_guiding))

    def run_NIHTS_CenOff(self):
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
        current_offset = str(OffsetCurrent[-1])
        current_direction = str(DirCurrent[-1])
        current_guiding = str(GuidingCurrent[-1])

        os.system('python /Users/user/xcam/NIHTS_CenOff_v3.py %s %s %s %s %s %s %s %s' % (current_target, current_slit, current_nexptime, current_xexptime, current_nnseq, current_offset, current_direction, current_guiding))



if __name__ == '__main__':
    app = QApplication([])
    ex = NIHTS()
    sys.exit(app.exec_())


quit()
    
    







