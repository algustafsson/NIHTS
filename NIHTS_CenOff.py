""" NIHTS CenOff - Performs Cen - Off slit sequence of images.
    v1.2: 2018-02-02, ag765@nau.edu, A Gustafsson
    
    Cen-Off Slit Nod Script from position Cen on slit and returning to Cen. CO-CO-CO-etc... Adds ZTV looped images. Inputs frame type and slit position into headers. Added guiding status yes/no. Option for up/down/left/right or RA/DEC offsets
    
    ** TEST - Current version for Cen to Off.
    
    To use, enter on the command line in the ipython environment:
    run -i NIHTS_CenOff.py target slit n_exptime opt(-nseq) opt(-x_exptime) opt(-direction) opt(-offset) opt(-gdr)
    
    uses the editted version of nihts.go
    
    updates:
    -
    """

import argparse

# define command line arguments
parser = argparse.ArgumentParser(description='provide the target name, slit width, NIHTS exposure time, number of sequences, XCAM exposure time, offset amount, direction of offset, and guiding on/off')
parser.add_argument('target', help='target name (e.g., 2000_VP1)')
parser.add_argument('slit', help='slit (")', choices=['0.27','0.54','0.81','1.07','1.34','1.61','sed1', 'sed2'], default=1.34)
parser.add_argument('n_exptime', help='NIHTS science detector exposure time (s)', default=1)
parser.add_argument('-nseq', help='number of ABBA sequences', default=1)
parser.add_argument('-x_exptime', help='XCAM slit viewing camera exposure time (s)', default=1)
parser.add_argument('-direction', help='direction of offset (RA/DEC)', choices=['RA','DEC', 'RIGHT', 'LEFT', 'UP', 'DOWN'], default='UP')
parser.add_argument('-offset', help='offset ('')', default=20)
parser.add_argument('-gdr_str', help='guiding on/off', default='False')
args = parser.parse_args()
targetname = args.target
slit = str(args.slit)
n_exptime = float(args.n_exptime)
nseq = int(args.nseq)
x_exptime = float(args.x_exptime)
offset = float(args.offset)
direction = str(args.direction)
gdr_str = args.gdr_str
gdr = gdr_str.lower() in ("yes","y","true","t","1")

# is the target on the cen beam location
status = raw_input("---- Have you acquired the target and sent it to the Cen Beam location? [Y/N]: ----")
if (status.lower()).startswith('n'):
    print("--Please place target on Cen position and try again--")

else:

    for i in range(nseq):
        seq = i+1
        print('STARTING Cen-Off SEQUENCE %d/%d' %(seq,nseq))
    
        nihts.wait4nihts()
        tcs.wait4(gdr)

        x.go(x_exptime,1,1,return_images=True)

        # take 1 exposure
        nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit: '+slit+', Position: Cen', aborterror=False)
        # take ZTV images while waiting for nihts
        while nihts.isNIHTSready() == False:
            x.go(x_exptime,1,1,return_images=False)
        tcs.wait4(gdr)
    
        #
        # move target to off slit position
        #
        if direction=='RA':
            ra = offset
            dec = 0
            tcs.send_target_offset(ra, dec, handset=True, tplane=True)
                
        elif direction=='DEC':
            ra = 0
            dec = offset
            tcs.send_target_offset(ra, dec, handset=True, tplane=True)

        elif direction=='RIGHT':
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(+offset,0))

        elif direction=='LEFT':
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(-offset,0))

        elif direction=='UP':
            y = +offset
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(0,+offset))

        elif direction=='DOWN':
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(0,-offset))

        nihts.wait4nihts()
        tcs.wait4(gdr)

        x.go(x_exptime,1,1,return_images=False)

    
        # take 1 exposure
        nihts.go(nexp=1, exptime=n_exptime, target=targetname, frame_type='object',  comment1 = 'Slit: None, Position: Cen', aborterror=False)
        # take ZTV images while waiting for nihts
        while nihts.isNIHTSready() == False:
            x.go(x_exptime,1,1,return_images=False)
        tcs.wait4(gdr)
    
        #
        # move back to position Cen
        #
        #
        if direction=='RA':
            ra = offset
            dec = 0
            tcs.send_target_offset(-ra, -dec, handset=True, tplane=True)

        elif direction=='DEC':
            ra = 0
            dec = offset
            tcs.send_target_offset(-ra, -dec, handset=True, tplane=True)

        elif direction=='RIGHT':
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(-offset,0))
        
        elif direction=='LEFT':
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(+offset,0))

        elif direction=='UP':
            y = +offset
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(0,-offset))
        
        elif direction=='DOWN':
            tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(0,+offset))

        # wait for telescope to move
        nihts.wait4nihts()
        tcs.wait4(gdr)


    print('-----Cen-Off Exposure Sequence Complete-----')

