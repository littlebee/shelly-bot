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

mkdir -p $TARGET_DIR/data
mkdir -p $TARGET_DIR/data/names
mkdir -p $TARGET_DIR/data/engagement

sudo apt install -y cmake build-essential pkg-config git
sudo apt install -y python3-dev python3-pip python3-numpy
sudo apt install -y espeak
sudo apt install -y mpg123

# needed for the heart, but it sucks, needs to run sudo
# sudo pip3 install rpi-ws281x

# head tilt and pan
sudo pip3 install adafruit-circuitpython-servokit

# These are for the webserver (flask) and websocket server
sudo pip3 install websockets flask flask_cors
sudo pip3 install pybase64 psutil

# for making http requests to service
sudo pip3 install requests

# start webservice on boot
if [ ! -f /etc/rc.local.preshellybot ]; then
  sudo cp /etc/rc.local /etc/rc.local.preshellybot
fi
sudo cp $TARGET_DIR/sbin/rclocal/engagement.sh /etc/rc.local
sudo chmod +x /etc/rc.local

# configure eth port to static 10.69.0.1
if [ ! -f /etc/dhcpcd.conf.preshellybot ]; then
  sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.preshellybot
fi
sudo cp $TARGET_DIR/sbin/setup/files/engagement/dhcpcd.conf /etc/dhcpcd.conf
sudo service dhcpcd restart

### start of router setup
# the engagment service SBC bridges it's wifi and serves as router
# is also the router for the other machines to reach the public internets
sudo apt install -y dnsmasq
if [ -f /etc/dnsmasq.conf ] && [ ! -f /etc/dnsmasq.conf.preshellybot ]; then
  sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.preshellybot
fi
sudo cp $TARGET_DIR/sbin/setup/files/engagement/dnsmasq.conf /etc/dnsmasq.conf

if [ -f /etc/sysctl.conf ] && [ ! -f /etc/sysctl.conf.preshellybot ]; then
  sudo cp /etc/sysctl.conf /etc/sysctl.conf.preshellybot
fi
sudo cp $TARGET_DIR/sbin/setup/files/engagement/sysctl.conf /etc/sysctl.conf


sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
sudo iptables -A FORWARD -i wlan0 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o wlan0 -j ACCEPT
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

sudo service dnsmasq start
sudo systemctl enable dnsmasq
sudo systemctl enable iptables
### End of router setup
