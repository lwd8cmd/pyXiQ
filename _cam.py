# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Camera module

import numpy as np
import cv2
import threading
import cPickle as pickle
import subprocess

class Cam(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.run_it	= True
		self.UI	= False
		self.frame	= np.zeros((480,640,3))
		self.frame_balls	= []#balls[]=[x,y,w,h,area]
		self.gates	= [None, None]
		self.largest_ball	= None
		self.fps	= '0'
		self.mins, self.maxs = pickle.load(open('colors.p', 'rb'))
		self.CAM_D_ANGLE	= 60 * np.pi / 180 / 640
		self.CAM_HEIGHT, self.CAM_DISTANCE, self.CAM_ANGLE = pickle.load(open('distances.p', 'rb'))
		self.H_BALL	= 2.15#half height
		self.H_GATE	= 10
		
		print('cam: V4L2 settings')
		subprocess.check_output('v4l2-ctl -d /dev/video0 -c white_balance_automatic=0 -c gain_automatic=0 -c auto_exposure=1', shell=True)
		
	def open(self):
		self.cam = cv2.VideoCapture(0)
		return self.cam.isOpened()
			
	def close(self):
		self.cam.release()
		
	def calc_location(self, x, y, is_ball):
		d	= (self.CAM_HEIGHT + (self.H_BALL if is_ball else self.H_GATE)) * np.tan(self.CAM_ANGLE - self.CAM_D_ANGLE * y) - self.CAM_DISTANCE
		alpha	= self.CAM_D_ANGLE * (x - 320)
		r	= d / np.cos(alpha)
		return (r, alpha)
		
	def ui_frame(self, t_ball, t_gatey, t_gateb):
		if self.UI:
			frame	= np.zeros((480,640,3))
			frame[t_ball > 0] = [0, 0, 255]#balls are shown as red
			frame[t_gatey > 0] = [0, 255, 255]#yellow gate is yellow
			frame[t_gateb > 0] = [255, 0, 0]#captain obvious is obvious
			self.frame	= frame
			
	def analyze_balls(self, t_ball):
		contours, hierarchy = cv2.findContours(t_ball, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		self.largest_ball	= None
		s_max	= 0
		self.frame_balls	= []
		for contour in contours:
			s	= cv2.contourArea(contour)
			if s > 30:
				x, y, w, h = cv2.boundingRect(contour)
				ratio	= w / h
				#if ratio > 0.8 and ratio < 1.2:
				coords	= self.calc_location(x + w / 2, y + h / 2, True)
				self.frame_balls.append(coords)
				if s > s_max:
					s_max	= s
					self.largest_ball	= coords
					
	def analyze_gate(self, t_gate, gate_nr):
		contours, hierarchy = cv2.findContours(t_gate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		self.gates[gate_nr]	= None
		s_max	= 0
		for contour in contours:
			s	= cv2.contourArea(contour)
			if s > 30:
				x, y, w, h = cv2.boundingRect(contour)
				ratio	= w / h
				#if ratio > 0.8 and ratio < 1.2:
				coords	= self.calc_location(x + w / 2, y + h / 2, False)
				if s > s_max:
					s_max	= s
					self.gates[gate_nr]	= coords
		
	def analyze_frame(self):
		_, img = self.cam.read()
		img = cv2.GaussianBlur(img,(3,3),0)
		
		t_ball = cv2.inRange(img, self.mins[0], self.maxs[0])
		t_gatey = cv2.inRange(img, self.mins[1], self.maxs[1])
		t_gateb = cv2.inRange(img, self.mins[2], self.maxs[2])
		
		self.ui_frame(t_ball, t_gatey, t_gateb)
		self.analyze_balls(t_ball)
		self.analyze_gate(t_gatey, 0)
		self.analyze_gate(t_gateb, 1)