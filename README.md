# extdb

## EXTREMES TOOL ##

This is the repo containing code for ExtDB. The website is served using HTML and Python's tornado server and the database is in Redis.

### Initial installation requirements

+ Install Python3 using the [open source Anaconda distribution of Python:](https://www.anaconda.com/distribution/#download-section)

+ Install [Redis](https://redis.io)

+ Install python library dependencies using: ```pip install -r requirements.txt``` (requirements.txt is in the root directory of the git repo).

### TO UPDATE and VIEW THE ExtDB visualization tool ###

+ ```./stop.sh```
+ ```./start.sh```
+ In browser, go to <http://localhost:8889> to view page. 

### TO INITIALIZE AND STORE DATA IN EXTDB ###

+ Run ```python store.py```
+ OR Run as a cron the script: ```./dly_update.cron```
