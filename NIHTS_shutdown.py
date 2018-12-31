""" NIHTS Shutdown
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
