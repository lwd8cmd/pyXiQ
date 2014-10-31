# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# profile
# python -m cProfile -s time profile.py
import _motors
import _logic

motors = _motors.Motors()
logic = _logic.Logic(motors)
logic.run()