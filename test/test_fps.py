import numpy as np
import cv2
import time

cap = cv2.VideoCapture(0)

if not cap.isOpened():
	print('Could not open')
	exit()
	
ret, frame = cap.read()
print(frame.shape)

#cap.release()
#exit()

time.sleep(1)
timea	= time.time()
element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
hsv_min	= np.array([0, 88, 224], np.uint8)
hsv_max	= np.array([14, 255, 255], np.uint8)
i = 0
while i<200:
	ret, frame = cap.read()
	i+=1
	#frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR)
	#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	a = cv2.inRange(frame, hsv_min, hsv_max)
	#a = cv2.erode(a,element, iterations=2)
	#a = cv2.dilate(a,element, iterations=2)
	#a = cv2.erode(a,element)
	contours, hierarchy = cv2.findContours(a, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(200 / (time.time() - timea))
cap.release()
