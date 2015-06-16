import pyXiQ
import cv2
import cPickle as pickle
import scipy.misc
import time

cam = pyXiQ.Camera()
if not cam.opened():
	print("cam not found")
	exit()
cam.setInt("exposure", 10000)
cam.start()

print("Press 'q' to quit, 's' to save")
while True:
	img = cam.image()
	if 1:#print image std for focus calib
		h, w, _ = img.shape
		pxs = img[h//4:h//4*3,w//4:w//4*3,:]
		print(pxs[:,:,0].std()**2+pxs[:,:,1].std()**2+pxs[:,:,2].std()**2)
	cv2.imshow('tava', img[::2,::2])
	k = cv2.waitKey(1) & 0xff
	if k == ord('q'):
		break
	elif k == ord('s'):
		scipy.misc.imsave(time.strftime("%Y%m%d%H%M%S.jpg"), img[:,:,::-1])
		print('saved')