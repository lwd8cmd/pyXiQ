# Color calibration for Ximea camera
# Lauri Hamarik 2015

import cv2
import numpy as np
import cPickle as pickle
import pyXiQ
import time

#load colortable
color_file = 'colors.pkl'
try:
	with open(color_file, 'rb') as fh:
		colors_lookup = pickle.load(fh)
except:
	colors_lookup	= np.zeros(0x1000000, dtype=np.uint8)

#open the camera
cam = pyXiQ.Camera()
if not cam.opened():
	print("cam not found")
	exit()

#camera settings
cam.setInt("exposure", 10000)
cam.setInt("downsampling", 2)
cam.setInt("auto_wb", 0)
#cam.setFloat("framerate", 30)
cam.start()# Start recording

def nothing(x):
	pass
	
#update colortable
def change_color():
	global update_i, noise, brush_size, mouse_x, mouse_y
	update_i	-= 1
	#brush (select adjacent pixels)
	ob		= image[max(0, mouse_y-brush_size):min(image.shape[0], mouse_y+brush_size+1),
					max(0, mouse_x-brush_size):min(image.shape[1], mouse_x+brush_size+1),:].reshape((-1,3)).astype('int32')
	#add noise (select close colors)
	noises		= xrange(-noise, noise+1)
	for a in noises:
		for b in noises:
			for c in noises:
				colors_lookup[((ob[:,0]+a) + (ob[:,1]+b) * 0x100 + (ob[:,2]+c) * 0x10000).clip(0,0xffffff)]	= color

# mouse callback function
def choose_color(event,x,y,flags,param):
	global update_i, noise, brush_size, mouse_x, mouse_y
	if event == cv2.EVENT_LBUTTONDOWN:
		mouse_x	= x
		mouse_y	= y
		brush_size	= cv2.getTrackbarPos('brush_size','settings')
		noise		= cv2.getTrackbarPos('noise','settings')
		update_i	= cv2.getTrackbarPos('frames','settings')
		change_color()
	
#opencv windows
cv2.namedWindow('settings')
cv2.namedWindow('tava')
cv2.namedWindow('mask')
cv2.moveWindow('mask', 400, 0)

cv2.createTrackbar('brush_size', 'settings', 3, 10, nothing)
cv2.createTrackbar('noise', 'settings', 1, 5, nothing)
cv2.createTrackbar('frames', 'settings', 10, 60, nothing)

cv2.setMouseCallback('tava', choose_color)
cv2.setMouseCallback('mask', choose_color)

# init values
mouse_x	= 0
mouse_y	= 0
brush_size	= 1
noise	= 1
color = 0
update_i	= 0
i 	= 0

print("Quit 'q', save 's', select color 0-9, erase color 'e', reset colors 'r'")
while True:
	image = cam.image()
	
	if update_i > 0:
		change_color()

	i	+= 1
	if i % 5 == 0:#display every n-th frame
		i	= 0
		cv2.imshow('tava', image)
		
		#threshold
		image	= image.astype('uint32')
		fragmented	= colors_lookup[image[:,:,0] + image[:,:,1] * 0x100 + image[:,:,2] * 0x10000]
		
		#show colors 0-8
		frame	= np.zeros(image.shape)
		frame[fragmented == 1] = np.array([0, 0, 255], dtype=np.uint8)#red
		frame[fragmented == 2] = np.array([0, 255, 255], dtype=np.uint8)#yellow
		frame[fragmented == 3] = np.array([255, 0, 0], dtype=np.uint8)#blue
		frame[fragmented == 4] = np.array([0, 255, 0], dtype=np.uint8)#green
		frame[fragmented == 5] = np.array([255, 255, 255], dtype=np.uint8)#white
		frame[fragmented == 6] = np.array([255, 255, 0], dtype=np.uint8)#dark green
		frame[fragmented == 7] = np.array([255, 0, 255], dtype=np.uint8)#dark green
		cv2.imshow('mask', frame)
	
	#key listener
	k = cv2.waitKey(1) & 0xff
	if k == ord('q'):
		break
	elif k == ord('s'):
		with open(color_file, 'wb') as fh:
			pickle.dump(colors_lookup, fh, -1)
		print('saved')
	elif k == ord('e'):
		colors_lookup[colors_lookup == color]	= 0
		print('erased color ' + str(color))
	elif k == ord('r'):
		colors_lookup[:]	= 0
		print('reset colors')
	elif k >= ord('0') and k <= ord('9'):
		color = k - ord('0')
		print('selected color ' + str(color))

cv2.destroyAllWindows()