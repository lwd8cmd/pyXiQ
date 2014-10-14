# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Motors module

import serial
import numpy as np
import threading
import time

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
		
	def open(self):
		for port_nr in range(8):
			id_nr	= -1
			try:
				connection_opened = False
				while not connection_opened:
					connection = serial.Serial('/dev/ttyACM' + str(port_nr), baudrate=115200, timeout=1)
					connection_opened = connection.isOpen()
				while True:
					try:
						connection.write('?\n')
						id_string = connection.readline()
						if id_string[:4] == '<id:':
							id_nr = int(id_string[4])
							self.motors[id_nr - 1] = connection
							print('motors: motor ' + str(id_nr) + ' at port ' + str(port_nr))
							if not None in self.motors:
								self.is_opened = True
								return True
						break
					except:
						continue
			except:
				continue
		return False
	
	def close(self):
		for motor in self.motors:
			motor.write('sd0\n')
			motor.close()
	
	def move(self, speed, direction, omega):
		self.speed	= speed
		self.direction	= direction
		self.angular_velocity	= omega
		#r = 0.1#ratta raadius
		#l = 0.3#ratta kaugus roboti keskpunktist
		#self.sd1 = int(round(-speed*np.sin(direction)/(2*r) - np.sqrt(3)*speed*np.cos(direction)/(2*r) - l*omega/r));#esimese ratta kiirus
		#self.sd2 = int(round(-speed*np.sin(direction)/(2*r) + np.sqrt(3)*speed*np.cos(direction)/(2*r) - l*omega/r));#teise ratta kiirus
		#self.sd3 = int(round(speed*np.sin(direction)/r - l*omega/r));#kolmanda ratta kiirus
		
		speed*=10
		self.sd1 = int(round(speed*np.sin(direction-2*np.pi/3) - omega));#esimese ratta kiirus
		self.sd2 = int(round(speed*np.sin(direction+2*np.pi/3) - omega));#teise ratta kiirus
		self.sd3 = int(round(speed*np.sin(direction) - omega));#kolmanda ratta kiirus
		
	def update(self):
		if not self.is_opened:
			return
		if self.sd1 > 50 or self.sd2 > 50 or self.sd3 > 50:
			print('Too fast', self.sd1, self.sd2, self.sd3)
			return
		self.motors[0].write('sd' + str(self.sd1) + '\n')
		self.motors[1].write('sd' + str(self.sd2) + '\n')
		self.motors[2].write('sd' + str(self.sd3) + '\n')
		
	def run(self):
		if self.open():
			print('motors: opened')
		else:
			print('motors: opening failed')
			return
		while self.run_it:
			self.update()
			time.sleep(1)
		print('motors: close thread')
		self.close()
