import time
from multiprocessing import Pool
import numpy as np

def doWork(N):
	for x in xrange(100000):
		N += 1
	return N
	
print('main')

if __name__ == '__main__':
	N	= np.arange(4)
	startTime = time.time()
	pool = Pool(processes=4)
	results = pool.map(doWork, (N[0], N[1], N[2], N[3]))
	print(results)
	N	= np.arange(4) + 1
	results = pool.map(doWork, (N[0], N[1], N[2], N[3]))
	print(results)
	print(time.time() - startTime)