# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Camera module

import numpy as np
import cv2
import threading
import cPickle as pickle
import subprocess
import time
import segment
from collections import deque

try:
	import _cam_settings
except:
	print('cam: settings not set')

class Cam(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.run_it	= True
		self.gate	= 0#0==yellow,1==blue
		self.gates	= [None, None]
		self.gates_last = [[999, 0], [999, 0]]
		self.frame_balls	= []#balls[]=[x,y,w,h,area]
		self.largest_ball	= None
		self.fps	= 60
		with open('colors/colors.pkl', 'rb') as fh:
			self.colors_lookup = pickle.load(fh)
			segment.set_table(self.colors_lookup)
		self.CAM_D_ANGLE	= 60 * np.pi / 180 / 640
		with open('distances.pkl', 'rb') as fh:
			self.CAM_HEIGHT, self.CAM_DISTANCE, self.CAM_ANGLE, self.Y_FAR, self.W_a, self.W_b = pickle.load(fh)
		self.H_BALL	= 2.15#half height
		self.H_GATE	= 10
		self.fragmented	= np.zeros((480,640), dtype=np.uint8)
		self.t_ball = np.zeros((480,640), dtype=np.uint8)
		self.t_gatey = np.zeros((480,640), dtype=np.uint8)
		self.t_gateb	= np.zeros((480,640), dtype=np.uint8)
		self.t_debug	= np.zeros((480,640,3), dtype=np.uint8)
		self.debugi	= 0
		self.ball_history	= deque([], maxlen=60)
		self.gate	= 0
		
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
		time.sleep(3)
		self.cam = cv2.VideoCapture(0)
		return self.cam.isOpened()
			
	def close(self):
		try:
			self.cam.release()
		except:
			print('cam: close err')
		
	def calc_location(self, x, y, h):
		d	= (self.CAM_HEIGHT - h) * np.tan(self.CAM_ANGLE - self.CAM_D_ANGLE * y) - self.CAM_DISTANCE
		alpha	= self.CAM_D_ANGLE * (x - 320)+0.063#+0.04# + 0.04#0.0082
		r	= d / np.cos(alpha)
		return (r, alpha)
			
	def analyze_balls(self, t_ball):
		contours, hierarchy = cv2.findContours(t_ball, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		self.largest_ball	= None
		s_max	= 0
		self.frame_balls	= []
		#self.t_debug	= np.zeros((480,640), dtype=np.uint8)
		for contour in contours:
			s	= cv2.contourArea(contour)
			if s < 4:
				#print('small', s)
				continue
			x, y, w, h = cv2.boundingRect(contour)
			if s < 10 and y > self.Y_FAR:
				#print('small2', s, y)
				continue
			ratio	= float(w) / h
			if y + h > 477 and s > 25:
				s += 10000
				ratio	= 1
			if ratio < 0.5 or ratio > 2.0:
				#print('ratio', ratio)
				continue
			ys	= np.repeat(np.arange(y + h, 480), 5)
			xs	= np.linspace(x + w / 2, 320, num=len(ys)/5).astype('uint16')
			xs	= np.repeat(xs, 5)
			xs[::5] -= 2
			xs[1::5] -= 1
			xs[3::5] += 1
			xs[4::5] += 2
			pxs	= self.fragmented[ys, xs]
			black_pixs	= sum([((pxs[:-i]==6)*(pxs[i:]==5)).sum() for i in xrange(15,20)])
			if black_pixs > 10:
				#print('black', black_pixs)
				continue
			if s > 10000:
				coords	= self.calc_location(x + w / 2, y, 2*self.H_BALL)
			else:
				coords	= self.calc_location(x + w / 2, y + h / 2, self.H_BALL)
			if coords[0] > 300:
				#print('far', coords[0])
				continue
			self.frame_balls.append(coords)
			if s > s_max:
				s_max	= s
				self.largest_ball	= [coords[0], coords[1], x, y, w, h, s]
					
	def analyze_gate(self, t_gate, gate_nr):
		contours, hierarchy = cv2.findContours(t_gate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		self.gates[gate_nr]	= None
		s_max	= 0
		self.debugi += 1
		for contour in contours:
			s	= cv2.contourArea(contour)
			if s < 500:
				continue
			x, y, w, h = cv2.boundingRect(contour)
			if (h < 18 and y > 2) or (h < 6 and w < 20):
				continue
			r, alpha	= self.calc_location(x + w / 2, y + h / 2, self.H_GATE)
			if s > s_max:
				s_max	= s
				self.gates[gate_nr]	= [r, alpha, w, h, s, x, y]
				self.gates_last[gate_nr]	= [r, alpha]
		
	def analyze_frame(self):
		#try:
			_, img = self.cam.read()
			segment.segment(img, self.fragmented, self.t_ball, self.t_gatey, self.t_gateb)
			self.analyze_balls(self.t_ball)
			self.analyze_gate((self.t_gatey if self.gate == 0 else self.t_gateb), self.gate)
			if self.gates[self.gate] is None:
				self.analyze_gate((self.t_gateb if self.gate == 0 else self.t_gatey), 1 - self.gate)
		#except:
		#	print('cam: except')

	def UI_screen(self):
		self.t_debug	= np.zeros((480,640,3), dtype=np.uint8)
		self.t_debug[self.t_ball > 0] = [0, 0, 255]#balls are shown as red
		self.t_debug[self.t_gatey > 0] = [0, 255, 255]#yellow gate is yellow
		self.t_debug[self.fragmented == 4] = [0, 255, 0]#green
		self.t_debug[self.fragmented == 5] = [255, 255, 255]#white
		self.t_debug[self.fragmented == 6] = [255, 255, 0]#dark
		self.t_debug[self.t_gateb > 0] = [255, 0, 0]#blue gate
		self.t_debug[:,320]	= [0,0,0]
		tmp_f	= self.largest_ball
		if tmp_f is not None:
			self.t_debug[tmp_f[3] + tmp_f[5] // 2,:] = [0, 0, 255]#locked ball horizontal
			self.t_debug[:,tmp_f[2] + tmp_f[4] // 2] = [0, 0, 255]#locked ball vertical