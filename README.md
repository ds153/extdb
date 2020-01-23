# extdb

## EXTREMES TOOL ##

This is the repo containing code for ExtDB. The website is served using HTML and Python's tornado server and the database is in Redis.

### Initial installation requirements

+ Install Python3 using the [open source Anaconda distribution of Python:](https://www.anaconda.com/distribution/#download-section)

+ After installation of Anaconda Python, on command line, create a Python2.7 environment. ```conda create -n py27 python=2.7 ```

+ Activate the python2.7 environment using the command: ```source ~/anaconda3/envs/py27/bin/activate py27```

+ Install [Redis](https://redis.io)

+ Install python library dependencies using: ```pip2.7 install -r requirements.txt``` (requirements.txt is in the root directory of the git repo).

### TO UPDATE and VIEW THE ExtDB visualization tool ###

+ ```./stop.sh```
+ ```./start.sh```
+ In browser, go to <http://localhost:8889> to view page. 

### TO INITIALIZE AND STORE DATA IN EXTDB ###

+ Run ```python store.py```
+ OR Run as a cron the script: ```./dly_update.cron```
