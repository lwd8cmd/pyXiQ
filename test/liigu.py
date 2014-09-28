import serial
import numpy as np

if True:
	m2	= serial.Serial(2)
	m3	= serial.Serial(5)
	m1	= serial.Serial(6)
	
def cl():
	m1.close()
	m2.close()
	m3.close()

def move(speed, direction, omega):
	direction	*= -np.pi / 180
	omega	*= np.pi / 180
	r = 0.1#ratta raadius
	l = 0.3#ratta kaugus roboti keskpunktist
	phi1 = int(round(speed*np.sin(direction)/(2*r) - np.sqrt(3)*speed*np.cos(direction)/(2*r) - l*omega/r));#esimese ratta kiirus
	phi2 = int(round(speed*np.sin(direction)/(2*r) + np.sqrt(3)*speed*np.cos(direction)/(2*r) - l*omega/r));#teise ratta kiirus
	phi3 = int(round(-speed*np.sin(direction)/r - l*omega/r));#kolmanda ratta kiirus
	print(phi1, phi2, phi3)
	m1.write(bytes('sd' + str(phi1) + '\n', 'utf-8'))
	m2.write(bytes('sd' + str(phi2) + '\n', 'utf-8'))
	m3.write(bytes('sd' + str(phi3) + '\n', 'utf-8'))
if False:
	m1.close()
	m2.close()
	m3.close()