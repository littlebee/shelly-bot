#!/bin/bash

# This script is meant to be run on the bot.  The upload.sh script in
# this directory will upload us and all of ./sbin to $TARGET_DIR
#

# This setup assumes that a full Raspian distro installed w/Desktop et al


# echo on
set -x

# stop on all errors
set -e

TARGET_DIR="/home/pi/shelly-bot"

# These are for the webserver (flask)
sudo pip3 install websockets flask flask_cors
sudo pip3 install pybase64 psutil

# needed for the LEDs in the heart
sudo pip3 install rpi-ws281x

# Make the webapp automatically start in raspian desktop, full screen
mkdir -p /home/pi/.config/lxsession/LXDE-pi/
cp $TARGET_DIR/sbin/setup/files/heart/lxe-autostart /home/pi/.config/lxsession/LXDE-pi/autostart
chmod +x /home/pi/.config/lxsession/LXDE-pi/autostart

# start both webservers on boot
if [ ! -f /etc/rc.local.preshellybot ]; then
  sudo cp /etc/rc.local /etc/rc.local.preshellybot
fi
sudo cp $TARGET_DIR/sbin/rclocal/heart.sh /etc/rc.local
sudo chmod +x /etc/rc.local

if [ ! -f /etc/dhcpcd.conf.preshellybot ]; then
  sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.preshellybot
fi
sudo cp $TARGET_DIR/sbin/setup/files/heart/dhcpcd.conf /etc/dhcpcd.conf
sudo service dhcpcd restart

