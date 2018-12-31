""" NIHTS Startup - Calls all the commands Henry requires for xcam to work in the ipython environment.
    v1.0: 2017-08-23, ag765@nau.edu, A Gustafsson
    
    To use, enter on the command line:
    python NIHTS_startup.py
    
    requires:
    - XenicsCamera
    - TCS
    - NIHTS
    - numpy
    - time
    - datetime
    - wx
    
    updates:
    -  None
    """

from xenics import XenicsCamera
x = XenicsCamera()
# currently need to confirm that camera is powered on at this step
x.set_gain(False)
x.go(1.0, 1, 1, return_images=True)
from xenics import TCS
from xenics import NIHTS
tcs = TCS()

nihts = NIHTS()

import numpy as np
import time
import datetime as dt
import wx

