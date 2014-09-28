import cv2
import numpy as np

def nothing(x):
	pass

drawing = False # true if mouse is pressed
ix,iy = -1,-1
cap = cv2.VideoCapture(0)
cv2.namedWindow('image')
kernel = np.ones((3,3),np.uint8)
Hmax = 0
Hmin = 255
Smax = 0
Smin = 255
Vmax = 0
Vmin = 255


cv2.createTrackbar('brush_size','image',1,10, nothing)
cv2.createTrackbar('vahe','image',0,50, nothing)
#ei lase varvidel alla 0 ja yle 255 minna
def pixel_min_value(arv1,arv2):
	if arv1-arv2 > 0:
		return arv1-arv2
	else:
		return 0

def pixel_max_value(arv1,arv2):
	if arv1+arv2 <255:
		return arv1+arv2
	else:
		return 255


# mouse callback function
def choose_color(event,x,y,flags,param):
	global ix,iy,drawing, Hmin, Hmax, Smax, Smin, Vmax, Vmin,brush_size

	if event == cv2.EVENT_LBUTTONDOWN:
		drawing = True
		ix,iy = x,y

	elif event == cv2.EVENT_LBUTTONUP:
		drawing = False
		nx = brush_size
		ny = brush_size
		for i in range (0,2*brush_size):
			for p in range(0,2*brush_size):
		#kontrollib, kas on vaja varvi skaalat muuta
					valik = frame[ix-nx+p,iy-ny+i]
					if valik[0] < Hmin:
						Hmin = pixel_min_value(Hmin, valik[0] + vahe)
					elif valik[0] > Hmax:
						Hmax = pixel_max_value(Hmax, valik[0] + vahe)
					if valik[1] < Smin:
						Smin = pixel_min_value(Smin, valik[1] + vahe)
					elif valik[1] > Smax:
						Smax = pixel_max_value(Smax, valik[1] + vahe)
					if valik[2] < Vmin:
						Vmin = pixel_min_value(Vmin, valik[2] + vahe)
					elif valik[2] > Vmax:
						Vmax = pixel_max_value(Vmax, valik[2] + vahe)

		print Hmin, Hmax, Smin, Smax, Vmin, Vmax
cv2.namedWindow('tava')
cv2.setMouseCallback('tava', choose_color)
while(True):
    # Capture frame-by-frame
	ret, frame = cap.read()
	hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) 
	brush_size =cv2.getTrackbarPos('brush_size','image')
	vahe = cv2.getTrackbarPos('brush_size','image')

	lower = np.array([Hmin,Smin,Vmin])
	upper = np.array([Hmax,Smax,Vmax])
    # Display the resulting frame
	mask = cv2.inRange(hsv, lower, upper)
	opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN,kernel)

	cv2.imshow('tava', hsv)
	cv2.imshow('mask', opening)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
# mask=((hsv[:,:,0]<10*(hsv[:,:,1]>128))
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
