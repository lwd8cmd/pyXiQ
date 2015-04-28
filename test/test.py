import pyXiQ
import numpy as np
import cPickle as pickle
import cv2
import time

cam = pyXiQ.Camera()# Open the camera
if not cam.opened():
	print("cam not found")
	exit()
cam.setInt("exposure", 10000)
#cam.setInt("downsampling", 2)
#cam.setInt("auto_wb", 0)
#cam.setFloat("framerate", 30)
try:
	with open('../samples/calibration/colors.pkl', 'rb') as fh:
		cam.setColors(pickle.load(fh))
except:
	print("Color table missing")
try:
	with open('../samples/calibration/locations.pkl', 'rb') as fh:
		print("open")
		loc_r, loc_phi = pickle.load(fh)
		cam.setLocations(loc_r, loc_phi)
except:
	print("Locations table missing")
cam.setColorMinArea(1, 1)
cam.setColorMinArea(2, 1)
cam.start()# Start recording
#segmented_buffer = np.frombuffer(cam.getBuffer(), dtype=np.uint8).reshape(cam.shape())
segmented_buffer = cam.getBuffer()

cv2.namedWindow('tava')
while False:
	#image = cam.image()
	cam.analyse()
	vals = cam.getBlobs(1)
	img = np.copy(segmented_buffer)*127
	if True and len(vals) > 0:
		print("Obj 1", vals[0,0], vals[0,1])
		img[vals[0,7]:vals[0,8],vals[0,5]] = 255
		img[vals[0,7]:vals[0,8],vals[0,6]] = 255
		img[vals[0,7],vals[0,5]:vals[0,6]] = 255
		img[vals[0,8],vals[0,5]:vals[0,6]] = 255
	
	cv2.imshow('tava', img)
		
	k = cv2.waitKey(1) & 0xff

	if k == ord('q'):
		break
		
if False:
	start_time = time.time()
	frames = 60*10
	for i in xrange(frames):
		cam.analyse()
		blobs = cam.getBlobs(1)
		#if i % 10 == 0 and len(blobs) > 0:
		#	print(blobs[0,4])
	print(frames * 1.0 / (time.time() - start_time))
	
if False:
	start_time = time.time()
	frames = 1000
	for i in xrange(frames):
		cam.image()
		
	print(frames * 1.0 / (time.time() - start_time))
	
if False:
	#image = cam.image()
	#img = cv2.cvtColor(image, cv2.COLOR_BayerBG2BGR)#BayerBG2BGR
	#image2 = cam.image()
	#print(image2[1,1:-1,2].mean())
	while True:
		img = cam.image()
		print(img[:,:,0].std()**2+img[:,:,1].std()**2+img[:,:,2].std()**2)
		cv2.imshow('tava', img[::2,::2,:])
		if cv2.waitKey(1) & 0xff == ord('q'):
			break
			
if True:
	cam.test()
	
# When everything done, release the capture
cv2.destroyAllWindows()
