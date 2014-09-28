import numpy as np
import cv2
import time

# http://www.blogdugas.net/?p=120
class Test(object):
	def __init__(self):
		self.img = cv2.imread('480p.jpg')
		self.hsv_min	= np.array([0, 88, 224], np.uint8)
		self.hsv_max	= np.array([14, 255, 255], np.uint8)
		#cv2.imwrite('720phsv.jpg',self.hsv)
		
	def analyze(self):
		hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
		a = cv2.inRange(hsv, self.hsv_min, self.hsv_max)
		element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
		a = cv2.erode(a,element, iterations=2)
		a = cv2.dilate(a,element, iterations=2)
		a = cv2.erode(a,element)
		
		contours, hierarchy = cv2.findContours(a, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		for contour in contours:
			#cv2.contourArea(contour)
			x,y,w,h = cv2.boundingRect(contour)
			#cv2.rectangle(self.img, (x,y),(x+w,y+h), (0,0,255), 1)
		
		#while True:
		#	cv2.imshow('a', self.img)
		#	if cv2.waitKey(1) & 0xFF == ord(' '):
		#		break
		
test	= Test()
timea	= time.time()
for i in xrange(500):
	test.analyze()
print(500 / (time.time() - timea))