# extdb

## EXTREMES TOOL ##

This is the repo containing code for ExtDB. The website is served using HTML and Python's tornado server and the database is in Redis.

### TO UPDATE THE WEBSITE ###

+ ./stop.sh
+ ./start.sh

### TO INITIALIZE AND STORE DATA IN EXTDB ###

+ Run python store.py
+ OR Run as a cron the script: dly_update.cron
