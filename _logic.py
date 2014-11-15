# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Logic module

import _cam
import time
import numpy as np
from collections import deque

class Logic(_cam.Cam):
	def __init__(self, motors):
		super(Logic, self).__init__()
		self.motors	= motors
		self.state	= 0
		self.S_MANUAL, self.S_FIND_BALL, self.S_WAIT, self.S_TURN, self.S_FOLLOW_BALL, self.S_FOLLOW_BALL_BLIND, self.S_FIND_GATE, self.S_AIM, self.S_KICK, \
			self.S_FIND_LOST_BALL, self.S_FIND_GATE_FAR, self.S_FOLLOW_GATE_FAR, self.S_STRAFE, self.S_STALLED, self.S_STALLEDB \
			= range(15)
		self.state_names	= {
			self.S_MANUAL : 'manuaalne',
			self.S_STALLED : 'stalled',
			self.S_STALLEDB : 'tagurda',
			self.S_FIND_LOST_BALL : 'leia kadunud pall',
			self.S_FIND_GATE_FAR : 'leia kauge v2ljak',
			self.S_FIND_BALL : 'leia pall',
			self.S_FOLLOW_BALL : 'j2lita palli',
			self.S_FOLLOW_BALL_BLIND : 'pime',
			self.S_FIND_GATE : 'leia varav',
			self.S_AIM : 'sihi',
			self.S_FOLLOW_GATE_FAR : 'l2hene kaugele v2ljakule',
			self.S_STRAFE : 'streifi',
			self.S_KICK : 'loo',
			self.S_TURN : 'poora 180d',
			self.S_WAIT : 'oota'
		}
		self.last_state = 0
		self.robot_x	= 0#max 460cm
		self.robot_y	= 155#max 310cm
		self.robot_dir	= 0
		self.gate	= 0#0=yellow,1=blue
		self.gate_far	= 0
		self.profile	= 60 * 10
		self.count_i	= 0
		self.count_j	= 0
		self.angle_history	= deque([], maxlen=60)
		self.ball_blind_i	= 0
		self.history	= deque([], maxlen=9)
		
	def f_manual(self):#manual mode, do nothing
		if self.count_i == 0:
			self.motors.move(0, 0, 0)
			self.motors.update()
			
		if False and self.largest_ball is not None:#ball is lost, find ball
			r, alpha	= self.largest_ball
			self.angle_history.append(alpha)
			print(r, sum(self.angle_history) / len(self.angle_history))
			
	def f_wait(self):#wait
		if self.count_i == 0:
			self.motors.move(0, 0, 0)
			self.motors.update()
		self.motors.motor_write(1, 'gb')
		self.motors.read_buffer(1)
		if self.motors.button:
			self.set_state(self.S_FIND_BALL)
		
	def f_find_lost_ball(self):#back away until see ball
		if self.motors.has_ball:
			self.set_state(self.S_FIND_GATE)
			return
		if self.count_i	== 0:
			self.motors.move(0, 0, 0)
			self.motors.update()
		if self.count_i	> 10:
			self.motors.move(-50, 0, 0)
			self.motors.update()
		if self.count_i > 60 and self.largest_ball is not None:#saw ball, follow it
			self.set_state(self.S_FOLLOW_BALL)
			return
		if self.count_i > 90:#timeout, find_ball
			self.set_state(self.S_FIND_BALL)
			
	def f_turn(self):#turn to see smth else
		if self.count_i == 0:
			self.motors.move(0, 0, 40)
			self.motors.update()
		if self.count_i > 30:#timeout, wait
			self.set_state(self.S_FIND_BALL)
		
	def f_find_ball(self):#turn until see ball
		if self.motors.has_ball:
			self.set_state(self.S_FIND_GATE)
			return
		if self.count_i == 0:
			self.motors.move(0, 0, 40)
			self.motors.update()
		if self.largest_ball is not None:
			self.set_state(self.S_FOLLOW_BALL)
			return
		if self.count_i > 120:#timeout, wait
			self.set_state(self.S_FIND_GATE_FAR)
			
	def f_find_gate_far(self):
		if self.count_i == 0:
			self.gate_far = 0 if self.gates_last[0][0] > self.gates_last[1][0] else 1
			self.motors.move(0, 0, 40)
			self.motors.update()
		if self.motors.has_ball:
			self.set_state(self.S_FIND_GATE)
			return
		if self.gates[self.gate_far] is not None:#gate found
			self.set_state(self.S_FOLLOW_GATE_FAR)
			
	def f_follow_gate_far(self):
		if self.motors.has_ball:
			self.set_state(self.S_FIND_GATE)
			return
		gate	= self.gates[self.gate_far]
		if gate is None:#gate is lost
			self.set_state(self.S_FIND_GATE_FAR)
			return
			
		if gate[0] > 100:#follow
			self.motors.move(60, gate[1], gate[1]*10)
			self.motors.update()
		else:#find ball
			self.set_state(self.S_FIND_BALL)
		
	def f_follow_ball(self):
		if self.motors.has_ball:
			self.set_state(self.S_FIND_GATE)
			return
		if self.largest_ball is None:#ball is lost, find ball
			self.set_state(self.S_FIND_BALL)
			return
			
		r, alpha	= self.largest_ball
		if r > 29:#follow
			self.motors.move(40, alpha, alpha*20)
			self.motors.update()
		else:#ball is going to the blind area, follow blind
			self.motors.move(20, alpha, 0)
			self.motors.update()
			self.set_state(self.S_FOLLOW_BALL_BLIND)
			
	def f_follow_ball_blind(self):
		if self.count_i == 0:
			self.ball_blind_i += 1
		if self.motors.has_ball:
			self.set_state(self.S_FIND_GATE)
			return
		if self.count_i > 50 + self.ball_blind_i * 30:
			if self.ball_blind_i > 3:
				self.set_state(self.S_TURN)
				return
			self.set_state(self.S_FIND_LOST_BALL)
			
	def f_find_gate(self):#turn until see gate
		if self.count_i == 0:
			self.motors.move(0, 0, 20 * ((1 if self.gates_last[self.gate][1] > 0 else -1)))#turn
			self.motors.update()
		if not self.motors.has_ball:#ball is lost
			self.set_state(self.S_FIND_LOST_BALL)
			return
		if self.gates[self.gate] is not None:#gate found
			self.set_state(self.S_AIM)
			return
			
	def f_aim(self):
		if self.count_i	== 0:
			self.count_j = 0
			self.ball_blind_i = 0
		if not self.motors.has_ball:#ball is lost
			self.set_state(self.S_FIND_LOST_BALL)
			return
		gate	= self.gates[self.gate]
		if gate is None:#gate lost, find gate
			self.set_state(self.S_FIND_GATE)
			return
		if np.abs(gate[1])*6000.0 < gate[2] and gate[2]*gate[3]/gate[4] > 2.5 or (self.fragmented[gate[6]+gate[3]:,320-2:320+2]==0).sum()>300:#see gate side
			self.set_state(self.S_STRAFE)
			return
		if np.abs(gate[1])*3000.0 < gate[2]:#gate in the center
			self.count_j += 60.0 / self.fps
			if self.count_j > 15:#time to wait when gate is in the center (ball stabilizes)
				self.set_state(self.S_KICK)
				return
		alp	= max(-10, min(10, gate[1] * 100))
		self.motors.move(0, 0, alp)
		self.motors.update()
		
	def f_kick(self):
		if self.count_i	== 0:
			if not self.motors.has_ball:#ball is lost
				self.set_state(self.S_FIND_LOST_BALL)
				return
			self.motors.coil_kick()
			self.motors.move(0, 0, 0)
			self.motors.update()
		if self.count_i > 60:
			self.set_state(self.S_FIND_BALL)
			return
			
	def f_strafe(self):
		if self.count_i == 0:
			pxs	= self.fragmented[240:]
			right = ((pxs[:,:-50]==5)*(pxs[:,50:]==6)).sum() > ((pxs[:,:-50]==6)*(pxs[:,50:]==5)).sum()
			self.motors.move(20, np.pi/2 * (-1 if right else 1), 0)
			self.motors.update()
			
		#if not self.motors.has_ball:#ball is lost
		#	self.set_state(1)
		#	return
		gate	= self.gates[self.gate]
		
		if gate is None:#gate lost, find gate
			self.set_state(self.S_FIND_GATE)
			return
			
		self.motors.move(self.motors.speed, self.motors.direction, gate[1] * 100)
		self.motors.update()
		
		if self.count_i > 60:
			self.set_state(self.S_AIM)
		
	def f_stalled(self):
		if self.count_i == 0:
			print('stalled')
			if not self.state == self.S_STALLEDB:
				self.last_state	= self.state
			self.motors.move(30, self.motors.direction + self.motors.DEG120, 0)#change dir
			self.motors.update()
		if self.count_i > 30:#drive 0.5s without checking stalled
			self.set_state(self.S_STALLEDB)
		
	def f_back_away_robot(self):
		if self.count_i > 30:#drive .5s
			self.set_state(self.last_state)
		
	def set_state(self, state):
		self.state	= state
		self.count_i	= 0
		print('logic: ' + self.state_names[state])
		self.history.append(time.strftime('%H:%M:%S') + ' ' + str(state) + ' ' + self.state_names[state])
		self.options[state]()
		
	def update_position(self):
		self.robot_x	+= self.motors.speed/64.0*np.cos(self.motors.direction+self.robot_dir)
		self.robot_y	+= self.motors.speed/64.0*np.sin(self.motors.direction+self.robot_dir)
		self.robot_dir	+= self.motors.angular_velocity/783.0
	
	def run(self):
		if self.open():
			print('logic: cam opened')
		else:
			print('logic: cam opening failed')
			return
		self.options = {
			self.S_MANUAL : self.f_manual,
			self.S_STALLED : self.f_stalled,
			self.S_STALLEDB : self.f_back_away_robot,
			self.S_FIND_LOST_BALL : self.f_find_lost_ball,
			self.S_FIND_GATE_FAR : self.f_find_gate_far,
			self.S_FIND_BALL : self.f_find_ball,
			self.S_FOLLOW_BALL : self.f_follow_ball,
			self.S_FOLLOW_BALL_BLIND : self.f_follow_ball_blind,
			self.S_FIND_GATE : self.f_find_gate,
			self.S_AIM : self.f_aim,
			self.S_FOLLOW_GATE_FAR : self.f_follow_gate_far,
			self.S_STRAFE : self.f_strafe,
			self.S_KICK : self.f_kick,
			self.S_TURN : self.f_turn,
			self.S_WAIT : self.f_wait
		}
		i	= 0
		timea	= time.time()
		while self.run_it:
			self.motors.read_buffers()
			if self.state is not self.S_WAIT:
				self.analyze_frame()
			else:
				time.sleep(0.2)
			if True in self.motors.stalled and self.state is not self.S_STALLED:
				self.set_state(self.S_STALLED)
			else:
				self.options[self.state]()
			self.update_position()
			
			self.count_i += 60.0 / self.fps
				
			#fps counter
			i += 1
			if i % 60 == 0:
				i = 0
				timeb	= time.time()
				self.fps	= 60 / (timeb - timea)
				timea	= timeb
				
			#self.profile -= 1
			#if self.profile < 0:
			#	self.run_it = False
		print('logic: close thread')
		self.motors.run_it	= False
		self.close()
