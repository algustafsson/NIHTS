""" NIHTS FOCUS - Runs a focus script.
    v1.7: 2018-04-14, ag765@nau.edu, A Gustafsson
    
    Focus NIHTS for LMI filter. Standalone.
    
    set LMI filter and step size. script changes focus 11 times stepping through the nominal value (determined from filter). script throws these x.go images into a focus folder. Here it takes a 30" box around the star and calculates FWHM in both x and y for each image. It then plots the FWHM ('') vs Focus and fits a polynomial to determine best fit.
    
    - set exposure time -- right now hard coded at 3sec
    - nominal focus set to 810
    - create new focus directory each time you run focus script with time stamp
    - x and y gaussian fits
    
    
    ** NEEDS TESTING
    
    
    To use, enter on the command line in the ipython environment:
    run -i NIHTS_focus.py xpos ypos opt(-filter) opt(-seeing) opt(-x_exptime) opt(-step) opt(-gdr_string)
    
    updates:
    - 3-5 exposures at each step for weighted fit
    - determine step size based on seeing
    
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


# define command line arguments
parser = argparse.ArgumentParser(description='provide the LMI filter, x position of star, y position of star, seeing desired step size (microns), and guiding on/off')
parser.add_argument('xpos', help='x pixel position of star')
parser.add_argument('ypos', help='y pixel position of star')
parser.add_argument('-filter', help='LMI filter', choices=['OPEN','B','V','R','VR','SDSSg','SDSSr','SDSSi','OIII','Ha_on','Ha_off','WC','WN','CT','BC','GC','RC'], default='SDSSr')
parser.add_argument('-seeing', help='estimated seeing ('')', default = 2)
parser.add_argument('-x_exptime', help='slit camera exposure time (s)', default=3)
parser.add_argument('-step', help='step size (microns)', default=50)
parser.add_argument('-gdr_str', help='guiding on/off', default='False')
args = parser.parse_args()
xpos = int(args.xpos)
ypos = int(args.ypos)
filter = str(args.filter)
seeing = float(args.seeing)
x_exptime = float(args.x_exptime)
step = float(args.step)
gdr_str = args.gdr_str
gdr = gdr_str.lower() in ("yes","y","true","t","1")

#### LMI Filter/Dichroic Dictionary

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

print('--- Ask the TO to move the dichroic position to %s mm---' % dichroic)

# is the dichroic in place?
status = raw_input("--- Is the dichroic in place? [Y/N]: ---")
if (status.lower()).startswith('n'):
    print("--Please wait for dichroic and try again--")

else:
    
    ####
    
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
        if file.endswith('.fits') and 'current' not in file:
            files.append(file)
    last_file = files[-1]
    print('last file',last_file)

    prefix, num = last_file.split('_')
    number, suffix = num.split('.')

    ####

    tcs.wait4(gdr)
    
    nom_focus = 810  #Nominal is 810 AG 02/26
    tcs.send_focus_microns(nom_focus)
    print('--- Nominal Focus value is 810 microns ---')

    # take background image
    nihts.wait4nihts()
    tcs.wait4(gdr)
    print(' --- Creating Background Image ---')
    tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(-50,0))

    nihts.wait4nihts()
    tcs.wait4(gdr)

    x.go(x_exptime,1,1,return_images=True)

    nihts.wait4nihts()
    tcs.wait4(gdr)

    tcs.move_object_on_xcam(tcs.current_target_pt, tcs.current_target_pt + wx.RealPoint(+50,0))

    nihts.wait4nihts()
    tcs.wait4(gdr)

    # take focus images
    print('----------------------- \n Beginning Focus Sequence \n ------------------------')
    
    focus_list = []
    for j in range(7):
        focus = nom_focus+offset+(j-3)*step
        print('---------------- \n Focus value: %f \n -----------------' % focus)
        tcs.send_focus_microns(focus)
        focus_list.append(focus)
        
        nihts.wait4nihts()
        tcs.wait4(gdr)
        
        for k in range(2):
            #take image
            x.go(x_exptime,1,1,return_images=True)

            nihts.wait4nihts()
            tcs.wait4(gdr)
    
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

        x_pos= xpos
        y_pos= ypos
        
        image_data_star = image_data[y_pos-30:y_pos+30, x_pos-30:x_pos+30] - fits.getdata(current_focus_dir + '/' + bkg)[0][y_pos-30:y_pos+30, x_pos-30:x_pos+30]

        plt.ion()
        plt.figure(1)
        plt.imshow(image_data_star, cmap='gray')
        plt.pause(0.0001)
        plt.scatter([30], [30], c='r', marker ='x', s=100)
        plt.pause(0.0001)
        time.sleep(1)
        plt.close()

        star_flat_x = np.array(np.sum(image_data_star, axis=0))
        star_flat_y = np.array(np.sum(image_data_star, axis=1))

        xrange = np.arange(0,60,1)
        mean_x = np.divide(np.sum(xrange*np.array(star_flat_x)),np.sum(np.array(star_flat_x)))
        sigma_x = np.sqrt([np.divide(np.sum(star_flat_x*((xrange-mean_x)**2)),(np.sum(star_flat_x)))])
        line_fit_coeff_x = np.polyfit(xrange, star_flat_x, 1, full=True)
        line_fit_x = line_fit_coeff_x[0][0]*np.power(xrange,1) + line_fit_coeff_x[0][1]
        zero_star_x = star_flat_x

        yrange = np.arange(0,60,1)
        mean_y = np.divide(np.sum(yrange*np.array(star_flat_y)),np.sum(np.array(star_flat_y)))
        sigma_y = np.sqrt([np.divide(np.sum(star_flat_y*((yrange-mean_y)**2)),(np.sum(star_flat_y)))])
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
        plt.plot(X, Gauss_x(X, *popt_x), 'g-', label='fit_x')
        plt.pause(0.0001)
        plt.plot(Y, zero_star_y, 'b+:', label='data_y')
        plt.pause(0.0001)
        plt.plot(Y, Gauss_y(Y, *popt_y), 'r-', label='fit_y')
        plt.pause(0.0001)
        plt.legend()
        plt.title('')
        plt.xlabel('Pixels')
        plt.ylabel('Intensity')
        time.sleep(1)
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
    focus_new = np.arange(nom_focus+offset+(-3)*step, nom_focus+offset+(3)*step, 0.001)

    ## polyfit -- short (2nd order)
    fit_coeff_x = np.polyfit(focus_values, FWHM_x, 2, full=True)
    fit_x_short = fit_coeff_x[0][0]*np.power(focus_values,2) + fit_coeff_x[0][1]*np.power(focus_values,1)+ fit_coeff_x[0][2]
    ## polyfit (2nd order)
    fit_x = fit_coeff_x[0][0]*np.power(focus_new,2) + fit_coeff_x[0][1]*np.power(focus_new,1)+ fit_coeff_x[0][2]

    fit_coeff_y = np.polyfit(focus_values, FWHM_y, 2, full=True)
    fit_y_short = fit_coeff_y[0][0]*np.power(focus_values,2) + fit_coeff_y[0][1]*np.power(focus_values,1)+ fit_coeff_y[0][2]
    fit_y = fit_coeff_y[0][0]*np.power(focus_new,2) + fit_coeff_y[0][1]*np.power(focus_new,1)+ fit_coeff_y[0][2]

    intersect = focus_new[np.where(np.round(fit_x,4) == np.round(fit_y,4))]

    FWHM_bestx = fit_x[np.where(np.round(fit_x,4) == np.round(fit_y,4))]
    FWHM_besty = fit_y[np.where(np.round(fit_x,4) == np.round(fit_y,4))]

    diff_x = FWHM_x - fit_x_short
    var_x = np.std(diff_x)
    diff_y = FWHM_y - fit_y_short
    var_y = np.std(diff_y)

    print('----------------------- \n Best Focus: %1.0f \n ----------------------- \n Best Seeing: %1.1f \n ----------------------- \n Seeing Variability: %1.1f \n -----------------------' % (float(np.median(intersect)), float(np.median(FWHM_bestx)), var_x))
    
    plt.ioff()
    plt.plot(focus_values, FWHM_x, 'b-.', label='data_x')
    plt.plot(focus_values, FWHM_y, 'b:', label='data_y')
    plt.plot(focus_new, fit_x, 'g-', label='fit_x')
    plt.plot(focus_new, fit_y, 'r-', label='fit_y')
    plt.legend()
    plt.title('Focus Script')
    plt.xlabel('Focus (microns)')
    plt.ylabel('FWHM (")')
    plt.show()
    plt.close()

    ## Fix this to just save original fig
    plt.ioff()
    plt.plot(focus_values, FWHM_x, 'b-.', label='data_x')
    plt.plot(focus_values, FWHM_y, 'b:', label='data_y')
    plt.plot(focus_new, fit_x, 'g-', label='fit_x')
    plt.plot(focus_new, fit_y, 'r-', label='fit_y')
    plt.legend()
    plt.title('Focus Script')
    plt.xlabel('Focus (microns)')
    plt.ylabel('FWHM (")')
    plt.savefig(current_focus_dir+'/focus_curve.png')
    plt.close()

# send new focus
status = raw_input('--- Do you want to send focus: %1.0f? [Y/N]: ---' % (float(np.round(np.median(intersect),-1))))
if (status.lower()).startswith('y'):
    tcs.send_focus_microns(float(np.round(np.median(intersect),-1)))

print('----- FOCUS SEQUENCE COMPLETE -----')

