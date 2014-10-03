import numpy as np
import cv2
import time

cap = cv2.VideoCapture(0)

if not cap.isOpened():
	print('Could not open')
	exit()
	
#START calibrate
	
def nothing(x):
	pass

print('Press SPACE when done')
ret, frame = cap.read()
img = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR)
#hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

cv2.namedWindow('controls', cv2.CV_WINDOW_AUTOSIZE)
cv2.namedWindow('mask', cv2.CV_WINDOW_AUTOSIZE)
cv2.namedWindow('image', cv2.CV_WINDOW_AUTOSIZE)

cv2.imshow('image', img[:,:,::-1])

#capture23:0,24,150,255,150,255
#cv2.resizeWindow('controls', 400, 300)
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
	
	mask = cv2.inRange(frame, hsv_min, hsv_max)
	
	cv2.imshow('mask', mask)
	if cv2.waitKey(1) & 0xFF == ord(' '):
		break

cv2.destroyAllWindows()

print('Press q to quit')
element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
timea	= time.time()
cv2.namedWindow('frame', cv2.CV_WINDOW_AUTOSIZE)

i = 0
while True:
	ret, frame = cap.read()
	if not ret:
		break
		
	#hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	a = cv2.inRange(frame, hsv_min, hsv_max)
	#a = cv2.erode(a,element, iterations=2)
	#a = cv2.dilate(a,element, iterations=2)
	#a = cv2.erode(a,element)
	
	contours, hierarchy = cv2.findContours(a, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	max_area	= 0
	ball	= None
	for contour in contours:
		s	= cv2.contourArea(contour)
		if s > max_area:
			max_area = s
			ball = contour
	
	i+=1
	if i % 3 == 0:# show every n-th frame
		if ball is not None:
			x,y,w,h = cv2.boundingRect(ball)
			cv2.rectangle(frame, (x,y),(x+w,y+h), (0,0,255), 1)
			
		timeb	= time.time()
		cv2.putText(frame, str(3 / (timeb - timea)), (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
		timea	= timeb
		
		cv2.imshow('frame', frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):#cv2.waitKey argument is 1000/fps
			break
	
cap.release()
cv2.destroyAllWindows()