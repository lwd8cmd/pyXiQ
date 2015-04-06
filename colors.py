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

cam = pyXiQ.Camera()# Open the camera
if not cam.opened():
	print("cam not found")
	exit()
#cam settings
cam.setParamInt("exposure", 30000)
#cam.setParamInt("downsampling", 2)
cam.setParamInt("auto_wb", 0)
cam.setParamFloat("framerate", 10)
cam.start()# Start recording

#opencv windows
cv2.namedWindow('settings')
cv2.namedWindow('tava')
cv2.namedWindow('mask')
cv2.moveWindow('mask', 400, 0)

def nothing(x):
	pass

cv2.createTrackbar('brush_size', 'settings', 3, 10, nothing)
cv2.createTrackbar('noise', 'settings', 1, 5, nothing)
cv2.createTrackbar('frames', 'settings', 1, 60, nothing)

# init values
mouse_x	= 0
mouse_y	= 0
brush_size	= 1
noise	= 1
p = 0
update_i	= 0

def change_color():#update colortable
	global update_i, noise, brush_size, mouse_x, mouse_y
	update_i	-= 1
	ob		= image[max(0, mouse_y-brush_size):min(image.shape[0], mouse_y+brush_size+1),
					max(0, mouse_x-brush_size):min(image.shape[1], mouse_x+brush_size+1),:].reshape((-1,3)).astype('int32')
	noises		= xrange(-noise, noise+1)
	for a in noises:
		for b in noises:
			for c in noises:
				colors_lookup[((ob[:,0]+a) + (ob[:,1]+b) * 0x100 + (ob[:,2]+c) * 0x10000).clip(0,0xffffff)]	= p

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

cv2.setMouseCallback('tava', choose_color)
cv2.setMouseCallback('mask', choose_color)

print("V2ljumiseks vajutada t2hte 'q', v22rtuste salvestamiseks 's', v22rtuste kustutamiseks 'e'")
print("Palli confimiseks 'r', kollane='y', sinine='b', roheline='g', valge='w', tumeroheline='d', muu='o'")

i 	= 0
while True:
	image = cam.image()
	
	if update_i > 0:
		change_color()

	i	+= 1
	if True:#i % 5 == 0:# Display the resulting frame
		i	= 0
		cv2.imshow('tava', image)
		
		image	= image.astype('uint32')
		fragmented	= colors_lookup[image[:,:,0] + image[:,:,1] * 0x100 + image[:,:,2] * 0x10000]
		frame	= np.zeros(image.shape)
		frame[fragmented == 1] = np.array([0, 0, 255], dtype=np.uint8)#balls are shown as red
		frame[fragmented == 2] = np.array([0, 255, 255], dtype=np.uint8)#yellow gate is yellow
		frame[fragmented == 3] = np.array([255, 0, 0], dtype=np.uint8)#blue gate
		frame[fragmented == 4] = np.array([0, 255, 0], dtype=np.uint8)#green
		frame[fragmented == 5] = np.array([255, 255, 255], dtype=np.uint8)#white
		frame[fragmented == 6] = np.array([255, 255, 0], dtype=np.uint8)#dark green
		cv2.imshow('mask', frame)
	
	k = cv2.waitKey(1) & 0xff

	if k == ord('q'):
		break
	elif k == ord('r'):
		print('balls')
		p = 1
	elif k == ord('y'):
		print('yellow gate')
		p = 2
	elif k == ord('b'):
		print('blue gate')
		p = 3
	elif k == ord('g'):
		print('green')
		p = 4
	elif k == ord('w'):
		print('white')
		p = 5
	elif k == ord('d'):
		print('dark green')
		p = 6
	elif k == ord('o'):
		print('everything else')
		p = 0
	elif k == ord('s'):
		with open(color_file, 'wb') as fh:
			pickle.dump(colors_lookup, fh, -1)
		print('saved')
	elif k == ord('e'):
		print('erased')
		colors_lookup[colors_lookup == p]	= 0

# When everything done, release the capture
cam.close()# Close camera
cv2.destroyAllWindows()
