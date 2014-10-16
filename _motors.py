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
		#motor ids: 1=top left, 2=top right, 3=bottom
		self.motors	= [None, None, None]
		self.is_opened	= False
		self.speed	= 0
		self.direction	= 0
		self.angular_velocity	= 0
		self.sd1	= 0
		self.sd2	= 0
		self.sd3	= 0
		self.rsd1	= 0
		self.rsd2	= 0
		self.rsd3	= 0
		self.DEG120	= 2*np.pi/3
		self.buffers	= ['', '', '']
		self.stalled	= [False, False, False]
		
	def open(self, allow_reset = True):
		stdout = subprocess.check_output('ls /dev/ttyACM*', shell=True)
		for port in stdout.split('\n'):
			id_nr	= -1
			try:
				connection_opened = False
				while not connection_opened:
					connection = serial.Serial(port, baudrate=115200, timeout=0.5)
					connection_opened = connection.isOpen()
				i	= 0
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
		stdout	= subprocess.check_output(['lsusb'])
		usbs	= stdout.split('\n')
		for usb in usbs:
			if usb[23:32] == '16c0:047a':
				bus	= usb[4:7]
				device	= usb[15:18]
				comm	= 'sudo /home/mitupead/Desktop/robotex/usbreset /dev/bus/usb/'+bus+'/'+device
				stdout	= subprocess.check_output(comm, shell=True)
				print(stdout)
	
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
		self.sd1 = int(round(speed*np.sin(direction - self.DEG120) - omega))#esimese ratta kiirus
		self.sd2 = int(round(speed*np.sin(direction + self.DEG120) - omega))#teise ratta kiirus
		self.sd3 = int(round(speed*np.sin(direction) - omega))#kolmanda ratta kiirus
		
	def update(self):
		if not self.is_opened:
			return
		if self.sd1 > 150 or self.sd2 > 150 or self.sd3 > 150:
			print('Too fast', self.sd1, self.sd2, self.sd3)
			return
		self.motors[0].write('sd' + str(self.sd1) + '\n')
		self.motors[1].write('sd' + str(self.sd2) + '\n')
		self.motors[2].write('sd' + str(self.sd3) + '\n')
		
	def read_buffer(self):
		for i in range(3):
			while self.motors[i].inWaiting() > 0:
				char	= self.motors[i].read(1)
				if char == '\n':
					print(self.buffers[i])
					self.buffers[i]	= ''
				else:
					self.buffers[i] += char
		
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