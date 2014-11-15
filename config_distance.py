import cv2
import numpy as np
import cPickle as pickle
from scipy.optimize import curve_fit

cap = cv2.VideoCapture(0)
with open('colors.pkl', 'rb') as fh:
	colors_lookup = pickle.load(fh)
ys	= []
i	= 0
distances	= np.linspace(30, 250, 4)
tmp = 14

print('Press q to QUIT')
print('Press o when ball is ' + str(distances[i] - tmp) + 'cm from the robot')

cv2.namedWindow('frame')
cv2.moveWindow('frame', 400, 0)

while(True):
    # Capture frame-by-frame
	_, yuv = cap.read()
	fragmented	= colors_lookup[yuv[:,:,0] + yuv[:,:,1] * 0x100 + yuv[:,:,2] * 0x10000]
	mask	= (fragmented == 1).view('uint8')
	
	contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	max_area	= 0
	y	= None
	x	= None
	for contour in contours:
		s = cv2.contourArea(contour)
		if s > max_area:
			max_area	= s
			_x, _y, _w, _h = cv2.boundingRect(contour)
			y	= _y + _h / 2
			x	= _x + _w / 2
			
	if y is not None:
		cv2.line(yuv, (0,y),(640,y),(255,255,255),1)
		cv2.line(yuv, (x,0),(x,480),(255,255,255),1)

	cv2.imshow('frame', yuv)
	k = cv2.waitKey(1) & 0xFF

	if k == ord('q'):
		break
	elif k == ord('o') and y is not None:
		print(y)
		ys.append(y)
		i += 1
		if i == len(distances):
			break
		print('Press o when ball is ' + str(distances[i] - tmp) + 'cm from the robot')
		
if len(ys) == len(distances):
	ys	= np.array(ys)
	
	print(ys, distances)
	
	d_angle	= 60 * np.pi / 180 / 640
	h_ball	= 2.15
			
	def calc_distance(y, cam_height, cam_distance, angle):
		return (cam_height - h_ball) * np.tan(angle - d_angle * y) - cam_distance
		
	p	= curve_fit(calc_distance, ys, distances, p0=[15, 8, 1.63])[0]
	
	print('params:', p)
	print('distance, calculated:')
	for i in range(len(distances)):
		print(distances[i], calc_distance(ys[i], p[0], p[1], p[2]))
	
	# When everything done, release the capture
	with open('distances.pkl', 'wb') as fh:
		pickle.dump(p, fh, -1)
cap.release()
cv2.destroyAllWindows()