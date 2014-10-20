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
			3 : 'j2lita',
			4 : 'l66',
			5 : 'stalled',
			6 : 'tagurda',
			7 : 'v2ravast',
			8 : 'v2ravasse'
		}
		self.stalled_i	= 0
		self.last_state = 0
		
	def f_manual(self):
		#manual mode, do nothing
		pass
		
	def f_wait(self):
		#wait until switch is flipped
		pass
		
	def f_find_ball(self):
		if self.frame_balls:
			self.state	= 3
		else:
			self.motors.move(0, 0, 15)
			self.motors.update()
		
	def f_follow_ball(self):
		if self.largest_ball is not None:
			r, alpha	= self.largest_ball
			self.motors.move(30, alpha, alpha*20)
			self.motors.update()
		else:
			self.state	= 4
			#self.motors.move(0, 0, 0)
			#self.motors.update()
		
	def f_follow_gate(self):
		if self.gates[0] is not None:
			r, alpha	= self.gates[0]
			self.motors.move(30, alpha, alpha*20)
		else:
			self.motors.move(0, 0, 0)
		self.motors.update()
		
	def f_kick_ball(self):
		if self.gates[0] is not None:
			self.state	= 8
		else:
			self.motors.move(0, 0, 15)
			self.motors.update()
		
	def f_stalled(self):
		self.stalled_i += 1
		if self.stalled_i > 30:#drive 0.5s without checking stalled
			self.state	= 6
			
	def f_stalled_init(self):
		print('stalled')
		if not self.state == 6:
			self.last_state	= self.state
		self.state	= 5
		self.stalled_i	= 0
		self.motors.move(30, self.motors.direction + self.motors.DEG120, 0)#change dir
		self.motors.update()
		
	def f_back_away_robot(self):
		self.stalled_i += 1
		if self.stalled_i > 60:#drive 1s
			self.state	= self.last_state
		
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
			5 : self.f_stalled,
			6 : self.f_back_away_robot,
			7 : self.f_back_away_gate,
			8 : self.f_follow_gate
		}
		i	= 0
		timea	= time.time()
		while self.run_it:
			self.analyze_frame()
			if True in self.motors.stalled and self.state is not 5:
				self.f_stalled_init()
			else:
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
