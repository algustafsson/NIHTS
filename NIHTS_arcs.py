""" NIHTS arcs - Take ARCS.
    v1.2: 2018-01-04, ag765@nau.edu, A Gustafsson
    
    turn on arc lamp, take 5 arc images with 120 second exposures, and turn lamp back off and take one 120 sec No Lamps exposure. Inputs frame type and slit information into headers.
    
    uses the editted version of nihts.go
    
    ** This is the current version!
    
    To use, enter on the command line:
    python NIHTS_arcs.py
    
    updates:
    """

import subprocess

print('Turning Xenon Lamp ON')
subprocess.call("pwrusb setone 3 1", shell=True) #lamp on
subprocess.call("pwrusb status", shell=True)

print('-----Starting Arc Lamp Sequence-----')

nihts.go(nexp=5, exptime=120, target='Comparison', frame_type='comparison', comment1='Slit: None, Position: None', aborterror=False)
# wait for exposures to complete
nihts.wait4nihts()

print('-----Arc Lamp Sequence Complete-----')

# Turn off Arc lamp
print('Turning Xenon Lamp OFF')
subprocess.call("pwrusb setone 3 0", shell=True) #lamp off
subprocess.call("pwrusb status", shell=True)


time.sleep(5)

print('-----Starting No Lamp Sequence-----')

nihts.go(nexp=1, exptime=120, target='Comparison - No Lamps', frame_type='comparison', comment1='Slit: None, Position: None', aborterror=False)
# wait for exposure to complete
nihts.wait4nihts()

print('-----No Lamp Sequence Complete-----')

