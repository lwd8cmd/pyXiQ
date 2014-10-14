# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Camera module

import numpy as np
import cv2
import threading
import cPickle as pickle

class Cam(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.run_it	= True
		self.UI	= False
		self.frame	= np.zeros((480,640,3))
		self.frame_balls	= []#balls[]=[x,y,w,h,area]
		self.fps	= '0'
		self.mins, self.maxs = pickle.load(open('colors.p', 'rb'))
		
	def open(self):
		self.cam = cv2.VideoCapture(0)
		return self.cam.isOpened()
			
	def close(self):
		self.cam.release()
		
	def ui_frame(self, t_ball):
		if self.UI:
			frame	= np.zeros((480,640,3))
			frame[t_ball > 0] = [0, 0, 255]#balls are shown as red
			self.frame	= frame
			
	def analyze_balls(self, t_ball):
		contours, hierarchy = cv2.findContours(t_ball, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		self.frame_balls	= []
		for contour in contours:
			s	= cv2.contourArea(contour)
			if s > 30:
				x, y, w, h = cv2.boundingRect(contour)
				ratio	= w / h
				#if ratio > 0.8 and ratio < 1.2:
				self.frame_balls.append([x, y, w, h, s])
		
	def analyze_frame(self):
		_, img = self.cam.read()
		img = cv2.GaussianBlur(img,(15,15),0)
		
		t_ball = cv2.inRange(img, self.mins[0], self.maxs[0])
		
		self.ui_frame(t_ball)
		self.analyze_balls(t_ball)