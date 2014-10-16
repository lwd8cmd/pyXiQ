# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Logic module

import _cam
import time
import numpy as np

class Logic(_cam.Cam):
	def __init__(self, motors):
		super(Logic, self).__init__()
		self.motors	= motors
		self.state	= 0
		self.state_names	= {
			0 : 'manuaalne',
			1 : 'oota',
			2 : 'leia pall',
			3 : 'j2lita palli',
			4 : 'loo palli',
			5 : 'tagurda robotist',
			6 : 'tagurda varavast'
		}
		
	def f_manual(self):
		#manual mode, do nothing
		pass
		
	def f_wait(self):
		#wait until switch is flipped
		pass
		
	def f_find_ball(self):
		pass
		
	def f_follow_ball(self):
		if self.largest_ball is not None:
			r, alpha	= self.largest_ball
			self.motors.move(20, alpha, alpha*30)
		else:
			self.motors.move(0, 0, 0)
		self.motors.update()
		
	def f_kick_ball(self):
		#find gate, aim, shoot
		pass
		
	def f_back_away_robot(self):
		#run into another robot, back away (motors are stalled)
		pass
		
	def f_back_away_gate(self):
		#gate too close, back away
		pass
	
	def run(self):
		if self.open():
			print('logic: cam opened')
		else:
			print('logic: cam opening failed')
			return
		options = {
			0 : self.f_manual,
			1 : self.f_wait,
			2 : self.f_find_ball,
			3 : self.f_follow_ball,
			4 : self.f_kick_ball,
			5 : self.f_back_away_robot,
			6 : self.f_back_away_gate
		}
		i	= 0
		timea	= time.time()
		while self.run_it:
			self.analyze_frame()
			
			options[self.state]()
			
			#fps counter
			i += 1
			if i % 60 == 0:
				i = 0
				timeb	= time.time()
				self.fps	= str(int(round(60 / (timeb - timea))))
				timea	= timeb
		print('logic: close thread')
		self.motors.run_it	= False
		self.close()