#!/bin/bash

TARGET_DIR="/home/pi/shelly-bot"
LOGS_DIR=$TARGET_DIR

echo "webapp started from rc.local" >> $LOGS_DIR/heart.log

cd $TARGET_DIR

# start the web server to serve the react app bundle (port 80)
bash run-webapp.sh &

# start the heart web service (port 5000)
sleep 10
bash run-heart.sh


exit 0
