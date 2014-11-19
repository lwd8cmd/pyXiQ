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

logic.start()
motors.start()

if use_UI:
	import _UI
	UI = _UI.UI(logic)
	UI.run()
	
else:
	print('Press Ctrl-c to exit.')
	while True:
		try:
			logic.gate = 0
			logic.set_state(logic.S_WAIT)
			time.sleep(1)
		except KeyboardInterrupt:
			print('Ctrl-c received! Killing threads.')
			motors.run_it	= False
			logic.run_it	= False
			break