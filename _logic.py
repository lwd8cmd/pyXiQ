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
		self.S_MANUAL, self.S_FIND_BALL, self.S_WAIT, self.S_STRAFE_BALL, self.S_YLARI, self.S_TURN, self.S_FOLLOW_BALL, self.S_FOLLOW_BALL_BLIND,\
			self.S_FIND_GATE, self.S_AIM, self.S_KICK, self.S_BACK_GATE, \
			self.S_FIND_GATE_FAR, self.S_FIND_LOST_BALL, self.S_FOLLOW_GATE_FAR, self.S_STRAFE, self.S_STALLED, self.S_STALLEDB \
			= range(18)
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
			self.S_TURN : 'poora',
			self.S_WAIT : 'oota',
			self.S_YLARI : 'ylari',
			self.S_BACK_GATE : 'tagurda varavast',
			self.S_STRAFE_BALL : 'streifi palliga'
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
		self.r_history	= deque([], maxlen=60)
		self.ball_blind_i	= 0
		self.history	= deque([], maxlen=9)
		self.has_ball_enabled = True
		self.ball_in_white	= False
		self.find_ball_i	= 0
		self.turn_ball_i	= 0
		self.strafe_right	= 1
		
	def r_history_clear(self):
		for i in range(5):
			self.r_history.append(i * 100)
			
	def r_history_add(self, r):
		self.r_history.append(r)
		if self.fps < 40:
			self.r_history.append(r)
		
	def f_manual(self):#manual mode, do nothing
		if self.count_i == 0:
			self.motors.move(0, 0, 0)
			self.motors.update()
			self.motors.coil_write('ts')
			
		gate	= self.gates[self.gate]		
		if False and gate is not None:
			ys, xs = np.mgrid[:480,:640]
			ylim	= gate[6]+gate[3]
			if gate[0] < 200:
				ylim = gate[6]+gate[3]//2+((self.fragmented[gate[6]+gate[3]//2:,318:323]==5).sum(1)>2).argmax()
			mask = (np.abs(xs-320) < 5 + ys * 0.162)*(ys>ylim)
			print(((self.fragmented==1)*mask).sum())
			self.t_debug = mask
			#print(self.t_ball[gate[6]+gate[3]:,318:323].sum())
		
		if False and self.largest_ball is not None:#ball is lost, find ball
			r = self.largest_ball[0]
			alpha	= self.largest_ball[1]
			#self.angle_history.append(alpha)
			print(self.largest_ball)
			
		if False and self.largest_ball is not None:
			x	= self.largest_ball[2] + self.largest_ball[4] // 2
			y	= self.largest_ball[3] + self.largest_ball[5]
			print((self.fragmented[max(0,y-30):min(480,y+30),max(0,x-40):min(640,x+40)]==5).sum())
			#self.ball_in_white
			
	def f_ylari(self):
		#self.motors.move(15, np.pi/2, -15)
		#self.motors.update()
		if self.largest_ball is not None:
			r = self.largest_ball[0]
			alpha	= self.largest_ball[1]
			print(r, alpha)
			self.motors.move(0, 0, alpha*150)
			self.motors.update()
			
	def f_wait(self):#wait
		if self.count_i == 0:
			self.motors.move(0, 0, 0)
			self.motors.update()
			self.motors.button = False
			self.motors.coil_write('ts')
			self.motors.coil_write('k10')
		self.motors.motor_write(1, 'gb')
		self.motors.read_buffer(1)
		if self.motors.button:
			self.set_state(self.S_FIND_BALL)
		
	def f_find_lost_ball(self):#back away until see ball
		if self.motors.has_ball:
			self.set_state(self.S_FIND_GATE)
			return
		if self.largest_ball is not None and self.largest_ball[6] > 10000:
			self.set_state(self.S_FOLLOW_BALL)
			return
		if self.count_i > 20:#timeout, find_ball
			self.set_state(self.S_FIND_BALL)
			return
			
	def f_turn(self):#turn to see smth else
		if self.count_i == 0:
			self.motors.move(0, 0, min(60, self.count_i*2+30))
			self.motors.update()
		if self.count_i > 25:#timeout, wait
			self.set_state(self.S_FIND_BALL)
		
	def f_find_ball(self):#turn until see ball
		if self.motors.has_ball and self.has_ball_enabled:
			self.set_state(self.S_FIND_GATE)
			return
		if self.largest_ball is not None:
			self.find_ball_i	= self.count_i
			self.set_state(self.S_FOLLOW_BALL)
			return
		if self.count_i > 110 * 60.0 / self.fps:#timeout, wait
			self.set_state(self.S_FIND_GATE_FAR)
			return
		if self.count_i == 0:
			self.count_i	= self.find_ball_i
		self.motors.move(0, 0, min(50, self.fps, self.count_i*2))
		self.motors.update()
		
	def f_follow_ball(self):
		if self.motors.has_ball and self.has_ball_enabled:
			self.set_state(self.S_FIND_GATE)
			return
		if self.largest_ball is None:#ball is lost, find ball
			self.set_state(self.S_FIND_BALL)
			return
		if self.count_i == 0:
			self.r_history_clear()
		if self.count_i > 20:
			self.find_ball_i = 0
			
		r = self.largest_ball[0]
		alpha	= self.largest_ball[1]
		self.r_history_add(r)
		if np.array(self.r_history).std() < 4:#stuck, ball not coming closer
			print('logic follow ball timeout')
			self.set_state(self.S_TURN)
			return
		turn_spd	= min(self.fps, alpha * 4000.0 / min(50, r))
		spd	= min(210 - abs(turn_spd),r*self.fps/30+10, self.count_i * 6 + 60)
		turn_spd -= spd * 0.08
		spd	= min(spd, 210 - abs(turn_spd))
		self.motors.move(spd, alpha, turn_spd)
		self.motors.update()
		if r < 19:#ball is going to the blind area, follow blind
			self.find_ball_i = 0
			x	= self.largest_ball[2] + self.largest_ball[4] // 2
			y	= self.largest_ball[3] + self.largest_ball[5]
			#self.ball_in_white = (self.fragmented[max(0,y-30):min(480,y+30),max(0,x-40):min(640,x+40)]==5).sum() > 100
			self.ball_in_white = False
			self.set_state(self.S_FOLLOW_BALL_BLIND)
			
	def f_follow_ball_blind(self):
		if self.count_i == 0:
			self.ball_blind_i += 1
			self.motors.coil_write('tg')
		if self.motors.has_ball and self.has_ball_enabled:
			self.set_state(self.S_FIND_GATE)
			return
		if self.count_i > 20 and not self.has_ball_enabled:
			self.set_state(self.S_FIND_GATE)
			return
		if self.largest_ball is not None and self.largest_ball[6] > 10000:
			r = self.largest_ball[0]
			alpha	= self.largest_ball[1]
			turn_spd	= min(self.fps, alpha * 4000.0 / r)
			spd	= r*1.3+10
			self.motors.move(spd, alpha, turn_spd)
			self.motors.update()
		if self.count_i > 20:
			if self.ball_blind_i > 2:
				self.set_state(self.S_TURN)
				return
			self.set_state(self.S_FIND_LOST_BALL)
			
	def f_find_gate(self):#turn until see gate
		if not self.motors.has_ball and self.has_ball_enabled:#ball is lost
			self.set_state(self.S_FIND_LOST_BALL)
			return
		if self.gates[self.gate] is not None:#gate found
			self.turn_ball_i = self.count_i
			self.set_state(self.S_AIM)
			return
		if self.count_i == 0:
			self.motors.coil_write('tg')
			if self.ball_in_white and self.gates[1-self.gate] is not None and self.gates[1-self.gate][0] < 70:
				self.ball_in_white = False
				self.set_state(self.S_BACK_GATE)
				return
		spd	= min(40, self.fps, self.count_i*2) * (1 if self.gates_last[self.gate][1] > 0 else -1)
		if self.ball_in_white: 
			self.motors.move(spd, -np.pi/2, spd)
		else:
			self.motors.move(max(0,(20-self.count_i*2)), 0, spd)#turn
		self.motors.update()
			
	def f_aim(self):
		if self.count_i	== 0:
			self.ball_blind_i = 0
		if not self.motors.has_ball and self.has_ball_enabled:#ball is lost
			self.set_state(self.S_FIND_LOST_BALL)
			return
		gate	= self.gates[self.gate]
		if gate is None:#gate lost, find gate
			self.set_state(self.S_FIND_GATE)
			return
		if np.abs(gate[1])*3000.0 < gate[2]:#gate in the center
			self.set_state(self.S_STRAFE)
			return
		spd	= max(15,min(40, self.fps, (self.count_i + self.turn_ball_i)*2, abs(gate[1] * 100))) * (1 if gate[1] > 0 else -1)
		if self.ball_in_white:
			self.motors.move(spd, -np.pi/2, spd)
		else:
			self.motors.move(0, 0, spd)
		self.motors.update()
		
	def f_kick(self):
		if self.count_i	== 0:
			if not self.motors.has_ball and self.has_ball_enabled:#ball is lost
				self.set_state(self.S_FIND_LOST_BALL)
				return
			gate	= self.gates[self.gate]
			if gate is None:#gate lost, find gate
				self.set_state(self.S_FIND_GATE)
				return
			self.motors.coil_kick(min(1000,gate[0]*2+400))
			self.motors.coil_write('ts')
			self.motors.move(0, 0, 0)
			self.motors.update()
		if self.count_i > 10:
			self.set_state(self.S_TURN)
			return
			
	def f_find_gate_far(self):
		if self.motors.has_ball and self.has_ball_enabled:
			self.set_state(self.S_FIND_GATE)
			return
		if self.largest_ball is not None:
			self.set_state(self.S_FOLLOW_BALL)
			return
		if self.count_i == 0:
			self.gate_far = 0 if self.gates_last[0][0] > self.gates_last[1][0] else 1
		if self.gates[self.gate_far] is not None:#gate found
			self.set_state(self.S_FOLLOW_GATE_FAR)
			return
		self.motors.move(0, 0, min(self.fps, self.count_i*2+20))
		self.motors.update()
			
	def f_follow_gate_far(self):
		if self.motors.has_ball and self.has_ball_enabled:
			self.set_state(self.S_FIND_GATE)
			return
		if self.largest_ball is not None:
			self.set_state(self.S_FOLLOW_BALL)
			return
		gate	= self.gates[self.gate_far]
		if gate is None:#gate is lost
			self.set_state(self.S_FIND_GATE_FAR)
			return
		if self.count_i == 0:
			self.r_history_clear()
		r	= gate[0]
		self.r_history_add(r)
		if np.array(self.r_history).std() < 5:
			print('logic follow gate timeout')
			self.set_state(self.S_TURN)
			return
		if r > 100:#follow
			alp = gate[1]*50
			self.motors.move(min(210 - abs(alp), (r - 50)*1.3, self.count_i*2 + 20), gate[1], alp)
			self.motors.update()
		else:#find ball
			self.set_state(self.S_FIND_BALL)
			
	def f_back_gate(self):
		if self.count_i	> 60:
			self.set_state(self.S_FIND_GATE)
			return
		self.motors.move(-min(40, self.count_i*2+1), 0, 0)
		self.motors.update()
			
	def f_strafe(self):
		if not self.motors.has_ball and self.has_ball_enabled:#ball is lost
			self.set_state(self.S_FIND_LOST_BALL)
			return
		gate	= self.gates[self.gate]
		if gate is None:#gate lost, find gate
			self.set_state(self.S_FIND_GATE)
			return
		if self.count_i > 180:
			self.set_state(self.S_KICK)
			return
		if not (gate[2]*gate[3]/gate[4] > 3.0 or (self.fragmented[gate[6]+gate[3]:425,320-20:320+20]==6).sum()>4000):#dont see side
			self.set_state(self.S_STRAFE_BALL)
			return
		if self.count_i == 0:
			pxs	= self.fragmented[240:425]
			self.strafe_right = 1 if ((pxs[:,:-50]==5)*(pxs[:,50:]==6)).sum() < ((pxs[:,:-50]==6)*(pxs[:,50:]==5)).sum() else -1
		self.motors.move(min(40, self.fps), np.pi/2 * self.strafe_right, gate[1] * self.fps * 2)
		self.motors.update()
		
	def f_strafe_ball(self):
		gate	= self.gates[self.gate]
		if gate is None:#gate lost, find gate
			self.set_state(self.S_FIND_GATE)
			return
		ys, xs = np.mgrid[:480,:640]
		gate	= self.gates[self.gate]
		ylim	= gate[6]+gate[3]
		if gate[0] < 200:
			ylim = gate[6]+gate[3]//2+((self.fragmented[gate[6]+gate[3]//2:,318:323]==5).sum(1)>2).argmax()
		mask = (self.fragmented==1)*(np.abs(xs-320) < self.W_b + ys * self.W_a)*(ys>ylim)
		msum	= mask.sum()
		if self.count_i == 0:
			self.strafe_right = 1 if (((xs < 320)*mask).sum() > msum/2) else -1
			self.count_j	= 0
		if msum < 10 and self.count_j > 15:
			self.set_state(self.S_KICK)
			return
		if self.count_i > 180:
			self.set_state(self.S_KICK)
			return
		if msum < 10:
			self.motors.move(0, 0, min(5, abs(gate[1]) * 100) * (1 if gate[1] > 0 else -1))
		else:
			self.motors.move(min(40, self.fps), np.pi/2 * self.strafe_right, gate[1] * self.fps * 2)
		self.motors.update()
		self.count_j += 60.0 / self.fps
		
	def f_stalled(self):
		if self.count_i == 0:
			self.motors.motor_write(1, 'gb')
			self.motors.read_buffer(1)
			if not self.motors.button:
				self.gate = 1 - self.gate
				self.set_state(self.S_WAIT)
				return
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
			self.run_it	= False
			self.motors.run_it	= False
			self.close()
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
			self.S_WAIT : self.f_wait,
			self.S_YLARI : self.f_ylari,
			self.S_BACK_GATE : self.f_back_gate,
			self.S_STRAFE_BALL : self.f_strafe_ball
		}
		i	= 0
		timea	= time.time()
		while self.run_it:
			#self.motors.motor_write(0, 'gb')
			self.motors.read_buffers()
			if self.state is not self.S_WAIT:
				self.analyze_frame()
			else:
				time.sleep(0.2)
			if True in self.motors.stalled and self.state is not self.S_STALLED and self.state is not self.S_WAIT:
				self.set_state(self.S_STALLED)
			else:
				self.options[self.state]()
			#self.update_position()
			
			self.count_i += 60.0 / self.fps
				
			#fps counter
			i += 1
			if i % 60 == 0:
				i = 0
				timeb	= time.time()
				self.fps	= 60 / (timeb - timea)
				timea	= timeb
			if i % 12 == 1:
				self.UI_screen()
				
			#self.profile -= 1
			#if self.profile < 0:
			#	self.run_it = False
		print('logic: close thread')
		self.motors.run_it	= False
		self.close()
