""" NIHTS LMI MAPPING
    v1.1: 2018-04-12, ag765@nau.edu, A Gustafsson

    
    ** CURRENT VERSION

    
    updates:
    -
    
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
import argparse
import numpy as np

# define command line arguments
parser = argparse.ArgumentParser(description='provide the home LMI x position, home LMI y position, and current x and y positions of the object')
parser.add_argument('home_x', help='LMI home position x')
parser.add_argument('home_y', help='LMI home position y')
parser.add_argument('xpos', help='x pixel position of star')
parser.add_argument('ypos', help='y pixel position of star')
parser.add_argument('-binning', help='binning (ex: enter 2 for 2x2, 3 for 3x3', default=2)
args = parser.parse_args()
home_x = float(args.home_x)
home_y = float(args.home_y)
xpos = float(args.xpos)
ypos = float(args.ypos)
binning = int(args.binning)

pixscale = binning*0.12

offset_x = (float(xpos)-float(home_x))*pixscale
offset_y = (float(ypos)-float(home_y))*pixscale

print(offset_x)
print(offset_y)

print('Apply the offset %.2f East and %.2f in South' %(offset_x, offset_y))
#print('East is positive, South is positive')

quit()


