# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Camera settings

import subprocess
print('apply cam settings')
subprocess.check_output('v4l2-ctl -d /dev/video0 -c white_balance_automatic=0,gain_automatic=0,auto_exposure=1,brightness=0,contrast=24,saturation=64,hue=0,red_balance=96,blue_balance=255,gamma=96,exposure=253,gain=1,sharpness=5', shell=True)
