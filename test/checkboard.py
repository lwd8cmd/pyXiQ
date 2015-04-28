#!/usr/bin/env python

import numpy as np
import cv2
square_size = 50

pattern_size = (8, 8)#(7, 10)
pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)
pattern_points *= square_size

obj_points = []
img_points = []
fn = 'calib5.jpg'
img = cv2.imread(fn, 0)
if img is None:
  print "Failed to load", fn
  exit()

h, w = img.shape[:2]
found, corners = cv2.findChessboardCorners(img, pattern_size)
if True and found:
	term = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1 )
	cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
if True:
	vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
	cv2.drawChessboardCorners(vis, pattern_size, corners, found)
	cv2.imshow('img',vis[::2,::2])
	cv2.waitKey(0)
if not found:
	print 'chessboard not found'
	exit()
img_points.append(corners.reshape(-1, 2))
obj_points.append(pattern_points)

shapey = (w, h)
rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, shapey, None, None)
print(rms)
print(camera_matrix)
print(dist_coefs)

# undistort
shapex = (w,h)
shapez = (w,h)
newcamera, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, shapex, 1, shapez, 10)
#rint(newcamera)

#newimg = cv2.undistort(img, camera_matrix, dist_coefs, None, newcamera)

newshape = (w,h)
mapx,mapy = cv2.initUndistortRectifyMap(camera_matrix,dist_coefs,None,newcamera,newshape,5)

newimg = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)

#x,y,w,h = roi
#newimg = newimg[y:y+h, x:x+w]
div = 4

cv2.imshow('img',newimg[h//2-h//div:h//2+h//div,w//2-w//div:w//2+w//div])
cv2.waitKey(0)

cv2.destroyAllWindows()