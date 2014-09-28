import numpy as np
import pygame.camera
import pygame.image
from pygame.locals import *
import time
import colorsys

class Test(object):
	def __init__(self):
		self.img = pygame.image.load('720phsv.jpg')
		self.hsv_min	= np.array([0, 88, 224], np.uint8)
		self.hsv_max	= np.array([14, 255, 255], np.uint8)
		self.color	= (self.hsv_min + self.hsv_max) // 2
		self.diff	= (self.hsv_max - self.hsv_min) // 2
		
	def analyze(self):
		#hsv	= pygame.camera.colorspace(self.img, 'HSV')
		self.mask = pygame.mask.from_threshold(self.img, self.color, self.diff)
		connected = self.mask.connected_components()
		
test	= Test()
timea	= time.time()
for i in range(100):
	test.analyze()
print(100 / (time.time() - timea))