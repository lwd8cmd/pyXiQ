import numpy as np
import cv2
import time
import pickle
import matplotlib.pyplot as plt

with open('data.pkl', 'rb') as inf:
	frame = pickle.load(inf)
	
#frame	= frame[:120,:].reshape((240,320,3))

#frame	= frame[:120,:320]
#print(frame[0:3,0:3])
frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR)

print([[frame[:,:,x].min(), frame[:,:,x].max()] for x in range(3)])

plt.imshow(frame)
plt.show()
exit()