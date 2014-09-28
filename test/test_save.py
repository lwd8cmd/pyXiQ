import numpy as np
import cv2
import time
import pickle

cap = cv2.VideoCapture(0)

if not cap.isOpened():
	print('Could not open')
	exit()
	
ret, frame = cap.read()

print(frame.shape)
with open('data.pkl', 'wb') as out:
	pickle.dump(frame, out, -1)

cap.release()