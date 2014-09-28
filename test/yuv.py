import numpy as np
import cv2
import time

frame = cv2.imread('480p.jpg')
#START calibrate
	
def nothing(x):
	pass

print('Press SPACE when done')
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)

cv2.namedWindow('controls', cv2.WINDOW_NORMAL)
#capture23:0,24,150,255,150,255
cv2.resizeWindow('controls', 400, 300)
cv2.createTrackbar('Hmin','controls',3,255,nothing)
cv2.createTrackbar('Hmax','controls',18,255,nothing)
cv2.createTrackbar('Smin','controls',99,255,nothing)
cv2.createTrackbar('Smax','controls',255,255,nothing)
cv2.createTrackbar('Vmin','controls',115,255,nothing)
cv2.createTrackbar('Vmax','controls',255,255,nothing)

while True:
	ha = cv2.getTrackbarPos('Hmin','controls')
	hb = cv2.getTrackbarPos('Hmax','controls')
	sa = cv2.getTrackbarPos('Smin','controls')
	sb = cv2.getTrackbarPos('Smax','controls')
	va = cv2.getTrackbarPos('Vmin','controls')
	vb = cv2.getTrackbarPos('Vmax','controls')
	
	hsv_min	= np.array([ha, sa, va], np.uint8)
	hsv_max	= np.array([hb, sb, vb], np.uint8)
	
	mask = cv2.inRange(hsv, hsv_min, hsv_max)
	
	cv2.imshow('mask', mask)
	if cv2.waitKey(1) & 0xFF == ord(' '):
		break

cv2.destroyAllWindows()