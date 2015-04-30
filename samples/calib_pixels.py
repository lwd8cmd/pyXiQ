#set pixels that are on the mirror
import pyXiQ
import numpy as np
import cPickle as pickle
import cv2

#get frame
cam = pyXiQ.Camera()# Open the camera
if not cam.opened():
	print("cam not found")
	exit()
cam.setInt("exposure", 10000)
cam.start()# Start recording
img = cam.image()
cam.stop()

#init default arrays
h, w, _ = img.shape
ys, xs = np.mgrid[:h,:w]
active_pixels = np.ones((h, w), dtype=np.uint8)

#set some pixels inactive
active_pixels[(ys-512)**2+(xs-640)**2 > 400**2] = 0#pixels which are outside the circle r=400 (x=640, y=512)

#show frame where inactive pixels are removed
img[active_pixels == 0] = [0,0,0]
print("Press 'q' to quit")
while True:
	cv2.imshow('tava', img[::2,::2])
	k = cv2.waitKey(1) & 0xff
	if k == ord('q'):
		print('Quit without saving')
		break
	elif k == ord('s'):
		with open('calibration/pixels.pkl', 'wb') as fh:
			pickle.dump(active_pixels, fh, -1)
			print('saved')