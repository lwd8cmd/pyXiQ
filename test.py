import pyXiQ
import numpy as np
import cPickle as pickle
import cv2

color_file = 'colors.pkl'
try:
	with open(color_file, 'rb') as fh:
		colors_lookup = pickle.load(fh)
except:
	colors_lookup	= np.zeros(0x1000000, dtype=np.uint8)

cam = pyXiQ.Camera()# Open the camera
if not cam.opened():
	print("cam not found")
	exit()
cam.setParamInt("exposure", 30000)
#cam.setParamInt("downsampling", 2)
cam.setParamInt("auto_wb", 0)
cam.setParamFloat("framerate", 60)
cam.start()# Start recording
cam.setTable(colors_lookup)

test = cam.image()
segmented = np.zeros((test.shape[0], test.shape[1]), dtype=np.uint8)

cv2.namedWindow('tava')
while True:
	#image = cam.image()
	cam.segment(segmented)
	
	cv2.imshow('tava', segmented*70)
		
	k = cv2.waitKey(1) & 0xff

	if k == ord('q'):
		break

# When everything done, release the capture
cam.close()# Close camera
cv2.destroyAllWindows()
