#!/bin/sh

# This script is meant to be run on the bot.  The upload.sh script in
# this directory will upload us and all of ./sbin to $TARGET_DIR
#
# This setup copied from here: https://www.tomshardware.com/how-to/raspberry-pi-facial-recognition


set -x

TARGET_DIR="/home/pi/shelly-bot"
TMP_DIR="/tmp/shelly-bot"

##
#
# Added the below following the excellent Tom's Hardward
# blog written by Caroline Dunn.  Thank you @carolinedunn!
#
# https://www.tomshardware.com/how-to/raspberry-pi-facial-recognition
##

sudo apt install -y cmake build-essential pkg-config git
sudo apt install -y libjpeg-dev libtiff-dev libjasper-dev libpng-dev libwebp-dev libopenexr-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libdc1394-22-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev
sudo apt install -y libgtk-3-dev libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt install -y libatlas-base-dev liblapacke-dev gfortran
sudo apt install -y libhdf5-dev libhdf5-103
sudo apt install -y python3-dev python3-pip python3-numpy
sudo apt install -y espeak


# needs to temporarily increase the swap file to build / install opencv
mkdir -p $TMP_DIR
sudo cp -f /etc/dphys-swapfile $TMP_DIR
sudo cp -f $TARGET_DIR/sbin/files/dphys-swapfile /etc
sudo systemctl restart dphys-swapfile

cd ~
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
mkdir -p ~/opencv/build
cd ~/opencv/build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
	-D ENABLE_NEON=ON \
	-D ENABLE_VFPV3=ON \
	-D BUILD_TESTS=OFF \
	-D INSTALL_PYTHON_EXAMPLES=OFF \
	-D OPENCV_ENABLE_NONFREE=ON \
	-D CMAKE_SHARED_LINKER_FLAGS=-latomic \
	-D BUILD_EXAMPLES=OFF ..

set +x
echo ""
echo "This will take a while - about 1 hour from $(date)"
set -x
make -j$(nproc)
sudo make install
sudo ldconfig

# restore original swap file settings
sudo cp -f $TMP_DIR/dphys-swapfile /etc
sudo systemctl restart dphys-swapfile

sudo pip3 install face-recognition imutils webrtcvada

##
#
# End of Caroline's setup
#
##


###
#
#  Added for Adeept video streaming; see,
#  base_camera.py, comaner_opencv.py + other code originally
#  "sourced" :) from @adeept/Adeept_RaspTank.
#
#  Thank you @adeept!  ❤️ you!


# I added these to accomodate adeept video streaming
sudo apt-get install -y libjasper-dev
sudo apt-get install -y libatlas-base-dev

# These are for the webserver (flask) and websocket server
sudo pip3 install websockets flask flask_cors
# I'm not sure why Caroline's cv2 setup didn't work for adeept.
# I originally tried to leave this out
sudo pip3 install opencv-contrib-python==3.4.3.18

sudo pip3 install zmq pybase64 psutil


##
# End Adeept setup
##

ssh $TARGET_HOST "mkdir -p $TARGET_DIR/data"
ssh $TARGET_HOST "mkdir -p $TARGET_DIR/data/engagement"
ssh $TARGET_HOST "mkdir -p $TARGET_DIR/data/faces"
