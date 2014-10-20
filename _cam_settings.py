# Mitupead Robotix project 2014
# Lauri Hamarik & Joosep Kivastik
# Camera settings

import subprocess
print('apply cam settings')
subprocess.check_output('v4l2-ctl -d /dev/video0 -c white_balance_automatic=0 -c gain_automatic=0 -c auto_exposure=1', shell=True)