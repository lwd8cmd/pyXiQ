import pygame.camera
import pygame.image
import time
import numpy as np
from pygame.locals import *

class Capture(object):
	def __init__(self):
		self.size = (640, 480)
		pygame.camera.init()
		# create a display surface. standard pygame stuff
		self.display = pygame.display.set_mode(self.size, 0)
		
		# this is the same as what we saw before
		self.clist = pygame.camera.list_cameras()
		if not self.clist:
			raise ValueError('Sorry, no cameras detected.')
		self.cam = pygame.camera.Camera(self.clist[0], self.size)
		self.cam.start()
		
		# create a surface to capture to.  for performance purposes
		# bit depth is the same as that of the display surface.
		self.snapshot = pygame.surface.Surface(self.size, 0, self.display)

	def get_and_flip(self):
		self.snapshot = self.cam.get_image(self.snapshot)
		#pygame.camera.colorspace(self.snapshot, 'HSV', self.snapshot)
		pxarray = pygame.PixelArray(self.snapshot)
		hsv	= pygame.camera.colorspace(self.snapshot, 'HSV')
		# threshold against the color we got before
		#mask = pygame.mask.from_threshold(self.snapshot, (255,255,128), (16, 128, 128))
		mask = pygame.mask.from_threshold(hsv, self.ccolor, (20, 64, 64))
		# find blobs
		connected = mask.connected_components(30)
		if True:# update screen?
			for ball in connected:
				for px in ball.outline():
					pxarray[px] = (0,255,0)
			del pxarray
			self.display.blit(self.snapshot,(0,0))
			pygame.display.flip()
			
	def calibrate(self):
		calibrate_surf = pygame.surface.Surface(self.size, 0, self.display)
		# capture the image
		going = True
		while going:
			calibrate_surf = self.cam.get_image(calibrate_surf)
			hsv	= pygame.camera.colorspace(calibrate_surf, 'HSV')
			# pygame.camera.colorspace(calibrate_surf, "HSV", calibrate_surf)
			# blit it to the display surface
			self.display.blit(calibrate_surf, (0,0))
			# make a rect in the middle of the screen
			crect = pygame.draw.rect(self.display, (255,0,0), (320,240,30,30), 4)
			# get the average color of the area inside the rect
			self.ccolor = pygame.transform.average_color(hsv, crect)
			# update
			pygame.display.flip()
			
			events = pygame.event.get()
			for e in events:
				if e.type == KEYDOWN and e.key == K_SPACE:
					going = False

	def main(self):
		going = True
		timea	= time.time()
		i	= 0
		while going:
			events = pygame.event.get()
			for e in events:
				if e.type == 12 or (e.type == KEYDOWN and e.key == K_SPACE):
					# close the camera safely
					self.cam.stop()
					pygame.camera.quit()
					going = False
			self.get_and_flip()
			# show fps
			i += 1
			if i % 30 == 0:
				timeb	= time.time()
				pygame.display.set_caption('FPS ' + str(30.0/(timeb-timea)))
				timea	= timeb
            
doit = Capture()
print('Press SPACE to CALIBRATE')
doit.calibrate()
print('Press SPACE to EXIT')
doit.main()