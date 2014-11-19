# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Camera settings

import subprocess
print('apply cam settings')
subprocess.check_output('v4l2-ctl -d /dev/video0 -c white_balance_automatic=0,gain_automatic=0,auto_exposure=1,brightness=0,contrast=24,saturation=64,hue=0,red_balance=96,blue_balance=255,gamma=96,exposure=96,gain=16,sharpness=5,vertical_flip=1,horizontal_flip=1', shell=True)

#subprocess.check_output('v4l2-ctl -d /dev/video0 -c white_balance_automatic=0,gain_automatic=0,auto_exposure=1,brightness=0,contrast=24,saturation=64,hue=0,red_balance=128,blue_balance=192,gamma=118,exposure=128,gain=16,sharpness=5,vertical_flip=1,horizontal_flip=1', shell=True)