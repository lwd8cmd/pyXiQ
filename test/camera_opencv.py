import numpy as np
import cv2
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480);
cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640);
cap.set(cv2.cv.CV_CAP_PROP_FPS, 30)

timea	= time.time()
i	= 0

print('Press SPACE to CALIBRATE')
while True:
	ret, frame = cap.read()
	x	= 320
	y	= 240
	w	= 20
	h	= 20
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	
	frame[y-h,x-w:x+w]	= [0,0,255]
	frame[y+h,x-w:x+w]	= [0,0,255]
	frame[y-h:y+h,x-w]	= [0,0,255]
	frame[y-h:y+h,x+w]	= [0,0,255]
	
	i	+= 1
	if i % 30 == 0:
		timeb	= time.time()
		print(30.0 / (timeb - timea))
		timea	= timeb
	
	cv2.imshow('frame', frame[:,::-1])
	if (cv2.waitKey(1) & 0xFF == ord(' ')):
		hsv_mean	= hsv[y-h:y+h,x-w:x+w].mean(0).mean(0)
		break

hsv_diff	= np.array([10, 32, 32], np.uint8)
hsv_min	= hsv_mean - hsv_diff
hsv_max	= hsv_mean + hsv_diff
print(frame.shape)

print('Press SPACE to EXIT')
while True:
	ret, frame = cap.read()
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	threshed = cv2.inRange(hsv, hsv_min, hsv_max)
	blobs, hier	= cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	
	i	+= 1
	if i % 30 == 0:
		timeb	= time.time()
		print(30.0 / (timeb - timea))
		timea	= timeb
	
	if True:#update screen
		for blob in [bl for bl in blobs if len(bl)>50]:
			for px in blob:
				frame[px[0][1], px[0][0]]	= [0,0,255]
		
		cv2.imshow('frame', frame)
	if cv2.waitKey(1) & 0xFF == ord(' '):
		break

cap.release()
cv2.destroyAllWindows()