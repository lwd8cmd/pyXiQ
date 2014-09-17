import pygame.camera
import pygame.image
import time

class Capture(object):
	def __init__(self):
		self.size = (640, 480)
		pygame.camera.init()
		# create a display surface. standard pygame stuff
		self.display = pygame.display.set_mode(self.size, 0)
		
		# this is the same as what we saw before
		self.clist = pygame.camera.list_cameras()
		if not self.clist:
			raise ValueError("Sorry, no cameras detected.")
		self.cam = pygame.camera.Camera(self.clist[0], self.size)
		self.cam.start()
		
		# create a surface to capture to.  for performance purposes
		# bit depth is the same as that of the display surface.
		self.snapshot = pygame.surface.Surface(self.size, 0, self.display)

	def get_and_flip(self):
		self.snapshot = self.cam.get_image(self.snapshot)
		hsv	= pygame.camera.colorspace(self.snapshot, 'HSV')
		# threshold against the color we got before
		mask = pygame.mask.from_threshold(hsv, (255,255,128), (16, 128, 128))
		# find blobs
		connected = mask.connected_components()
		if True:# update screen?
			# display image
			self.display.blit(self.snapshot,(0,0))
			for mask in connected:
				for pix in mask.outline():
					pygame.draw.circle(self.display, (0,255,0), pix, 1)
			# make sure the blob is big enough that it isn't just noise
			#if connected[0].count() > 10:
			#	# find the center of the blob
			#	# draw a circle with size variable on the size of the blob
			#	pygame.draw.circle(self.display, (0,0,255), connected[0].centroid(), 10)
			pygame.display.flip()

	def main(self):
		going = True
		timea	= time.time()
		i	= 0
		while going:
			events = pygame.event.get()
			for e in events:
				if e.type == 12:
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
doit.main()