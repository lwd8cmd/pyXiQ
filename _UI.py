# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# UI module

import pygame
import numpy as np
import threading
import cv2
import time
from collections import deque

class UI(object):
	def __init__(self, logic):
		self.logic	= logic
		pygame.init()
		pygame.display.set_caption('Press ESC to quit')
		self.background = pygame.image.load('UI_bg.png')
		self.size = (self.width, self.height) = self.background.get_size()
		self.screen = pygame.display.set_mode((self.size), pygame.DOUBLEBUF)
		self.clock = pygame.time.Clock()
		self.fps = 5
		self.font = pygame.font.SysFont('mono', 16, bold=False)
		self.font2 = pygame.font.SysFont('mono', 14, bold=False)
		self.GREEN = (0, 255, 0)
		self.WHITE = (255, 255, 255)
		self.BLACK = (0, 0, 0)
		self.RED = (255, 0, 0)
		self.HFOV	= 30 * np.pi / 180
		
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
		pygame_keys_dir	= [pygame.K_a,pygame.K_q,pygame.K_w,pygame.K_e,pygame.K_d,pygame.K_x,pygame.K_s,pygame.K_z]
		pygame_keys_rotate	= [pygame.K_n,pygame.K_m]
		pygame_keys_states	= [pygame.K_0,pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8]
		pygame_keys_gates	= [pygame.K_y,pygame.K_b]
		S_MANUAL = 0
		
		while running and self.logic.run_it:
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
					break
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						running = False
						break
					if event.key == pygame.K_c:
						self.logic.motors.coil_kick(1000)
					elif event.key == pygame.K_t:
						self.logic.motors.coil_write('m')
					elif event.key == pygame.K_SPACE:#SPACE==stop
						self.logic.set_state(S_MANUAL)
						speed		= 0
						direction	= 0
						omega		= 0
					for index, item in enumerate(pygame_keys_states):#0-9==state
						if item == event.key:
							self.logic.set_state(index)
					for index, item in enumerate(pygame_keys_gates):#yb==change gate
						if item == event.key:
							self.logic.gate	= index
					if not (self.logic.state == 5 or self.logic.state == 6):
						for index, item in enumerate(pygame_keys_dir):#aqwedxsz==move
							if item == event.key:
								if self.logic.state is not S_MANUAL:
									self.logic.set_state(S_MANUAL)
								speed		= 1
								direction	= -np.pi/2 + index * np.pi/4#self.logic.motors.DEG120
								omega		= 0
								no_key 		= 0
						for index, item in enumerate(pygame_keys_rotate):#nm==rotate
							if item == event.key:
								if self.logic.state is not S_MANUAL:
									self.logic.set_state(S_MANUAL)
								speed		= 0
								direction	= 0
								omega		= (-1 if index == 0 else 1)
								no_key 		= 0
						
			if self.logic.state == 0 and (speed > 0 or omega is not 0):#set speed
				self.logic.motors.move(speed * 50, direction, omega * 40)
				self.logic.motors.update()
			
			#draw bg
			self.screen.blit(self.background, (0, 0))
			
			#draw velocity info (bottom right)
			tmp_om	= self.logic.motors.angular_velocity / 20
			pygame.draw.line(self.screen, self.WHITE, (305, 314), (
				305 + np.sin(self.logic.motors.direction)*self.logic.motors.speed,
				314 - np.cos(self.logic.motors.direction)*self.logic.motors.speed), 1)
			radius	= 64
			if tmp_om > 0:
				pygame.draw.arc(self.screen, self.WHITE, [305-radius, 314-radius, 2*radius, 2*radius], np.pi/2 - tmp_om, np.pi/2, 1)
			elif tmp_om < 0:
				pygame.draw.arc(self.screen, self.WHITE, [305-radius, 314-radius, 2*radius, 2*radius], np.pi/2, np.pi/2 - tmp_om, 1)
				
			#draw info (bottom left) (motors speed, fps, state)
			for i in range(3):
				self.screen.blit(self.font.render(
					self.strint(self.logic.motors.sds[i]),
					False, self.WHITE), (48, 250 + i * 19))
			self.screen.blit(self.font.render(self.strint(self.logic.fps), False, self.WHITE), (48, 307))
			self.screen.blit(self.font.render(('+' if self.logic.motors.has_ball else '-'), False, self.WHITE), (48, 326))
			self.screen.blit(self.font.render(('blue' if self.logic.gate else 'yellow'), False, self.WHITE), (48, 345))
			self.screen.blit(self.font.render(self.logic.motors.opened_status, False, self.WHITE), (48, 364))
			
			#draw status history
			for idx, val in enumerate(self.logic.history):
				self.screen.blit(self.font2.render(val, False, self.BLACK), (3, 383 + idx * 16))

			#draw robot
			robot_x	= self.logic.robot_x*185*2/460#185
			robot_y	= self.logic.robot_y*122*2/310#122
			#print(self.logic.robot_x, self.logic.robot_y, self.logic.robot_dir)
			robot_angle	= self.logic.robot_dir
			pygame.draw.line(self.screen, self.BLACK, (robot_x, robot_y), (
				robot_x + 150 * np.cos(robot_angle - self.HFOV),
				robot_y + 150 * np.sin(robot_angle - self.HFOV)), 1)
			pygame.draw.line(self.screen, self.BLACK, (robot_x, robot_y), (
				robot_x + 150 * np.cos(robot_angle + self.HFOV),
				robot_y + 150 * np.sin(robot_angle + self.HFOV)), 1)
			
			#draw balls
			for ball in self.logic.frame_balls:
				ball_x	= robot_x + ball[0] * np.cos(ball[1])*185*2/460
				ball_y	= robot_y + ball[0] * np.sin(ball[1])*185*2/460
				pygame.draw.rect(self.screen, self.RED, (ball_x-1,ball_y-1,3,3), 0)
			
			#update pygame screen
			pygame.display.flip()
				
			#show camera feed
			cv2.imshow('frame', self.logic.t_debug)
			
			#wait w/ openCV, pygame
			if cv2.waitKey(1) & 0xFF == pygame.K_ESCAPE:
				running	= False
			self.clock.tick(self.fps)

		#clean exit
		pygame.quit()
		cv2.destroyAllWindows()
		self.logic.run_it	= False
