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
			2 : 'j2lita palli',
			3 : 'loo palli',
			4 : 'tagurda robotist',
			5 : 'tagurda varavast'
		}
		
	def f_manual(self):
		#manual mode, do nothing
		pass
		
	def f_wait(self):
		#wait until switch is flipped
		pass
		
	def f_follow_ball(self):
		max_area	= 0
		largest_ball	= None
		print(len(self.frame_balls))
		for ball in self.frame_balls:
			if ball[4] > max_area:
				max_area = ball[4]
				largest_ball = ball
		
		if largest_ball is not None:
			x	= largest_ball[0] + largest_ball[2] / 2
			self.motors.move(2, (x - 320) * 70 * np.pi / 180 / 640, 0)
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
			2 : self.f_follow_ball,
			3 : self.f_kick_ball,
			4 : self.f_back_away_robot,
			5 : self.f_back_away_gate
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