""" NIHTS FLATS - Take Dome Flats.
    v1.5: 2018-1-04, ag765@nau.edu, A Gustafsson
    
    Take 10 exposures at each exposure time from 1 - 20 seconds. Records frame type and slit information into headers. 4.03 slit is called sed1 and sed2.
    
    
    ** This is the Current version!
    
    To use, enter on the command line:
    run -i NIHTS_flats.py
    
    updates:
    - 
    """

import subprocess

# make sure arc lamp is turned off
print('Confirming ARC lamp is turned off')
subprocess.call("pwrusb setone 3 0", shell=True)


print('-----Starting Dome Flats Sequence of Thermal Profiles-----')


status = raw_input("--- Are the Flat Lamps OFF? [Y/N]: ---")
if (status.lower()).startswith('n'):
    print("--Turn off the lamps and try again--")

else:

    exposure_time = [1,3,6,15,7,4,2,1]
    nexp=1
    slit = ['sed1', 1.34, 0.81, 0.27, 0.54, 1.07, 1.61, 'sed2']

    for i in range(len(exposure_time)):
        print('Current Exposure Time', exposure_time[i])
        nihts.go(nexp=nexp, exptime=exposure_time[i], target='Dome Flats - No Lamps', frame_type='dome flat', comment1 = 'Slit: '+str(slit[i])+', Position: None', aborterror=False)
        # wait for exposures to complete
        nihts.wait4nihts()

    print('-----Dome Flats Sequence of Thermal Profiles Complete-----')


    status = raw_input("--- Ask the operator to turn on the Deveny 6V Lamps... Ready? [Y/N]: ---")
    if (status.lower()).startswith('n'):
        print("--Turn on the lamps and try again--")

    else:

        print('-----Starting Dome Flats Sequence-----')

        exposure_time = [1,3,6,15,7,4,2,1]
        nexp=10

        for i in range(len(exposure_time)):
            print('Current Exposure Time', exposure_time[i])
            nihts.go(nexp=nexp, exptime=exposure_time[i], target='Dome Flats', frame_type='dome flat', comment1 = 'Slit: '+str(slit[i])+', Position: None', aborterror=False)
            # wait for exposures to complete
            nihts.wait4nihts()

        print('-----Dome Flats Sequence Complete-----')
