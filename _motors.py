# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Motors module

import serial
import numpy as np
import threading
import time
import subprocess

class Motors(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.run_it	= True
		self.DEG120	= 2*np.pi/3
		#motor ids: 1=top left, 2=top right, 3=bottom
		self.motors	= [None, None, None]
		self.sds	= [0, 0, 0]#motor speeds
		self.rsds	= [0, 0, 0]#real motor speeds
		self.buffers	= ['', '', '']
		self.stalled	= [False, False, False]
		self.angles	= [-self.DEG120, self.DEG120, 0]
		self.is_opened	= False
		self.speed	= 0
		self.direction	= 0
		self.angular_velocity	= 0
		
	def open(self, allow_reset = True):
		try:
			ports = subprocess.check_output('ls /dev/ttyACM*', shell=True).split('\n')[:-1]
		except:
			print('motors: /dev/ttyACM empty')
			return False
		for port in ports:
			id_nr	= -1
			try:
				connection_opened = False
				while not connection_opened:
					connection = serial.Serial(port, baudrate=115200, timeout=1)
					connection_opened = connection.isOpen()
				i	= 0
				#connection.flush()
				while True:
					try:
						i	+= 1
						if i > 4:
							break
						connection.write('?\n')
						id_string = connection.readline()
						print('motors: readline ' + port + ', ' + id_string.rstrip())
						if id_string[:4] == '<id:':#~x~~x~?\n
							id_nr = int(id_string[4])
							self.motors[id_nr - 1] = connection
							print('motors: motor ' + str(id_nr) + ' at ' + port)
							if not None in self.motors:
								self.is_opened = True
								return True
							break
					except:
						continue
			except:
				continue
		if allow_reset:
			self.close()
			self.reset_usb()
			return self.open(False)
		else:
			return False
			
	def reset_usb(self):
		print('motors: reset USB')
		for usb in subprocess.check_output(['lsusb']).split('\n')[:-1]:
			if usb[23:32] == '16c0:047a':
				comm	= 'sudo /home/mitupead/Desktop/robotex/usbreset /dev/bus/usb/'+usb[4:7]+'/'+usb[15:18]
				print(subprocess.check_output(comm, shell=True))
		time.sleep(1)
	
	def close(self):
		for motor in self.motors:
			if motor is not None:
				if motor.isOpen():
					motor.write('sd0\n')
				motor.close()
		self.motors	= [None, None, None]
	
	def move(self, speed, direction, omega):
		self.speed	= speed
		self.direction	= direction
		self.angular_velocity	= omega
		self.sds	= [int(round(speed*np.sin(direction + self.angles[i]) - omega)) for i in range(3)]
		
	def read_buffer(self, i):
		while self.motors[i].inWaiting() > 0:
			char	= self.motors[i].read(1)
			if char == '\n':
				print(i, self.buffers[i])
				if self.buffers[i][:7] == '<stall:':
					self.stalled[i]	= not self.buffers[i][7:8] == '0'
				self.buffers[i]	= ''
			else:
				self.buffers[i] += char
		
	def update(self):
		if not self.is_opened:
			return
		if max(self.sds) > 150:
			print('motors: too fast', self.sds)
			return
		for i in range(3):
			self.motors[i].write('sd' + str(self.sds[i]) + '\n')
			self.read_buffer(i)
		
	def run(self):
		if self.open():
			print('motors: opened')
		else:
			print('motors: opening failed')
			self.close()
			return
		while self.run_it:
			self.update()
			time.sleep(1)
		print('motors: close thread')
		self.close()
