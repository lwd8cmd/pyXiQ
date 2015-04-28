import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import scipy.ndimage
from scipy.optimize import curve_fit
import cPickle as pickle
import pyXiQ

def cmToPx(arr):#convert real coordinates to pixel coordinates
	return (arr*194.5/2950.0 + 30.0).astype(np.uint16)
	
def pxToCm(p, y0, x0, a, b, c):#convert pixel coordinates to real coordinates
	ys = p[:,0] - y0
	xs = p[:,1] - x0
	fiis = np.arctan2(ys, xs)
	rs = (xs**2 + ys**2)**0.5
	distances = a*rs**1 + b*rs**4 + c*rs**10
	
	res = np.zeros(p.shape)
	res[:,0] = distances*np.sin(fiis)
	res[:,1] = distances*np.cos(fiis)
	return res.flatten()

#define real points in the field (in mm) used during calibration
l = 50.0
x = 4600.0 - 3*l
y = 3100.0 - 3*l
d = 800.0 - l
g = (y - 350.0 - 2*500.0 + l) / 2
gate = 700.0 + 2*20.0

points = np.array([
	[0,		0],
	[y,		0],
	[0,		x/2],
	[y,		x/2],
	[0,		x],
	[y,		x],
	
	[g,		0],
	[y-g,	0],
	[g,		x],
	[y-g,	x],
	
	[(y-d)/2,	x/2],
	[(y+d)/2,	x/2],
	
	[(y-gate)/2,	-l*1.5],
	[(y+gate)/2,	-l*1.5],
	
	[0,	140.0]
])
points_tuple = [(p[1], p[0]) for p in cmToPx(points)]
curpoint = 0
	
#get cam image
cam = pyXiQ.Camera()# Open the camera
if not cam.opened():
	print("cam not found")
	exit()
cam.setInt("exposure", 10000)
cam.start()# Start recording
cam_img = cam.image()
cam.stop()
#cam_img = np.array(Image.open('servas.jpg'))[::-1,::-1,::-1]
downsample = 4
upsample = 4
h, w, _ = cam_img.shape
dh = h // 2 // downsample // upsample
dw = w // 2 // downsample // upsample
img = cam_img[::downsample,::downsample]
cv2.namedWindow('pilt')

#get field image
field = np.array(Image.open('valjak.png'))
cv2.namedWindow('valjak')
cv2.moveWindow('valjak', 80, 330)

#mouse click listener
click_yx = None
def choose_loc(event, _x, _y, flags, param):
	global click_yx
	if event == cv2.EVENT_LBUTTONDOWN:
		click_yx = [_y, _x]
			
cv2.setMouseCallback('pilt', choose_loc)

if 1:#calibrate from the image
	#select calibration points in the image
	points_selected = []
	zoom = False
	print('Press q to quit')
	while curpoint < len(points):
		cv2.imshow('pilt', img)
		cv2.circle(field, points_tuple[curpoint], 5, (0,0,255), -1)
		cv2.imshow('valjak', field)
		print('select point x={p[1]} mm, y={p[0]} mm'.format(p=points[curpoint]))
		while True:
			if click_yx:
				if zoom:
					zoom = False
					points_selected.append([click_yx[0] // upsample + max(0, y-dh), click_yx[1] // upsample + max(0, x-dw)])
					cv2.circle(field, points_tuple[curpoint], 5, (128,128,128), -1)
					curpoint += 1
					img = cam_img[::downsample,::downsample]
				else:
					zoom = True
					y = click_yx[0] * downsample
					x = click_yx[1] * downsample
					img = scipy.ndimage.zoom(cam_img[max(0, y-dh):min(h, y+dh),max(0, x-dw):min(w, x+dw)], (upsample, upsample, 1))
				click_yx = None
				break
			k = cv2.waitKey(1) & 0xff
			if k == ord('q'):
				exit()
else:#presaved points
	points_selected = [
		[512, 640],
		[934, 643],
		[512, 997],
		[881, 920],
		[512, 1131],
		[798, 1071],
		[657, 640],
		[858, 640],
		[602, 1124],
		[732, 1096],
		[680, 984],
		[778, 962],
		[707, 626],
		[821, 627],
		[512, 667]
	]
		
#fit parameters		
points_selected = np.array(points_selected)
p0 = [h/2, w/2, 5e-1, 1e-9, 1e-25]
popt, pcov = curve_fit(pxToCm, points_selected, points.flatten(), p0=p0)
rps = pxToCm(points_selected, popt[0],popt[1],popt[2],popt[3],popt[4]).reshape(points.shape)
print('Fitting parameters:', popt)
print('Mean error: {merr} mm'.format(merr=np.abs(((rps-points)[:,0]**2+(rps-points)[:,1]**2)**0.5).mean()))
	
#print real and fitted coordinates
print('/----+------------------+-------------------\\')
print('| nr | real coordinates | fitted coordinates|')
print('+----+------------------+-------------------+')
_real = np.around(points).astype(np.int16)
_fitted = np.around(rps).astype(np.int16)
for i in xrange(len(points)):
	print('|{i: >3} |{r[1]: >8},{r[0]: >8} |{f[1]: >8},{f[0]: >8}  |'.format(i=i, r=_real[i], f=_fitted[i]))
print('\\----+------------------+-------------------/')

if 1:
	#show fitted points in the field
	for p in cmToPx(rps):
		cv2.circle(field, (p[1], p[0]), 5, (0,0,255), -1)
	print('press q to exit view')
	while True:
		cv2.imshow('valjak', field)
		k = cv2.waitKey(1) & 0xff
		if k == ord('q'):
			break
cv2.destroyAllWindows()

if 1:
	#show fitted curve (real distance vs pixel distance)
	ys = (points[:,0]**2+points[:,1]**2)**0.5
	xs = ((points_selected[:,0] - popt[0])**2 + (points_selected[:,1] - popt[1])**2)**0.5
	plt.plot(xs, ys, 'x')
	xs2 = np.linspace(0, 600, 100)
	ps = np.repeat(xs2, 2).reshape((-1,2))+popt[0]
	ps[:,1] = popt[1]
	ys2 = pxToCm(ps, popt[0],popt[1],popt[2],popt[3],popt[4])[0::2]
	plt.plot(xs2, ys2, '-')
	plt.xlabel('pixel distance')
	plt.ylabel('real distance')
	plt.show()

#save?
conf = raw_input('Save conf? (y)')
if conf == 'y':
	ys, xs = np.mgrid[:h,:w]
	
	ys = ys - popt[0]
	xs = xs - popt[1]
	fiis = ((np.arctan2(ys, xs)%(2*np.pi))/(2*np.pi)*65535).astype(np.uint16)
	rs = (xs**2 + ys**2)**0.5
	distances = (popt[2]*rs**1 + popt[3]*rs**4 + popt[4]*rs**10).clip(min=0, max=65535).astype(np.uint16)
	
	with open('calibration/locations.pkl', 'wb') as fh:
		pickle.dump((distances, fiis), fh, -1)
	