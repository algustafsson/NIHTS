""" NIHTS ABBA - Performs ABBA sequence of images.
    v1.8: 2018-03-23, ag765@nau.edu, A Gustafsson
    
    ABBA Nod Script from position A on slit and returning to A. Adds ZTV looped images. Inputs frame type and slit position into headers. Added guider status. Added for guiding on/off. Save every Nth image enabled for xcam.
    
    ** Current version for A to A.
    
    To use, enter on the command line in the ipython environment:
    run -i NIHTS_ABBA.py target slit n_exptime opt(-nseq) opt(-x_exptime) opt(-save_n) opt(-gdr_str)
    
    uses the editted version of nihts.go
    
    updates:
    -
    """

import argparse

# define command line arguments
parser = argparse.ArgumentParser(description='provide the target name, slit width, NIHTS exposure time, number of sequences, XCAM exposure time, and guiding on/off')
parser.add_argument('target', help='target name (e.g., 2000_VP1)')
parser.add_argument('slit', help='slit (")', choices=['0.27','0.54','0.81','1.07','1.34','1.61','sed1', 'sed2'], default=1.34)
parser.add_argument('n_exptime', help='NIHTS science detector exposure time (s)', default=1)
parser.add_argument('-nseq', help='number of ABBA sequences', default=1)
parser.add_argument('-x_exptime', help='XCAM slit viewing camera exposure time (s)', default=1)
parser.add_argument('-x_coadds', help='XCAM slit viewing camera number of coadds', default=1)
parser.add_argument('-save_n', help='save every Nth slit viewing camera image to disk', default=1)
parser.add_argument('-gdr_str', help='guiding on/off', default='False')
args = parser.parse_args()
targetname = args.target
n_exptime = float(args.n_exptime)
slit = str(args.slit)
nseq = int(args.nseq)
x_exptime = float(args.x_exptime)
x_coadds = int(args.x_coadds)
save_n = int(args.save_n)
gdr_str = args.gdr_str
gdr = gdr_str.lower() in ("yes","y","true","t","1")


# is the target on the A beam location
status = raw_input("---- Have you acquired the target and sent it to the A Beam location? [Y/N]: ----")
if (status.lower()).startswith('n'):
    print("--Please place target on A position and try again--")

else:
    for i in range(nseq):
        seq = i+1
        print('STARTING ABBA SEQUENCE %d/%d' %(seq,nseq))
    
        nihts.wait4nihts()
        tcs.wait4(gdr)

        x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)

        # take 1 exposure
        nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit: '+slit+', Position: A', aborterror=False)
        # take ZTV images while waiting for nihts
        while nihts.isNIHTSready() == False:
            x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)
        tcs.wait4(gdr)
    
        #
        # move target to slit position B
        #
        tcs.move_to_slit_position(tcs.slits[slit]['B'])
        nihts.wait4nihts()
        tcs.wait4(gdr)

        x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)

    
        # take 2 exposures
        nihts.go(nexp=2, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit: '+slit+', Position: B', aborterror=False)
        # take ZTV images while waiting for nihts
        while nihts.isNIHTSready() == False:
            x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)
        tcs.wait4(gdr)
    
        #
        # move back to position A
        #
        tcs.move_to_slit_position(tcs.slits[slit]['A'])
        # wait for telescope to move
        nihts.wait4nihts()
        tcs.wait4(gdr)

        x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)

    
        # take 1 exposure
        nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit: '+slit+', Position: A', aborterror=False)
        # take ZTV images while waiting for nihts
        while nihts.isNIHTSready() == False:
            x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)
        tcs.wait4(gdr)


    print('-----ABBA Exposure Sequence Complete-----')

