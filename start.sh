#!/bin/bash
source ~/anaconda3/envs/py27/bin/activate py27
~/anaconda3/envs/py27/bin/python extreme.py >& extremes.log &
pgrep -f 'extreme' > ./extremes.pid
