import numpy as np
import cv2
import time

class Test(object):
	def __init__(self):
		self.img = cv2.imread('720p.jpg')
		self.hsv_min	= np.array([0, 88, 224], np.uint8)
		self.hsv_max	= np.array([14, 255, 255], np.uint8)
		self.hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV).reshape((-1,3))
		print(self.hsv)
		#cv2.imwrite('720phsv.jpg',self.hsv)
		
	def analyze(self):
		threshed =   (self.hsv[:,:,0]>self.hsv_min[0])*(self.hsv[:,:,0]<self.hsv_max[0])\
					*(self.hsv[:,:,1]>self.hsv_min[1])*(self.hsv[:,:,1]<self.hsv_max[1])\
					*(self.hsv[:,:,2]>self.hsv_min[2])*(self.hsv[:,:,2]<self.hsv_max[2])
		#blobs, hier	= cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
		
	def show(self):
		while True:
			cv2.imshow('frame', self.threshed)
			if cv2.waitKey(1) & 0xFF == ord(' '):
				break
		
test	= Test()
timea	= time.time()
for i in xrange(100):
	test.analyze()
print(100 / (time.time() - timea))