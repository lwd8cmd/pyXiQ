# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Camera module

import numpy as np
import cv2
import threading
import cPickle as pickle
import subprocess
import _cam_settings
import time
import segment

class Cam(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.run_it	= True
		self.frame_balls	= []#balls[]=[x,y,w,h,area]
		self.gates	= [None, None]
		self.largest_ball	= None
		self.gate_right	= True
		self.fps	= '0'
		with open('colors.pkl', 'rb') as fh:
			self.colors_lookup = pickle.load(fh)
			segment.set_table(self.colors_lookup)
		self.CAM_D_ANGLE	= 60 * np.pi / 180 / 640
		with open('distances.pkl', 'rb') as fh:
			self.CAM_HEIGHT, self.CAM_DISTANCE, self.CAM_ANGLE = pickle.load(fh)
		self.H_BALL	= 2.15#half height
		self.H_GATE	= 10
		self.fragmented	= np.zeros((480,640), dtype=np.uint8)
		self.t_ball = np.zeros((480,640), dtype=np.uint8)
		self.t_gatey = np.zeros((480,640), dtype=np.uint8)
		self.t_gateb	= np.zeros((480,640), dtype=np.uint8)
		self.gate	= 0#0==yellow,1==blue
		
	def open(self):
		self.cam = cv2.VideoCapture(0)
		if self.cam.isOpened():
			return True
		self.cam.release()
		print('cam: reset USB')
		for usb in subprocess.check_output(['lsusb']).split('\n')[:-1]:
			if usb[23:32] == '1415:2000':
				comm	= 'sudo /home/mitupead/Desktop/robotex/usbreset /dev/bus/usb/'+usb[4:7]+'/'+usb[15:18]
				print(subprocess.check_output(comm, shell=True))
		time.sleep(1)
		self.cam = cv2.VideoCapture(0)
		return self.cam.isOpened()
			
	def close(self):
		self.cam.release()
		
	def calc_location(self, x, y, is_ball):
		d	= (self.CAM_HEIGHT - (self.H_BALL if is_ball else self.H_GATE)) * np.tan(self.CAM_ANGLE - self.CAM_D_ANGLE * y) - self.CAM_DISTANCE
		alpha	= self.CAM_D_ANGLE * (x - 320)
		r	= d / np.cos(alpha)
		return (r, alpha)
			
	def analyze_balls(self, t_ball):
		contours, hierarchy = cv2.findContours(t_ball, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		self.largest_ball	= None
		s_max	= 0
		self.frame_balls	= []
		for contour in contours:
			s	= cv2.contourArea(contour)
			if s > 10:
				x, y, w, h = cv2.boundingRect(contour)
				ratio	= float(w) / h
				ratio	= max(ratio, 1/ratio)
				if ratio < 1.2 or (ratio < 1.4 and w < 10) or (ratio < 1.7 and w < 9):
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
			if s > 250:
				x, y, w, h = cv2.boundingRect(contour)
				#ratio	= w / h
				#if ratio > 0.8 and ratio < 1.2:
				coords	= self.calc_location(x + w / 2, y + h / 2, False)
				if s > s_max:
					s_max	= s
					self.gates[gate_nr]	= coords
		
	def analyze_frame(self):
		_, img = self.cam.read()
		segment.segment(img, self.fragmented, self.t_ball, self.t_gatey, self.t_gateb)
		#yuv	= img.astype('uint32')
		#fragmented	= self.colors_lookup[yuv[:,:,0] + yuv[:,:,1] * 0x100 + yuv[:,:,2] * 0x10000]
		
		#self.t_ball = (fragmented == 1).view('uint8')
		#self.t_gatey = (fragmented == 2).view('uint8')
		#self.t_gateb = (fragmented == 3).view('uint8')
		
		self.analyze_balls(self.t_ball)
		self.analyze_gate(self.t_gatey, 0)
		self.analyze_gate(self.t_gateb, 1)
		if self.gates[self.gate] is not None:
			self.gate_right = self.gates[self.gate][1] > 0