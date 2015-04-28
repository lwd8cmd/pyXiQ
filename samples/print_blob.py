import numpy as np
import pyXiQ

cam = pyXiQ.Camera()
cam.setInt("exposure", 10000)
colors = np.zeros((256,256,256), dtype=np.uint8)
colors[0:128,0:128,20:256] = 1#set colors blue=0..128, green=0..128, red=128..255 index to 1
cam.setColors(colors)
cam.setColorMinArea(1, 50)#show only blobs larger than 50 pixels
cam.start()

cam.analyse()
blobs = cam.getBlobs(1)
if len(blobs) > 0:
	print('x: {x}, y: {y}'.format(x=blobs[0,3], y=blobs[0,4]))