""" NIHTS AB - Performs 1 AB sequence of images.
    v1.3: 2018-02-03, ag765@nau.edu, A Gustafsson
    
    AB Nod Script from position A on slit and returning to A. Adds ZTV looped images. Inputs frame type and slit position into headers. Added guider status. Added for guiding on/off.
    
    ** Current version for A to B.
    
    To use, enter on the command line in the ipython environment:
    run -i NIHTS_AB.py target slit n_exptime opt(-x_exptime) opt(-gdr)
    
    uses the editted version of nihts.go
    
    updates:
    -
    """

import argparse

# define command line arguments
parser = argparse.ArgumentParser(description='provide the target name, slit width, NIHTS exposure time, XCAM exposure time, and guiding on/off')
parser.add_argument('target', help='target name (e.g., 2000_VP1)')
parser.add_argument('slit', help='slit (")', choices=['0.27','0.54','0.81','1.07','1.34','1.61','sed1', 'sed2'], default=1.34)
parser.add_argument('n_exptime', help='NIHTS science detector exposure time (s)', default=1)
parser.add_argument('-x_exptime', help='XCAM slit viewing camera exposure time (s)', default=1)
parser.add_argument('-gdr_str', help='guiding on/off', default='False')
args = parser.parse_args()
targetname = args.target
slit = str(args.slit)
n_exptime = float(args.n_exptime)
x_exptime = float(args.x_exptime)
gdr_str = args.gdr_str
gdr = gdr_str.lower() in ("yes","y","true","t","1")

# is the target on the A beam location
status = raw_input("---- Have you acquired the target and sent it to the A beam location? [Y/N]: ----")
if (status.lower()).startswith('n'):
    print("--Please place target at the A position and try again--")

else:

    nihts.wait4nihts()
    tcs.wait4(gdr)
    
    x.go(x_exptime,1,1,return_images=True)

    # take 1 exposure
    nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit: '+slit+', Position: A', aborterror=False)
    # wait for exposure
    while nihts.isNIHTSready() == False:
        x.go(x_exptime,1,1,return_images=False)
    tcs.wait4(gdr)

    
    #
    # move target to slit position B
    #
    tcs.move_to_slit_position(tcs.slits[slit]['B'])
    nihts.wait4nihts()
    tcs.wait4(gdr)

    x.go(x_exptime,1,1,return_images=False)

    
    # take 1 exposure
    nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit: '+slit+', Position: B', aborterror=False)
    # wait for both exposures to complete plus readout in between
    while nihts.isNIHTSready() == False:
        x.go(x_exptime,1,1,return_images=False)
    tcs.wait4(gdr)

    print('-----AB Exposure Sequence Complete-----')

