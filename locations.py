# Distance calibration for Ximea camera
# Lauri Hamarik 2015

import numpy as np
import cPickle as pickle

loc_r, loc_phi = np.mgrid[:1024,:1280]

with open('locations.pkl', 'wb') as fh:
	pickle.dump([loc_r.astype(np.uint16), loc_phi.astype(np.uint16)], fh, -1)