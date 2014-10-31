import cv2
import numpy as np
from matplotlib import pyplot as plt
import cPickle as pickle
import time

mask = cv2.imread('mask.png')[:,:,::-1]
lookup	= np.zeros(256*256*256).astype('uint8')
im	= cv2.imread('1/24_64.jpg')
yuv = cv2.cvtColor(im, cv2.COLOR_BGR2YUV)

ob	= yuv[mask[:,:,0]>128].astype('uint32')
noise	= 2
noises	= range(-noise,noise+1)
for x in noises:
	for y in noises:
		for z in noises:
			lookup[((ob[:,0]+x) + (ob[:,1]+y) * 0x100 + (ob[:,2]+z) * 0x10000).clip(0,0xffffff)]	= 1
			
ob	= yuv[mask[:,:,1]>128].astype('uint32')
for x in noises:
	for y in noises:
		for z in noises:
			lookup[((ob[:,0]+x) + (ob[:,1]+y) * 0x100 + (ob[:,2]+z) * 0x10000).clip(0,0xffffff)]	= 2
			
ob	= yuv[mask[:,:,2]>128].astype('uint32')
for x in noises:
	for y in noises:
		for z in noises:
			lookup[((ob[:,0]+x) + (ob[:,1]+y) * 0x100 + (ob[:,2]+z) * 0x10000).clip(0,0xffffff)]	= 3
			
ob	= yuv[(mask[:,:,0]==0)*(mask[:,:,1]==0)*(mask[:,:,2]==0)].astype('uint32')
for x in noises:
	for y in noises:
		for z in noises:
			lookup[((ob[:,0]+x) + (ob[:,1]+y) * 0x100 + (ob[:,2]+z) * 0x10000).clip(0,0xffffff)]	= 0

fragmented	= lookup[yuv[:,:,0] + yuv[:,:,1] * 0x100 + yuv[:,:,2] * 0x10000]
plt.imshow(fragmented, interpolation='None')
plt.show()

with open('colors.pkl', 'wb') as out:
	pickle.dump(lookup, out, -1)

exit()

#mask	= mask / 255
#table	= np.array([[[0,1],[2,3]],[[4,5],[6,7]]]).astype('uint8')
#table	= np.array([0,1,2,3,4,5,6,7]).astype('uint8')
table	= np.zeros(256*256*256).astype('uint8')
prea	= np.array([165,0,254]).astype('uint8')
preb	= np.array([255,255,255]).astype('uint8')

timea	= time.time()
mask	= mask.astype('uint32')
#table	= table.reshape((256,256,256))
#yuv = cv2.cvtColor(mask, cv2.COLOR_BGR2YUV)
for x in xrange(60):
	#tmp	= table[mask[:,:,0],mask[:,:,1],mask[:,:,2]]
	#tmpa	= cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
	#tmpb	= cv2.cvtColor(tmpa, cv2.COLOR_BGR2HSV)
	#tmp	= table[mask.reshape((-1)).view('uint16')]
	#tmp	= mask[:,:,0] + mask[:,:,1] * 256 + mask[:,:,2] * 256 * 256
	#tmp	= table[mask[:,:,0] + (mask[:,:,1] << 8) + (mask[:,:,2] << 16)]
	tmp	= table[mask[:,:,0] + mask[:,:,1] * 0x100 + mask[:,:,2] * 0x10000]
	asda	= tmp==0
	asdb	= tmp==1
	asdc	= tmp==2
	#tmp	= cv2.inRange(mask, prea, preb)
	#tmp	= cv2.inRange(mask, prea, preb)
	#tmp	= cv2.inRange(mask, prea, preb)
print(time.time() - timea)


exit()
print(table[tmp])

exit()
#table	= np.array([])

timea	= time.time()
for x in xrange(1):
	tmp	= cv2.inRange(mask, np.array([165,0,254]), np.array([255,255,255]))
print(time.time() - timea)

exit()


mask = cv2.imread('mask.png')[:,:,::-1]
im	= cv2.imread('1/48_64.jpg')
yuv = cv2.cvtColor(im, cv2.COLOR_BGR2YUV)
pixsa	= yuv[mask[:,:,0]>128]
pixsb	= yuv[mask[:,:,1]>128]
pixsc	= yuv[mask[:,:,2]>128]
if False:
	bitt	= 2
	plt.hist(pixsb[:,bitt], bins=50, color='yellow')
	plt.hist(pixsc[:,bitt], bins=50, color='blue')
	plt.hist(pixsa[:,bitt], bins=50, color='red')
	plt.show()
	
if False:
	step	= 1
	ret	=  []
	for u in range(0,256,step):
		retb	= []
		for v in range(0,256,step):
			#retb.append(np.sum((pixsa[:,1]>=u)*(pixsa[:,1]<u+step)*(pixsa[:,2]>=v)*(pixsa[:,2]<v+step)))
			retb.append(np.sum((pixsb[:,1]==u)*(pixsb[:,2]==v)))
		ret.append(retb)
	plt.imshow(ret, interpolation='None')
	plt.title('yellow gate,contrast=48,saturation=64')
	plt.ylabel('u')
	plt.xlabel('v')
	plt.show()

if False:
	ret	=  []
	for h in range(256):
		retb	= []
		for s in range(256):
			retb.append(np.sum((pixsa[:,0]==h)*(pixsa[:,1]==s)))
		ret.append(retb)
	plt.imshow(ret, interpolation='None')
	plt.title('ball,contrast=48,saturation=64')
	plt.ylabel('h')
	plt.xlabel('s')
	plt.show()
	
if False:
	yuv[:,:,2]	= 0
	tmp	= yuv[mask[:,:,0]>128]
	tmp[:,2]	= 255
	yuv[mask[:,:,0]>128]	= tmp
	maskb	= cv2.inRange(yuv, np.array([165,0,254]), np.array([255,255,255]))
	print(maskb.max())
	plt.imshow(maskb)
	plt.show()

