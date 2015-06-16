import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import scipy.ndimage
from scipy.optimize import curve_fit
import cPickle as pickle
import pyXiQ

def cmToPx(arr):#convert real coordinates to pixel coordinates
	return (arr*194.5/2950.0 + 30.0).astype(np.int16)
	
def findFiis(p, x0, y0, fii0):#convert pixel coordinates to angular coordinate
	xs = p[:,0] - x0
	ys = -(p[:,1] - y0)
	return np.arctan2(ys, xs) + fii0
	
def findDistances(rs, a, b, c):#convert pixel distances to real distances
	return a*rs**1 + b*rs**4 + c*rs**10

#get cam image
cam = pyXiQ.Camera()# Open the camera
if not cam.opened():
	print("cam not found")
	exit()
cam.setInt("exposure", 10000)
cam.start()# Start recording
cam_img = cam.image()

downsample = 4
upsample = 4
h, w, _ = cam_img.shape
dh = h // 2 // downsample // upsample
dw = w // 2 // downsample // upsample
img = cam_img[::downsample,::downsample]
cv2.namedWindow('pilt')

#mouse click listener
click_yx = None
def choose_loc(event, _x, _y, flags, param):
	global click_yx
	if event == cv2.EVENT_LBUTTONDOWN:
		click_yx = [_y, _x]
			
cv2.setMouseCallback('pilt', choose_loc)

select_points = True
if 0:#calibrate from the image
	#select calibration points in the image
	points_img = []
	points_real = []
	while select_points:#select new point
		x = raw_input("Ball x-coordinate (mm) or q to quit:")
		if x == 'q':
			break
		y = raw_input("Ball y-coordinate (mm) or q to quit:")
		if y == 'q':
			break
		points_real.append([int(x), int(y)])
		print('Press q to quit, b to zoom out. Click on the ball.')
		zoom = False
		click_yx = None
		while True:#wait until user clicks 2 times
			if click_yx:
				if zoom:
					points_img.append([click_yx[1] // upsample + max(0, w-x-dw), click_yx[0] // upsample + max(0, y-dh)])
					break
				else:
					zoom = True
					y = click_yx[0] * downsample
					x = click_yx[1] * downsample
					click_yx = None
			cam_img = cam.image()
			if zoom:
				img = scipy.ndimage.zoom(cam_img[max(0, y-dh):min(h, y+dh),max(0, w-x-dw):min(w, w-x+dw)], (upsample, upsample, 1))
			else:
				img = cam_img[::downsample,::downsample]
			cv2.imshow('pilt', img[:,::-1])
			k = cv2.waitKey(1) & 0xff
			if k == ord('q'):
				select_points = False
				break
			elif k == ord('b'):
				zoom = False
else:#presaved points
	points_real = [[ -500,     0],
       [-1000,     0],
       [-2000,     0],
       [    0,   300],
       [    0,   750],
       [    0,  1500],
       [  400,     0],
       [  900,     0],
       [ 2500,     0]]
	   
	points_img = [[ 499,  477],
       [ 401,  477],
       [ 297,  473],
       [ 625,  539],
       [ 623,  669],
       [ 633,  785],
       [ 733,  476],
       [ 848,  478],
       [1009,  476]]

#fit parameters
points_real = np.array(points_real)
points_img = np.array(points_img)
print('Real coordinates: ', points_real)
print('Pixel coordinates: ', points_img)

#angular calibration
p0 = [w/2, h/2, 0.0]
fiis_r = np.arctan2(points_real[:,0], points_real[:,1])
p1, pcov = curve_fit(findFiis, points_img, fiis_r, p0=p0)
calib_fiis = findFiis(points_img, p1[0], p1[1], p1[2])
print('angular calibration', p1)
print('real fiis', fiis_r/np.pi*180)
print('calib fiis', calib_fiis/np.pi*180)
x0, y0, fii0 = p1

#distance calibration
xs = points_img[:,0] - x0
ys = points_img[:,1] - y0
rs = (xs**2 + ys**2)**0.5
real_rs = (points_real[:,0]**2 + points_real[:,1]**2)**0.5
p2 = [5e-1, 1e-9, 1e-25]
p3, pcov = curve_fit(findDistances, rs, real_rs, p0=p2)
calib_rs = findDistances(rs, p3[0], p3[1], p3[2])
print('distance calibration', p3)
print('real distances', real_rs)
print('calib distances', calib_rs)

points_calib = np.zeros(points_real.shape)
points_calib[:,0] = calib_rs*np.sin(calib_fiis)
points_calib[:,1] = calib_rs*np.cos(calib_fiis)
	
_diffs = points_calib - points_real
print('Mean error: {merr} mm'.format(merr=np.abs((_diffs[:,0]**2+_diffs[:,1]**2)**0.5).mean()))
	
#print real and fitted coordinates
print('/----+------------------+-------------------\\')
print('| nr | real coordinates | fitted coordinates|')
print('+----+------------------+-------------------+')
_real = np.around(points_real).astype(np.int16)
_fitted = np.around(points_calib).astype(np.int16)
for i in xrange(len(points_real)):
	print('|{i: >3} |{r[1]: >8},{r[0]: >8} |{f[1]: >8},{f[0]: >8}  |'.format(i=i, r=_real[i], f=_fitted[i]))
print('\\----+------------------+-------------------/')

if 1:#show fitted curve (real distance vs pixel distance)
	ys = real_rs
	xs = rs
	plt.plot(xs, ys, 'x')
	xs2 = np.linspace(0, rs.max()*1.1, 100)
	ys2 = findDistances(xs2, p3[0], p3[1], p3[2])
	plt.plot(xs2, ys2, '-')
	plt.xlabel('pixel distance')
	plt.ylabel('real distance')
	plt.show()
	
if raw_input("Save conf (y/n): ") == 'y':
	ys, xs = np.mgrid[:h,:w]
	
	ys = ys - y0
	xs = w - xs - x0
	fiis = (((np.arctan2(ys, xs)-fii0)%(2*np.pi))/(2*np.pi)*65536).clip(min=0, max=65535).astype(np.uint16)
	rs = (xs**2 + ys**2)**0.5
	distances = (findDistances(rs, p3[0], p3[1], p3[2])).clip(min=0, max=65535).astype(np.uint16)
	
	#show fiis map
	plt.title('angles')
	plt.imshow(fiis[:,::-1])
	plt.colorbar()
	plt.show()
	
	#show distances map
	plt.title('distances')
	plt.imshow(distances[:,::-1])
	plt.colorbar()
	plt.show()
	
	with open('calibration/locations.pkl', 'wb') as fh:
		pickle.dump((distances, fiis), fh, -1)
	print('saved')