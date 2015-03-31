#!/usr/bin/python
#
# python-v4l2capture
#
# This file is an example on how to capture a mjpeg video with
# python-v4l2capture.
#
# 2009, 2010 Fredrik Portstrom
#
# I, the copyright holder of this file, hereby release it into the
# public domain. This applies worldwide. In case this is not legally
# possible: I grant anyone the right to use this work for any
# purpose, without any conditions, unless such conditions are
# required by law.

import pyXiQ
import numpy as np
import matplotlib.pyplot as plt

cam = pyXiQ.Camera()# Open the camera
print("cam")
cam.setParamInt("exposure", 100000)
cam.start()# Start recording
print("start")

while 1:
	img = cam.image()# Capture image
	asd = np.fromstring(img, dtype=np.uint8)
	print(len(asd))
	if (len(asd) == 1280*1024*3):
		plt.imshow(asd.reshape((1024,1280,3)))
	elif (len(asd) == 1280*1024):
		plt.imshow(asd.reshape((1024,1280)))
	else:
		plt.imshow(asd[:1280*150].reshape((-1,1280)))
	plt.show()

cam.close()# Close camera

