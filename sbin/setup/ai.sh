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
sudo apt install -y libjpeg-dev libtiff-dev libpng-dev libwebp-dev libopenexr-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libdc1394-22-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev
sudo apt install -y libgtk-3-dev libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt install -y libatlas-base-dev liblapack-dev gfortran
sudo apt install -y libhdf5-dev
sudo apt install -y python3-dev python3-pip python3-numpy


# if jetson nano (ubuntu)
if [ "$(uname -p)" == "aarch64" ]; then
  # see also, https://automaticaddison.com/how-to-install-opencv-4-5-on-nvidia-jetson-nano/
  sudo sh -c "echo '/usr/local/cuda/lib64' >> /etc/ld.so.conf.d/nvidia-tegra.conf"
  sudo ldconfig
  sudo apt-get install -y unzip
  sudo apt-get install -y libgtk2.0-dev libcanberra-gtk*
  sudo apt-get install -y libtbb2 libtbb-dev
  sudo apt-get install -y v4l-utils
  sudo apt-get install -y libavresample-dev libvorbis-dev libxine2-dev
  sudo apt-get install -y libfaac-dev libmp3lame-dev libtheora-dev
  sudo apt-get install -y libopencore-amrnb-dev libopencore-amrwb-dev
  sudo apt-get install -y libopenblas-dev libblas-dev
  sudo apt-get install -y protobuf-compiler
  sudo apt-get install -y libprotobuf-dev libgoogle-glog-dev libgflags-dev

  if [ -f "/swapfile" ]; then
    sudo swapoff /swapfile
    sudo rm  /swapfile
  fi

  # set up swap file on Jetson (ubuntu)
  sudo fallocate -l 4G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile

  cd ~
  if [ ! -d "./opencv" ]; then
    wget -O opencv.zip https://github.com/opencv/opencv/archive/4.5.1.zip
    wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.5.1.zip
    unzip opencv.zip
    unzip opencv_contrib.zip

    mv opencv-4.5.1 opencv
    mv opencv_contrib-4.5.1 opencv_contrib
    rm opencv.zip
    rm opencv_contrib.zip
  fi

  cd ~/opencv
  mkdir -p build
  cd build

  cmake -D CMAKE_BUILD_TYPE=RELEASE \
  -D CMAKE_INSTALL_PREFIX=/usr \
  -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
  -D EIGEN_INCLUDE_PATH=/usr/include/eigen3 \
  -D WITH_OPENCL=OFF \
  -D WITH_CUDA=ON \
  -D CUDA_ARCH_BIN=5.3 \
  -D CUDA_ARCH_PTX="" \
  -D WITH_CUDNN=ON \
  -D WITH_CUBLAS=ON \
  -D ENABLE_FAST_MATH=ON \
  -D CUDA_FAST_MATH=ON \
  -D OPENCV_DNN_CUDA=ON \
  -D ENABLE_NEON=ON \
  -D WITH_QT=OFF \
  -D WITH_OPENMP=ON \
  -D WITH_OPENGL=ON \
  -D BUILD_TIFF=ON \
  -D WITH_FFMPEG=ON \
  -D WITH_GSTREAMER=ON \
  -D WITH_TBB=ON \
  -D BUILD_TBB=ON \
  -D BUILD_TESTS=OFF \
  -D WITH_EIGEN=ON \
  -D WITH_V4L=ON \
  -D WITH_LIBV4L=ON \
  -D OPENCV_ENABLE_NONFREE=ON \
  -D INSTALL_C_EXAMPLES=OFF \
  -D INSTALL_PYTHON_EXAMPLES=OFF \
  -D BUILD_NEW_PYTHON_SUPPORT=ON \
  -D BUILD_opencv_python3=TRUE \
  -D OPENCV_GENERATE_PKGCONFIG=ON \
  -D BUILD_EXAMPLES=OFF ..

# Raspberry pi
else
  sudo apt install -y libjasper-dev

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

fi

set +x
echo ""
echo "This will take a while - about 1 hour from $(date)"
set -x
make -j4
sudo make install
sudo ldconfig


# jetson nano
if [ "$(uname -p)" == "aarch64" ]; then
  # This could take a while to compile (like 15min)
  sudo pip3 install numpy

  # Install DLIB for the jetson
  cd ~
  wget http://dlib.net/files/dlib-19.22.tar.bz2
  tar jxf dlib-19.22.tar.bz2
  cd dlib-19.22
  # sed -i 's/forward_algo = forward_best_algo/\/\/ forward_algo = forward_best_algo/g' dlib/cuda/cudnn_dlibapi.cpp
  # This could take 30 - 60 mins to complete
  sudo python3 setup.py install

  # provides jtop command for debugging
  sudo -H pip install -U jetson-stats
  sudo systemctl restart jetson_stats.service


# raspberry pi
else
  # restore original swap file settings
  sudo cp -f $TMP_DIR/dphys-swapfile /etc
  sudo systemctl restart dphys-swapfile

  sudo pip3 install webrtcvada zmq
fi

sudo pip3 install face-recognition imutils

# These are for the webserver (flask) and websocket server
sudo pip3 install websockets flask flask_cors
sudo pip3 install opencv-contrib-python
sudo pip3 install pybase64 psutil


mkdir -p $TARGET_DIR/data
mkdir -p $TARGET_DIR/data/engagement
mkdir -p $TARGET_DIR/data/faces
