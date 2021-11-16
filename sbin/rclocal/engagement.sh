#!/bin/bash

TARGET_DIR="/home/pi/shelly-bot"
LOGS_DIR=$TARGET_DIR

echo "engagement service started from rc.local" >> $LOGS_DIR/engagment.log

cd $TARGET_DIR
bash run-engagement.sh

exit 0
