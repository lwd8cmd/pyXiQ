#!/usr/bin/env python

import numpy as np
import cv2

fn = 'calib5.jpg'
img = cv2.imread(fn, 0)
if img is None:
	print "Failed to load", fn
	exit()

for x in xrange(3,10):
	for y in xrange(x, 10):
		pattern_size = (x, y)
		found, corners = cv2.findChessboardCorners(img, pattern_size)
		if found:
			print(x, y)
			if True:
				term = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1 )
				cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
				vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
				cv2.drawChessboardCorners(vis, pattern_size, corners, found)
				cv2.imshow('img',vis[::2,::2])
				cv2.waitKey(0)

cv2.destroyAllWindows()