import numpy as np
import cv2
import time
import pickle
import matplotlib.pyplot as plt

with open('../colors.pkl', 'rb') as fh:
	colors = pickle.load(fh).reshape((256,256,256))
	
for i in range(256):
	print(i)
	plt.imshow(colors[i,:,:], interpolation='None')
	plt.show()