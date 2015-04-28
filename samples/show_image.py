import pyXiQ
import cv2

cam = pyXiQ.Camera()
if not cam.opened():
	print("cam not found")
	exit()
cam.setInt("exposure", 10000)
cam.start()

print("Press 'q' to quit")
while True:
	cv2.imshow('tava', cam.image())
	if cv2.waitKey(1) & 0xff == ord('q'):
		break