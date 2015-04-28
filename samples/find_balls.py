import pyXiQ
import numpy as np
import cPickle as pickle
import cv2

cam = pyXiQ.Camera()# Open the camera
if not cam.opened():
	print("cam not found")
	exit()
cam.setInt("exposure", 10000)
try:
	with open('calibration/colors.pkl', 'rb') as fh:
		cam.setColors(pickle.load(fh))
except:
	print("Color table missing")
try:
	with open('calibration/locations.pkl', 'rb') as fh:
		loc_r, loc_phi = pickle.load(fh)
		cam.setLocations(loc_r, loc_phi)
except:
	print("Locations table missing")
try:
	with open('calibration/pixels.pkl', 'rb') as fh:
		active_pixels = pickle.load(fh)
		cam.setPixels(active_pixels)
except:
	print("Active pixels table missing")
cam.setColorMinArea(1, 30)#find blobs having color 1 with min area 30
cam.start()# Start recording
segmented_buffer = cam.getBuffer()#get buffer containing thresholded image

cv2.namedWindow('tava')
print("Press 'q' to quit")
while True:
	cam.analyse()
	blobs = cam.getBlobs(1)
	img = np.copy(segmented_buffer)*127
	if len(blobs) > 0:
		ball = blobs[0]
		print('Largest ball d={r: >5}mm, fii={f: >3}deg, area={a: >5}px, x={x: >4}, y={y: >4}'.format(r=ball[0], f=int(round(ball[1]*360.0/65536.0)), a=ball[2], x=ball[3], y=ball[4]))
		#print("Obj 1", blobs[0,0], blobs[0,1])
		#draw white bounding box
		img[blobs[0,7]:blobs[0,8],blobs[0,5]:blobs[0,5]+2] = 255#left line
		img[blobs[0,7]:blobs[0,8],blobs[0,6]:blobs[0,6]+2] = 255#right line
		img[blobs[0,7]:blobs[0,7]+2,blobs[0,5]:blobs[0,6]] = 255#top line
		img[blobs[0,8]:blobs[0,8]+2,blobs[0,5]:blobs[0,6]] = 255#bottom line
	
	cv2.imshow('tava', img[::2,::2])#show segmentated image and bounding box

	if cv2.waitKey(1) & 0xff == ord('q'):#exit
		break