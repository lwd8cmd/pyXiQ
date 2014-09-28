import cv2
import numpy as np

def nothing(x):
	pass

drawing = False # true if mouse is pressed
ix,iy = -1,-1
cap = cv2.VideoCapture(0)
cv2.namedWindow('image')
mins = np.array([255,255,255])
maxs = np.array([0,0,0])
#eelnev vaartus
minse = []
maxse = []


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
	global mins, maxs, minse, maxse, jarjekord

	if event == cv2.EVENT_LBUTTONDOWN:
		nx = brush_size
		ny = brush_size
		pixs=hsv[y-ny:y+ny,x-nx:x+nx,:] 
		minse.append(mins)
		maxse.append(maxs)
		mins=np.minimum(mins, pixs.min(0).min(0) - vahe).clip(0, 255).astype('uint8')
		maxs=np.maximum(maxs, pixs.max(0).max(0) + vahe).clip(0, 255).astype('uint8')

#kustutab viimased maxid minid
def eelmised_varvid():
	global maxs, maxse, mins, minse, jarjekord
	try:
		maxs = maxse.pop()
		mins = minse.pop()


cv2.namedWindow('tava')
cv2.setMouseCallback('tava', choose_color)
while(True):
    # Capture frame-by-frame
	ret, frame = cap.read()
	hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) 
	brush_size =cv2.getTrackbarPos('brush_size','image')
	vahe = cv2.getTrackbarPos('brush_size','image')

    # Display the resulting frame
	mask = cv2.inRange(hsv, mins, maxs)

	cv2.imshow('tava', hsv)
	cv2.imshow('mask', mask)
	k = cv2.waitKey(1) & 0xFF
	if k == ord('q'):
		break
	elif k == ord('e'):
		eelmised_varvid()
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
