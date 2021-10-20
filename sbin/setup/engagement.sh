#!/bin/bash

# This script is meant to be run on the bot.  The upload.sh script in
# this directory will upload us and all of ./sbin to $TARGET_DIR
#


# echo on
set -x

# stop on all errors
set -e

TARGET_DIR="/home/pi/shelly-bot"
TMP_DIR="/tmp/shelly-bot"


sudo apt install -y cmake build-essential pkg-config git
sudo apt install -y python3-dev python3-pip python3-numpy
sudo apt install -y espeak

sudo pip3 install rpi-ws281x

# These are for the webserver (flask) and websocket server
sudo pip3 install websockets flask flask_cors
sudo pip3 install opencv-contrib-python  # ==3.4.3.18
sudo pip3 install pybase64 psutil

