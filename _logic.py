# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Logic module

import _cam
import time
import numpy as np

class Logic(_cam.Cam):
	def f_manual_init(self):
		self.motors.move(0, 0, 0)
		self.motors.update()
		
	def f_manual(self):#manual mode, do nothing
		pass
		
	def f_find_lost_ball_init(self):
		self.motors.move(-50, 0, 0)
		self.motors.update()
		self.count_i = 60
		
	def f_find_lost_ball(self):#back away until see ball
		if self.largest_ball is not None:#saw ball, follow it
			self.set_state(4)
			return
		self.count_i -= 1
		if self.count_i == 0:#timeout, find_ball
			self.set_state(3)
				
	def f_find_ball_init(self):
		self.count_i	= 180
		self.motors.move(0, 0, 40)
		self.motors.update()
		
	def f_find_ball(self):#turn until  see ball
		if self.largest_ball is not None:
			self.set_state(4)
			return
		self.count_i -= 1
		if self.count_i == 0:#timeout, wait
			self.set_state(0)
			
	def f_follow_ball_init(self):
		return
		
	def f_follow_ball(self):
		if self.largest_ball is None:#ball is lost, find ball
			self.set_state(3)
			return
			
		r, alpha	= self.largest_ball
		if r > 30:#follow
			self.motors.move(100, alpha, alpha*50)
			self.motors.update()
		else:#ball is going to the blind area, follow blind
			self.set_state(5)
			
	def f_follow_ball_blind_init(self):
		if self.largest_ball is not None:
			r, alpha	= self.largest_ball
			self.motors.move(50, alpha, alpha*100)
			self.motors.update()
			self.count_i = 60
			
	def f_follow_ball_blind(self):
		if self.motors.has_ball:
			self.set_state(6)
			return
		self.count_i -= 1
		if self.count_i == 30:
			self.motors.move(10, 0, 0)
			self.motors.update()
		if self.count_i == 0:
			self.set_state(3)
			
	def f_aim_init(self):
		self.count_i = 15#time to wait when gate is in the center (ball stabilize)
		
	def f_aim(self):
		if not self.motors.has_ball:#ball is lost
			self.set_state(1)
			return
		if self.gates[self.gate] is None:#gate lost, find gate
			self.set_state(6)
			return
		r, alpha, w	= self.gates[self.gate]
		if np.abs(alpha) < 3.0 / w:#gate in the center
			self.count_i	-= 1
			if self.count_i == 0:
				self.motors.coil_kick()
				self.set_state(3)
		else:#turn to the gate
			alp	= max(-10, min(10, alpha * 100))
			self.motors.move(0, 0, alp)
			self.motors.update()
			
	def f_find_gate_init(self):
		self.motors.move(0, 0, 20 * ((1 if self.gate_right else -1)))#turn
		self.motors.update()
		
	def f_find_gate(self):#turn until see gate
		if not self.motors.has_ball:#ball is lost
			self.set_state(1)
			return
		if self.gates[self.gate] is not None:#gate found
			self.set_state(7)
			return
			
	def f_stalled_init(self):
		print('stalled')
		if not self.state == 12:
			self.last_state	= self.state
		self.count_i	= 30
		self.motors.move(30, self.motors.direction + self.motors.DEG120, 0)#change dir
		self.motors.update()
		
	def f_stalled(self):
		self.count_i -= 1
		if self.stalled_i == 0:#drive 0.5s without checking stalled
			self.set_state(12)
		
	def f_back_away_robot_init(self):
		self.count_i = 30
		
	def f_back_away_robot(self):
		self.count_i -= 1
		if self.count_i == 0:#drive 1s
			self.set_state(self.last_state)
		
	def set_state(self, state):
		self.init_options[state]()
		self.state	= state
		
	def update_position(self):
		self.robot_x	+= self.motors.speed/64.0*np.cos(self.motors.direction+self.robot_dir)
		self.robot_y	+= self.motors.speed/64.0*np.sin(self.motors.direction+self.robot_dir)
		self.robot_dir	+= self.motors.angular_velocity/783.0
		
	def __init__(self, motors):
		super(Logic, self).__init__()
		self.motors	= motors
		self.state	= 0
		self.state_names	= {
			0 : 'manuaalne',
			11 : 'stalled',
			12 : 'tagurda',
			1 : 'leia kadunud pall',
			3 : 'leia pall',
			4 : 'j2lita palli',
			5 : 'pime',
			6 : 'leia varav',
			7 : 'sihi'
		}
		self.init_options = {
			0 : self.f_manual_init,
			11 : self.f_stalled_init,
			12 : self.f_back_away_robot_init,
			1 : self.f_find_lost_ball_init,
			3 : self.f_find_ball_init,
			4 : self.f_follow_ball_init,
			5 : self.f_follow_ball_blind_init,
			6 : self.f_find_gate_init,
			7 : self.f_aim_init
		}
		self.last_state = 0
		self.robot_x	= 0#max 460cm
		self.robot_y	= 155#max 310cm
		self.robot_dir	= 0
		self.gate	= 0#0=yellow,1=blue
		self.profile	= 60 * 10
		self.count_i	= 0
	
	def run(self):
		if self.open():
			print('logic: cam opened')
		else:
			print('logic: cam opening failed')
			return
		options = {
			0 : self.f_manual,
			11 : self.f_stalled,
			12 : self.f_back_away_robot,
			1 : self.f_find_lost_ball,
			3 : self.f_find_ball,
			4 : self.f_follow_ball,
			5 : self.f_follow_ball_blind,
			6 : self.f_find_gate,
			7 : self.f_aim
		}
		i	= 0
		timea	= time.time()
		while self.run_it:
			self.analyze_frame()
			if True in self.motors.stalled and self.state is not 11:
				self.set_state(11)
			else:
				options[self.state]()
			
			self.update_position()
				
			#fps counter
			i += 1
			if i % 60 == 0:
				i = 0
				timeb	= time.time()
				self.fps	= str(int(round(60 / (timeb - timea))))
				timea	= timeb
				
			#self.profile -= 1
			#if self.profile < 0:
			#	self.run_it = False
		print('logic: close thread')
		self.motors.run_it	= False
		self.close()
