# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Main module
# NB!!! RUN sudo python run.py

import time
import _motors
import _logic

use_UI	= True

motors = _motors.Motors()
logic = _logic.Logic(motors)

motors.start()
while motors.opened_status == '?':
	time.sleep(0.1)
time.sleep(1)
logic.start()

if use_UI:
	import _UI
	UI = _UI.UI(logic)
	UI.run()
	
else:
	print('Press Ctrl-c to exit.')
	logic.gate = 0
	logic.set_state(logic.S_WAIT)
	while True:
		try:
			time.sleep(1)
		except KeyboardInterrupt:
			print('Ctrl-c received! Killing threads.')
			motors.run_it	= False
			logic.run_it	= False
			break