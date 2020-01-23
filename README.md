# extdb

## EXTREMES TOOL ##

This is the repo containing code for ExtDB. The website is served using HTML and Python's tornado server and the database is in Redis.

### Initial installation requirements

+ Install Python3 using the [open source Anaconda distribution of Python:](https://www.anaconda.com/distribution/#download-section)

+ Install [Redis](https://redis.io)

+ Install python library dependencies using: ```pip install -r requirements.txt``` (requirements.txt is in the root directory of the git repo).

### TO UPDATE THE WEBSITE ###

+ ./stop.sh
+ ./start.sh

### TO INITIALIZE AND STORE DATA IN EXTDB ###

+ Run python store.py
+ OR Run as a cron the script: dly_update.cron
