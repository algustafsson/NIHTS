""" NIHTS Nod - Performs 0.54-Cen to 1.34-Cen nod sequence of images.
    v1.0: 2018-04-13, ag765@nau.edu, A Gustafsson

    
    ** Current version for 0.54-Cen to 1.34-Cen.
    
    To use, enter on the command line in the ipython environment:
    run -i NIHTS_Nod.py target n_exptime n_numexp opt(-nseq) opt(-x_exptime) opt(-save_n) opt(-gdr_str)
    
    uses the editted version of nihts.go
    
    updates:
    -
    """

import argparse

# define command line arguments
parser = argparse.ArgumentParser(description='provide the target name, NIHTS exposure time, number of sequences, XCAM exposure time, and guiding on/off')
parser.add_argument('target', help='target name (e.g., 2000_VP1)')
parser.add_argument('n_exptime', help='NIHTS science detector exposure time (s)', default=1)
parser.add_argument('n_numexp', help='NIHTS science detector number of exposures', default=1)
parser.add_argument('-nseq', help='number of ABBA sequences', default=1)
parser.add_argument('-x_exptime', help='XCAM slit viewing camera exposure time (s)', default=1)
parser.add_argument('-x_coadds', help='XCAM slit viewing camera number of coadds', default=1)
parser.add_argument('-save_n', help='save every Nth slit viewing camera image to disk', default=1)
parser.add_argument('-gdr_str', help='guiding on/off', default='False')
args = parser.parse_args()
targetname = args.target
n_exptime = float(args.n_exptime)
n_numexp = float(args.n_numexp)
nseq = int(args.nseq)
x_exptime = float(args.x_exptime)
x_coadds = int(args.x_coadds)
save_n = int(args.save_n)
gdr_str = args.gdr_str
gdr = gdr_str.lower() in ("yes","y","true","t","1")


# is the target on the A beam location
status = raw_input("---- Have you acquired the target and sent it to the 0.54-Cen Beam location? [Y/N]: ----")
if (status.lower()).startswith('n'):
    print("--Please place target on 0.54-Cen position and try again--")

else:
    for i in range(nseq):
        seq = i+1
        print('STARTING Nod SEQUENCE %d/%d' %(seq,nseq))
    
        nihts.wait4nihts()
        tcs.wait4(gdr)

        x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)

        # take N exposures
        nihts.go(nexp=n_numexp, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit: 0.54, Position: Cen', aborterror=False)
        # take ZTV images while waiting for nihts
        while nihts.isNIHTSready() == False:
            x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)
        tcs.wait4(gdr)
    
        #
        # move target to 1.34-Cen
        #
        tcs.move_to_slit_position(tcs.slits['1.34']['cen'])
        nihts.wait4nihts()
        tcs.wait4(gdr)

        x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)

    
        # take N exposures
        nihts.go(nexp=n_numexp, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit: 1.34, Position: Cen', aborterror=False)
        # take ZTV images while waiting for nihts
        while nihts.isNIHTSready() == False:
            x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)
        tcs.wait4(gdr)
    
        #
        # move back to position 0.54-Cen
        #
        tcs.move_to_slit_position(tcs.slits['0.54']['cen'])
        # wait for telescope to move
        nihts.wait4nihts()
        tcs.wait4(gdr)

        x.go(x_exptime,x_coadds,1,return_images=False,save_every_Nth_to_currentfits=save_n)


    print('-----ABBA Exposure Sequence Complete-----')

