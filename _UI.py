# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# UI module

import pygame
import numpy as np
import threading
import cv2

class UI(object):
	def __init__(self, logic):
		self.logic	= logic
		self.logic.UI	= True
		pygame.init()
		pygame.display.set_caption('Press ESC to quit')
		self.background = pygame.image.load('UI_bg.png')
		self.size = (self.width, self.height) = self.background.get_size()
		self.screen = pygame.display.set_mode((self.size), pygame.DOUBLEBUF)
		self.clock = pygame.time.Clock()
		self.fps = 15
		self.playtime = 0.0
		self.font = pygame.font.SysFont('mono', 16, bold=False)
		self.GREEN = (0, 255, 0)
		self.WHITE = (255, 255, 255)
		self.BLACK = (0, 0, 0)
		
	def strint(self, val):
		return str(int(round(val)))

	def run(self):
		running	= True
		speed	= 0
		direction	= 0
		omega	= 0
		no_key	= 0
		
		cv2.namedWindow('frame')
		cv2.moveWindow('frame', 400, 0)
		
		while running:
			#keylisteners
			if no_key > 8:
				speed	= 0
				direction	= 0
				omega	= 0
			else:
				no_key += 1
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						running = False
						break
					elif event.key == pygame.K_a:
						self.logic.state	= 0
						speed		= 1
						direction	= -np.pi/2
						omega		= 0
						no_key 		= 0
					elif event.key == pygame.K_d:
						self.logic.state	= 0
						speed		= 1
						direction	= np.pi/2
						omega		= 0
						no_key 		= 0
					elif event.key == pygame.K_w:
						self.logic.state	= 0
						speed		= 1
						direction	= 0
						omega		= 0
						no_key 		= 0
					elif event.key == pygame.K_s:
						self.logic.state	= 0
						speed		= 1
						direction	= np.pi
						omega		= 0
						no_key 		= 0
					elif event.key == pygame.K_q:
						self.logic.state	= 0
						speed		= 1
						direction	= -np.pi/4
						omega		= 0
						no_key 		= 0
					elif event.key == pygame.K_e:
						self.logic.state	= 0
						speed		= 1
						direction	= np.pi/4
						omega		= 0
						no_key 		= 0
					elif event.key == pygame.K_n:
						self.logic.state	= 0
						speed		= 0
						direction	= 0
						omega		= -1
						no_key 		= 0
					elif event.key == pygame.K_m:
						self.logic.state	= 0
						speed		= 0
						direction	= 0
						omega		= 1
						no_key 		= 0
					elif event.key == pygame.K_x:
						self.logic.state	= 0
						speed		= 0
						direction	= 0
						omega		= 0
						no_key 		= 0
					elif event.key == pygame.K_p:
						self.logic.state	= 2
						
			if not running:
				break
			if self.logic.state == 0:#set speed
				self.logic.motors.move(speed*3, direction, omega*5)
				self.logic.motors.update()
			
			#draw bg
			self.screen.blit(self.background, (0, 0))
			
			#draw velocity info (bottom right)
			tmp_om	= self.logic.motors.angular_velocity / 5
			pygame.draw.line(self.screen, self.WHITE, (305, 314), (
				305 + np.sin(self.logic.motors.direction)*self.logic.motors.speed*10,
				314 - np.cos(self.logic.motors.direction)*self.logic.motors.speed*10), 1)
			radius	= 64
			if tmp_om > 0:
				pygame.draw.arc(self.screen, self.WHITE, [305-radius, 314-radius, 2*radius, 2*radius], np.pi/2 - tmp_om, np.pi/2, 1)
			elif tmp_om < 0:
				pygame.draw.arc(self.screen, self.WHITE, [305-radius, 314-radius, 2*radius, 2*radius], np.pi/2, np.pi/2 - tmp_om, 1)
				
			#draw info (bottom left) (motors speed, fps, state)
			self.screen.blit(self.font.render(
				self.strint(self.logic.motors.rsd1) + '/' + self.strint(self.logic.motors.sd1),
				False, self.WHITE), (40, 251))
			self.screen.blit(self.font.render(
				self.strint(self.logic.motors.rsd2) + '/' + self.strint(self.logic.motors.sd2),
				False, self.WHITE), (40, 273))
			self.screen.blit(self.font.render(
				self.strint(self.logic.motors.rsd3) + '/' + self.strint(self.logic.motors.sd3),
				False, self.WHITE), (40, 295))
			self.screen.blit(self.font.render(self.logic.fps, False, self.WHITE), (40, 317))
			self.screen.blit(self.font.render(self.logic.state_names[self.logic.state], False, self.WHITE), (40, 339))

			#update pygame screen
			pygame.display.flip()
			
			#draw ball boxes
			#for x,y,w,h,s in self.logic.frame_balls:
			#	cv2.rectangle(self.logic.frame, (x,y),(x+w,y+h), (255), 1)
			
			#show camera feed
			cv2.imshow('frame', self.logic.frame)
			
			#wait w/ openCV, pygame
			if cv2.waitKey(1) & 0xFF == pygame.K_ESCAPE:
				running	= False
			self.clock.tick(self.fps)

		#clean exit
		pygame.quit()
		cv2.destroyAllWindows()
		self.logic.run_it	= False