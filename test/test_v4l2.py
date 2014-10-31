import numpy as np
import cv2
import time
import subprocess

subprocess.check_output('v4l2-ctl -d /dev/video0 -c brightness=0,contrast=36,saturation=96'\
	+',sharpness=5,gain=16,exposure=255,red_balance=128,blue_balance=128,gamma=128'\
	+',white_balance_automatic=1,auto_exposure=0,gain_automatic=0', shell=True)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
	print('could not open')
	exit()
	
for x in xrange(60):
	_, frame = cap.read()
	
parms = subprocess.check_output('v4l2-ctl -d /dev/video0 -C exposure', shell=True)
exposure	= 0
for line in parms.split('\n')[:-1]:
	if line[:8] == 'exposure':
		exposure = int(line[10:])
		
print('exposure=' + str(exposure))
subprocess.check_output('v4l2-ctl -d /dev/video0 -c auto_exposure=1,exposure='+str(exposure), shell=True)

#subprocess.check_output('v4l2-ctl -d /dev/video0 -c white_balance_automatic=1,gain_automatic=1,auto_exposure=0', shell=True)
for x in xrange(5):
	_, frame = cap.read()
frame_comp	= frame.copy().astype('int16')
subprocess.check_output('v4l2-ctl -d /dev/video0 -c white_balance_automatic=0', shell=True)

step	= 8#32
edges	= 3#1
red		= 118
green	= 128
blue	= 140
xgreen = green
while step > 0:#1:
	diffsa	= []
	for xred in xrange(red - edges*step, red + (edges+1)*step, step):
		diffsb	= []
		#for xgreen in xrange(green - edges*step, green + (edges+1)*step, step):
		if True:
			diffsc	= []
			for xblue in xrange(blue - edges*step, blue + (edges+1)*step, step):
				subprocess.check_output('v4l2-ctl -d /dev/video0 -c red_balance='+str(xred)\
				+',gamma='+str(xgreen)+',blue_balance='+str(xblue), shell=True)
				for x in xrange(5):
					_, frame = cap.read()
				diffsc.append(np.abs(frame_comp - frame.astype('int16')).mean())
			diffsb.append(diffsc)
		diffsa.append(diffsb)
	diffsa	= np.array(diffsa)
	redi, greeni, bluei = np.unravel_index(diffsa.argmin(), diffsa.shape)
	red += (redi - edges)*step
	#green += (greeni - edges)*step
	blue += (bluei - edges)*step
	print('red='+str(red)+',green='+str(green)+',blue='+str(blue)+',delta='+str(step))
	step /= 2
	break
	
import pickle
with open('calib.pkl', 'wb') as out:
	pickle.dump(diffsa, out, -1)
	
cap.release()