#!/bin/bash

TARGET_DIR="/home/bee/shelly-bot"
LOGS_DIR=$TARGET_DIR

echo "ai service started from rc.local" >> $LOGS_DIR/ai.log

cd $TARGET_DIR
bash run-ai.sh

exit 0
